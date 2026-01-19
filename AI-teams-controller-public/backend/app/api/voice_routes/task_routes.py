# -*- coding: utf-8 -*-
"""Voice task completion and feedback routes.

Contains endpoints for:
- POST /task-done/{team_id}/{role_id} - Handle Claude Stop hook for voice feedback
- WS /ws/feedback/{team_id}/{role_id} - Team-specific voice feedback WebSocket
- WS /ws/feedback/global - Global voice feedback WebSocket
"""

import logging
import uuid

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from app.models.voice_schemas import TaskDoneRequest, TaskDoneResponse
from app.services.skip_logic import should_skip_role
from app.services.task_done_listener import get_task_done_listener

logger = logging.getLogger(__name__)

router = APIRouter()


# Import helper function from command_routes for pane content capture
def get_tmux_pane_content(team_id: str, role_id: str, lines: int = 50) -> str:
    """Get content from a tmux pane (imported from command_routes)."""
    from app.api.voice_routes.command_routes import get_tmux_pane_content as _get_content
    return _get_content(team_id, role_id, lines)


# ============================================================
# Task Done Endpoint (Stop Hook Integration)
# ============================================================


@router.post("/task-done/{team_id}/{role_id}", response_model=TaskDoneResponse)
async def handle_task_done(
    team_id: str,
    role_id: str,
    request: TaskDoneRequest,
):
    """Handle Claude Code Stop hook for voice feedback.

    Called by Stop hook when Claude finishes responding.
    Generates summary + TTS and broadcasts to frontend.

    Skip logic runs HERE (FastAPI layer) where tmux is accessible,
    NOT in Celery worker. Uses fail-closed pattern.

    Args:
        team_id: tmux session name
        role_id: pane index
        request: Contains session_id, transcript_path

    Returns:
        TaskDoneResponse with summary
    """
    request_id = str(uuid.uuid4())[:8]  # Short unique ID for tracing
    logger.info(f"[VOICE:{request_id}] Task-done ENTRY: {team_id}/{role_id} role_name={request.role_name}")

    # If legacy clients send team_id/role_id in body, validate they match path
    if request.team_id and request.team_id != team_id:
        raise HTTPException(
            status_code=400,
            detail="team_id in body does not match path parameter",
        )
    if request.role_id and request.role_id != role_id:
        raise HTTPException(
            status_code=400,
            detail="role_id in body does not match path parameter",
        )

    # SKIP CHECK: Run in FastAPI layer where tmux is accessible (Story 2)
    # Uses fail-closed pattern: unknown roles are skipped for safety
    # Prefer role_name from hook (stable) over querying tmux (pane_title gets overwritten)
    if should_skip_role(team_id, role_id, role_name=request.role_name):
        logger.info(f"[VOICE:{request_id}] SKIPPED by skip_logic: role={request.role_name}")
        return TaskDoneResponse(
            success=True,
            summary=None,
            command_id=None,
        )
    logger.info(f"[VOICE:{request_id}] PASSED skip_logic: role={request.role_name}")

    # EAGER TTS PROVIDER VALIDATION (AC5): Check provider config BEFORE queueing task
    # This prevents queueing tasks that will fail due to unknown/misconfigured provider
    try:
        from app.services.tts_providers import TTSProviderFactory
        TTSProviderFactory.validate_provider()
        logger.info(f"[VOICE:{request_id}] TTS provider validation PASSED")
    except ValueError as e:
        logger.error(f"[VOICE:{request_id}] TTS provider validation FAILED: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"TTS provider configuration error: {str(e)}"
        )

    try:
        # Get pane output for context (200 lines to handle narrow pane wrapping)
        pane_output = get_tmux_pane_content(team_id, role_id, lines=200)
        logger.info(f"[VOICE:{request_id}] Captured pane output: {len(pane_output)} chars")

        # Process via TaskDoneListener (skip check already done above)
        listener = get_task_done_listener()
        result = await listener.stop_hook_fired(
            team_id=team_id,
            role_id=role_id,
            pane_output=pane_output,
            request_id=request_id,  # Pass for tracing
        )

        # Log the result for debugging
        if result.get("skipped"):
            logger.info(f"[VOICE:{request_id}] SKIPPED by listener: reason={result.get('reason')}")
        elif result.get("success"):
            logger.info(f"[VOICE:{request_id}] QUEUED to Celery: task_id={result.get('task_id')}")
        else:
            logger.warning(f"[VOICE:{request_id}] FAILED: error={result.get('error')}")

        # result is never None in v2 (stateless architecture)
        if not result.get("success"):
            return TaskDoneResponse(
                success=False,
                error=result.get("error", "Unknown error"),
            )

        return TaskDoneResponse(
            success=True,
            summary=result.get("summary"),
            command_id=result.get("command_id"),
        )

    except Exception as e:
        logger.error(f"[VOICE:{request_id}] Task done EXCEPTION: {e}")
        return TaskDoneResponse(
            success=False,
            error=str(e)[:200],
        )


# ============================================================
# WebSocket for Voice Feedback
# ============================================================


@router.websocket("/ws/feedback/{team_id}/{role_id}")
async def voice_feedback_websocket(
    websocket: WebSocket,
    team_id: str,
    role_id: str,
):
    """WebSocket for receiving voice feedback (TTS audio).

    DEPRECATED: Use /ws/feedback/global instead for team-independent feedback.

    Frontend connects here to receive voice_feedback messages
    with summary text and base64-encoded audio.
    """
    await websocket.accept()
    logger.info(f"[VOICE] Feedback WebSocket connected: {team_id}/{role_id}")

    # Register WebSocket with TaskDoneListener (uses global manager internally)
    listener = get_task_done_listener()
    listener.register_websocket(team_id, role_id, websocket)

    try:
        # Keep connection alive until client disconnects
        while True:
            # Wait for any message (keepalive or close)
            try:
                message = await websocket.receive_text()
                # Echo back for keepalive
                if message == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    finally:
        listener.unregister_websocket(team_id, role_id)
        logger.info(f"[VOICE] Feedback WebSocket disconnected: {team_id}/{role_id}")


@router.websocket("/ws/feedback/global")
async def global_voice_feedback_websocket(websocket: WebSocket):
    """Global WebSocket for receiving voice feedback from ALL teams.

    This endpoint receives voice feedback from any team/pane completion.
    Messages include team_id and role_id so frontend can filter if needed.

    Message format:
    {
        "type": "voice_feedback",
        "team_id": "my-team",
        "role_id": "pane-0",
        "summary": "Done. Fixed the bug.",
        "audio": "<base64 MP3>"
    }
    """
    await websocket.accept()
    logger.info("[VOICE] Global feedback WebSocket connected")

    listener = get_task_done_listener()
    await listener.ws_manager.register(websocket)

    try:
        while True:
            try:
                message = await websocket.receive_text()
                if message == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    finally:
        await listener.ws_manager.unregister(websocket)
        logger.info("[VOICE] Global feedback WebSocket disconnected")
