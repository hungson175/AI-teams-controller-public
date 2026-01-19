"""API routes for TMUX Team Controller."""

import asyncio
import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

from app.api.auth_routes import get_current_user_from_token
from app.models.auth_schemas import UserResponse
from app.models.schemas import (
    TeamsResponse,
    RolesResponse,
    SendMessageRequest,
    SendMessageResponse,
    PaneStateResponse,
    TeamActionResponse,
    CreateTerminalRequest,
    CreateTerminalResponse,
    ListAvailableTeamsResponse,
)
from app.services.base import TeamService
from app.services.factory import get_team_service

router = APIRouter()


@router.get("/teams", response_model=TeamsResponse)
async def get_teams(
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TeamService = Depends(get_team_service),
):
    """List all tmux sessions (teams). Requires JWT auth."""
    teams = service.get_teams()
    return {"teams": teams}


@router.get("/teams/available", response_model=ListAvailableTeamsResponse)
async def list_available_teams(
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TeamService = Depends(get_team_service),
):
    """List available team directories that can be loaded. Requires JWT auth.

    Scans docs/tmux/ for team directories with setup-team.sh scripts.
    Returns whether each team is currently active.
    """
    teams = service.list_available_teams()
    return {"teams": teams}


@router.get("/teams/{team_id}/roles", response_model=RolesResponse)
async def get_roles(
    team_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TeamService = Depends(get_team_service),
):
    """List all tmux panes (roles) for a team. Requires JWT auth."""
    roles = service.get_roles(team_id)
    return {"teamId": team_id, "roles": roles}


@router.post("/send/{team_id}/{role_id}", response_model=SendMessageResponse)
async def send_message(
    team_id: str,
    role_id: str,
    request: SendMessageRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TeamService = Depends(get_team_service),
):
    """Send a message to a specific pane. Requires JWT auth."""
    result = service.send_message(team_id, role_id, request.message)
    return result


@router.get("/state/{team_id}/{role_id}", response_model=PaneStateResponse)
async def get_pane_state(
    team_id: str,
    role_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TeamService = Depends(get_team_service),
):
    """Get the current state/output of a pane. Requires JWT auth."""
    state = service.get_pane_state(team_id, role_id)
    return state


# ========== Commander Epic: Team Lifecycle Management ==========


@router.post("/teams/{team_id}/kill", response_model=TeamActionResponse)
async def kill_team(
    team_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TeamService = Depends(get_team_service),
):
    """Kill a tmux session. Requires JWT auth.

    Terminates all agents running in the specified team.
    """
    result = service.kill_team(team_id)
    return result


@router.post("/teams/{team_id}/restart", response_model=TeamActionResponse)
async def restart_team(
    team_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TeamService = Depends(get_team_service),
):
    """Restart a tmux session. Requires JWT auth.

    Kills the session and runs the setup script from README if available.
    Returns setupScriptRun=true if a setup script was found and executed.
    """
    result = service.restart_team(team_id)
    return result


@router.post("/teams/{team_id}/roles/{role}/restart")
async def restart_role(
    team_id: str,
    role: str,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TeamService = Depends(get_team_service),
):
    """Restart a specific role within a team. Requires JWT auth.

    Finds pane by @role_name, sends Ctrl+C, re-runs claude command, sends /init-role.
    Returns pane_id and status.
    """
    result = service.restart_role(team_id, role)
    return result


@router.post("/teams/create-terminal", response_model=CreateTerminalResponse)
async def create_terminal(
    request: CreateTerminalRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    service: TeamService = Depends(get_team_service),
):
    """Create a new tmux session (terminal). Requires JWT auth.

    Creates a new detached tmux session in the specified directory.
    If name is not provided, auto-generates one like 'terminal-HHMMSS'.
    If directory is not provided, defaults to home directory.
    """
    result = service.create_terminal(request.name, request.directory)
    return result


@router.websocket("/ws/state/{team_id}/{role_id}")
async def websocket_pane_state(websocket: WebSocket, team_id: str, role_id: str):
    """WebSocket endpoint for real-time pane state streaming.

    Client can send JSON messages to configure:
    - {"interval": 5} - Set polling interval (1, 2, or 5 seconds)
    - {"captureLines": 100} - Set number of lines to capture (50-500)
    - {"pause": true} - Pause streaming
    - {"pause": false} - Resume streaming
    - "ping" - Keepalive ping, server responds with "pong"

    Server sends pane state updates only when content changes.
    Includes isActive field for activity detection (Sprint 29).
    Server sends keepalive ping every 30 seconds to prevent connection timeout.
    """
    await websocket.accept()

    service = get_team_service()
    interval = 5  # Default polling interval (5s for activity detection)
    capture_lines = 100  # Default capture lines
    paused = False
    last_output = None
    last_keepalive = asyncio.get_event_loop().time()
    keepalive_interval = 30  # Send keepalive every 30 seconds

    try:
        while True:
            try:
                # Check for client messages (non-blocking)
                try:
                    # Use wait_for with 0 timeout to check without blocking
                    message = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=0.01
                    )
                    # Handle plain text "ping" keepalive
                    if message == "ping":
                        await websocket.send_text("pong")
                        continue
                    try:
                        data = json.loads(message)
                        if "interval" in data:
                            new_interval = float(data["interval"])
                            # Accept sub-second intervals (0.5s)
                            if new_interval in [0.5, 1, 2, 5]:
                                interval = new_interval
                        if "captureLines" in data:
                            new_lines = int(data["captureLines"])
                            if 50 <= new_lines <= 500:
                                capture_lines = new_lines
                                service.set_capture_lines(capture_lines)
                        if "pause" in data:
                            paused = bool(data["pause"])
                    except json.JSONDecodeError:
                        pass
                except asyncio.TimeoutError:
                    pass  # No message, continue

                current_time = asyncio.get_event_loop().time()

                if not paused:
                    # Get current pane state
                    state = service.get_pane_state(team_id, role_id)

                    # Send if output changed OR keepalive interval elapsed
                    if state["output"] != last_output:
                        last_output = state["output"]
                        await websocket.send_json(state)
                        last_keepalive = current_time
                    elif current_time - last_keepalive >= keepalive_interval:
                        # Send keepalive ping to prevent connection timeout
                        await websocket.send_json({"type": "keepalive", "timestamp": current_time})
                        last_keepalive = current_time

                await asyncio.sleep(interval)

            except WebSocketDisconnect:
                # Re-raise to be handled by outer exception handler
                raise
            except Exception as e:
                # P0 Fix: Catch exceptions from get_pane_state() or send_json()
                logger.error(f"[WS] Error in websocket loop for {team_id}/{role_id}: {e}")
                try:
                    # Try to send error notification to client
                    await websocket.send_json({
                        "error": str(e),
                        "output": f"Error: {e}",
                        "lastUpdated": asyncio.get_event_loop().time(),
                        "highlightText": None,
                        "isActive": False,
                    })
                except Exception:
                    # If sending error fails, connection is likely broken
                    logger.error(f"[WS] Failed to send error notification, closing connection")
                    break

    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected: {team_id}/{role_id}")
    except Exception as e:
        logger.error(f"[WS] Unexpected error in websocket handler: {e}")
    finally:
        logger.debug(f"[WS] Cleaning up websocket connection: {team_id}/{role_id}")
