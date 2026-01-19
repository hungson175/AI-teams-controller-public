# -*- coding: utf-8 -*-
"""Voice command processing routes.

Contains endpoints for:
- POST /command/{team_id}/{role_id} - Process voice command with LLM correction
- POST /transcribe - Audio transcription via Soniox
- Helper functions: get_pane_id, get_tmux_pane_content, send_to_tmux_pane, correct_voice_command
"""

import logging
import os
import subprocess
from typing import Optional

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.voice_schemas import (
    TranscriptionResponse,
    VoiceCommandRequest,
    VoiceCommandResponse,
)
from app.services.prompts import VOICE_2_COMMAND_SYSTEM_PROMPT
from app.services.task_done_listener import get_task_done_listener

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# Helper Functions
# ============================================================


def get_pane_id(team_id: str, role_id: str) -> Optional[str]:
    """Look up actual tmux pane_id from role_id.

    Args:
        team_id: tmux session name
        role_id: API role ID like "pane-0", "pane-1"

    Returns:
        pane_id like %17, %18 or None if not found
    """
    from app.services.tmux_service import TmuxService
    service = TmuxService()
    return service._get_pane_target(team_id, role_id)


def get_tmux_pane_content(team_id: str, role_id: str, lines: int = 50) -> str:
    """Get content from a tmux pane for LLM context.

    CRITICAL FIX: Forces pane to bottom before capture to prevent reading
    ancient scrollback when pane is scrolled up.

    Args:
        team_id: tmux session name
        role_id: API role ID like "pane-0", "pane-1"
        lines: number of lines to capture

    Returns:
        Pane content as string
    """
    # Look up actual pane_id from role_id
    target = get_pane_id(team_id, role_id)
    if not target:
        return f"[Pane not found: {role_id}]"
    try:
        # CRITICAL FIX: Force pane to bottom (latest content) before capture
        # This ensures we capture CURRENT output, not ancient scrollback
        subprocess.run(
            ["tmux", "copy-mode", "-q", "-t", target],
            capture_output=True,
            timeout=2,
        )  # Exit copy mode if active

        # Now capture from the bottom (most recent content)
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", target, "-p", "-J", "-S", f"-{lines}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return f"[Error capturing pane: {result.stderr}]"
    except FileNotFoundError:
        return "[tmux not found]"
    except subprocess.TimeoutExpired:
        return "[tmux command timed out]"
    except Exception as e:
        return f"[Error: {e}]"


def send_to_tmux_pane(team_id: str, role_id: str, command: str) -> bool:
    """Send command to tmux pane.

    Uses two-enter rule for Claude CLI compatibility.
    IMPORTANT: Two Enters must be SEPARATE tmux commands with delay!

    Args:
        team_id: tmux session name
        role_id: API role ID like "pane-0", "pane-1"

    Returns:
        True if successful
    """
    import time

    # Look up actual pane_id from role_id
    target = get_pane_id(team_id, role_id)
    if not target:
        logger.error(f"[VOICE] Pane not found: {role_id}")
        return False

    try:
        # First send-keys with the command + Enter
        result1 = subprocess.run(
            ["tmux", "send-keys", "-t", target, command, "C-m"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result1.returncode != 0:
            logger.error(f"[VOICE] Failed first send-keys to {target}")
            return False

        # CRITICAL: Wait 0.3s before second Enter (timing issue!)
        time.sleep(0.3)

        # Second Enter - SEPARATE command (two-enter rule for Claude CLI)
        result2 = subprocess.run(
            ["tmux", "send-keys", "-t", target, "C-m"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        success = result2.returncode == 0
        if success:
            logger.info(f"[VOICE] Command sent to {target}: {command[:50]}...")
        else:
            logger.error(f"[VOICE] Failed second Enter to {target}")
        return success

    except Exception as e:
        logger.error(f"[VOICE] Error sending to tmux: {e}")
        return False


def get_bl_pane_id(team_id: str) -> Optional[str]:
    """Get the BL (Backlog Organizer) pane ID for a team.

    Looks up pane with @role_name = "BL" in the team's tmux session.

    Args:
        team_id: tmux session name

    Returns:
        role_id like "pane-6" or None if BL pane not found
    """
    from app.services.tmux_service import tmux_service

    roles = tmux_service.get_roles(team_id)
    for role in roles:
        if role.get("name") == "BL":
            return role.get("id")

    logger.warning(f"[VOICE] BL pane not found in team {team_id}")
    return None


class RoutedCommand:
    """Result of voice command correction with routing decision.

    Attributes:
        corrected_command: The cleaned/corrected command in English
        is_backlog_task: True if command should be routed to BL pane
    """

    def __init__(self, corrected_command: str, is_backlog_task: bool = False):
        self.corrected_command = corrected_command
        self.is_backlog_task = is_backlog_task


def correct_voice_command(voice_transcript: str, tmux_context: str) -> RoutedCommand:
    """Use LLM to correct pronunciation errors and determine routing.

    Args:
        voice_transcript: Raw transcript from voice input (may have errors)
        tmux_context: Current tmux pane content for context

    Returns:
        RoutedCommand with corrected_command and is_backlog_task
    """
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import HumanMessage, SystemMessage
    from pydantic import BaseModel, Field

    class RoutedCommandSchema(BaseModel):
        """Structured output for voice command correction with routing decision."""

        corrected_command: str = Field(
            description="The cleaned/corrected command in English only"
        )
        is_backlog_task: bool = Field(
            description=(
                "True ONLY if this is a WRITE operation on backlog: "
                "CREATE (add new item), UPDATE (change priority/description), or DELETE (remove item). "
                "False for READ operations (check backlog, list tasks, query status) "
                "or any non-backlog task."
            )
        )

    # Use grok-4-fast for speed (requires XAI_API_KEY)
    xai_key = os.environ.get("XAI_API_KEY")
    if not xai_key:
        logger.warning("[VOICE] XAI_API_KEY not set, returning original transcript")
        return RoutedCommand(corrected_command=voice_transcript, is_backlog_task=False)

    llm = init_chat_model(
        "grok-4-fast-non-reasoning",
        model_provider="xai",
        temperature=0.1,
    )
    structured_llm = llm.with_structured_output(RoutedCommandSchema)

    # Build user message with context
    user_content = f"""## Tmux Pane Context (last 50 lines):
```
{tmux_context[-2000:] if len(tmux_context) > 2000 else tmux_context}
```

## Voice Transcript (may have pronunciation errors):
"{voice_transcript}"
"""

    messages = [
        SystemMessage(content=VOICE_2_COMMAND_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = structured_llm.invoke(messages)
    return RoutedCommand(
        corrected_command=response.corrected_command,
        is_backlog_task=response.is_backlog_task,
    )


# ============================================================
# Voice Command Processing
# ============================================================


@router.post("/command/{team_id}/{role_id}", response_model=VoiceCommandResponse)
async def process_voice_command(
    team_id: str,
    role_id: str,
    request: VoiceCommandRequest,
):
    """Process voice command: correct with LLM and send to tmux.

    Called by frontend after detecting stop word ("go go").

    Args:
        team_id: tmux session name
        role_id: pane index
        request: Contains raw_command and transcript

    Returns:
        VoiceCommandResponse with corrected command
    """
    logger.info(
        f"[VOICE] Processing command for {team_id}/{role_id}: "
        f"'{request.transcript[:50]}...'"
    )

    try:
        # Get tmux pane context for LLM
        tmux_context = get_tmux_pane_content(team_id, role_id)

        # Correct command with LLM and get routing decision
        result = correct_voice_command(request.transcript, tmux_context)
        logger.info(
            f"[VOICE] Corrected: '{result.corrected_command[:50]}...' "
            f"(is_backlog_task={result.is_backlog_task})"
        )

        # Route to BL pane if this is a backlog WRITE task, otherwise use selected pane
        if result.is_backlog_task:
            bl_pane_id = get_bl_pane_id(team_id)
            if bl_pane_id:
                target_role_id = bl_pane_id
                logger.info(f"[VOICE] Routing to BL pane: {bl_pane_id}")
            else:
                # BL pane not found, fall back to selected pane
                logger.warning(f"[VOICE] BL pane not found in {team_id}, using selected pane")
                target_role_id = role_id
        else:
            target_role_id = role_id

        # Send to tmux pane
        success = send_to_tmux_pane(team_id, target_role_id, result.corrected_command)

        if not success:
            return VoiceCommandResponse(
                success=False,
                corrected_command=result.corrected_command,
                error="Failed to send command to tmux pane",
            )

        # Store pending command for Stop hook correlation (Sprint 4)
        listener = get_task_done_listener()
        listener.command_sent(
            team_id=team_id,
            role_id=target_role_id,
            raw_command=request.raw_command,
            corrected_command=result.corrected_command,
            speed=request.speed,  # Pass speed from request
        )

        return VoiceCommandResponse(
            success=True,
            corrected_command=result.corrected_command,
        )

    except Exception as e:
        logger.error(f"[VOICE] Command processing error: {e}")
        return VoiceCommandResponse(
            success=False,
            error=str(e)[:200],
        )


# ============================================================
# Audio Transcription Endpoint
# ============================================================


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio file using Soniox API.

    Accepts multipart/form-data with audio file and returns transcription.

    Args:
        audio: Audio file (multipart/form-data)

    Returns:
        TranscriptionResponse with transcription text and success status
    """
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        logger.error("[VOICE] SONIOX_API_KEY not configured for transcription")
        raise HTTPException(
            status_code=500,
            detail="SONIOX_API_KEY not configured",
        )

    if not audio.filename:
        logger.error("[VOICE] Audio file missing filename")
        raise HTTPException(
            status_code=400,
            detail="Audio file must have a filename",
        )

    # Read audio file content early (outside try block for validation errors)
    try:
        audio_content = await audio.read()
    except Exception as e:
        logger.error(f"[VOICE] Failed to read audio file: {e}")
        raise HTTPException(
            status_code=400,
            detail="Failed to read audio file",
        )

    if not audio_content:
        logger.error("[VOICE] Audio file is empty")
        raise HTTPException(
            status_code=400,
            detail="Audio file is empty",
        )

    logger.info(
        f"[VOICE] Transcribing audio: {audio.filename} "
        f"({len(audio_content)} bytes)"
    )

    try:
        # Call Soniox API for transcription
        async with httpx.AsyncClient() as client:
            files = {"audio": (audio.filename, audio_content, audio.content_type)}
            headers = {
                "Authorization": f"Bearer {api_key}",
            }

            response = await client.post(
                "https://api.soniox.com/v1/transcribe",
                files=files,
                headers=headers,
                timeout=30.0,
            )

            if response.status_code != 200:
                logger.error(
                    f"[VOICE] Soniox transcription failed: {response.status_code} "
                    f"{response.text[:200]}"
                )
                return TranscriptionResponse(
                    transcription="",
                    success=False,
                    error=f"Soniox API error: {response.status_code}",
                )

            # Parse response
            data = response.json()
            transcription = data.get("transcript", "").strip()

            if not transcription:
                logger.warning("[VOICE] Soniox returned empty transcription")
                return TranscriptionResponse(
                    transcription="",
                    success=False,
                    error="No speech detected in audio",
                )

            logger.info(f"[VOICE] Transcription successful: {transcription[:50]}...")
            return TranscriptionResponse(
                transcription=transcription,
                success=True,
            )

    except httpx.TimeoutException:
        logger.error("[VOICE] Soniox transcription timeout")
        return TranscriptionResponse(
            transcription="",
            success=False,
            error="Soniox API timeout",
        )
    except httpx.RequestError as e:
        logger.error(f"[VOICE] Soniox request error: {e}")
        return TranscriptionResponse(
            transcription="",
            success=False,
            error=f"Request error: {str(e)[:100]}",
        )
    except Exception as e:
        logger.error(f"[VOICE] Transcription processing error: {e}")
        return TranscriptionResponse(
            transcription="",
            success=False,
            error=str(e)[:200],
        )
