# -*- coding: utf-8 -*-
"""Pydantic schemas for voice command integration.

Architecture: Frontend Direct with Soniox STT
- Frontend connects directly to Soniox API for speech-to-text
- Backend provides Soniox API key and command processing
"""

from typing import Literal, Optional

from pydantic import BaseModel


# ============================================================
# Soniox Token API
# ============================================================


class SonioxTokenResponse(BaseModel):
    """Response from POST /api/voice/token/soniox."""

    api_key: str


# ============================================================
# Voice Command API (Frontend -> Backend after stop word)
# ============================================================


class VoiceCommandRequest(BaseModel):
    """Request to process voice command.

    Sent by frontend after detecting stop word.
    """

    raw_command: str  # Full transcript including stop word
    transcript: str  # Command text (stop word removed by frontend)
    speed: Optional[float] = 0.8  # TTS speech speed (0.5-2.0, default 0.8)


class VoiceCommandResponse(BaseModel):
    """Response from voice command processing."""

    success: bool
    corrected_command: Optional[str] = None
    error: Optional[str] = None


# ============================================================
# Streaming Response Messages (for SSE)
# ============================================================


class LLMTokenMessage(BaseModel):
    """Streaming token from LLM correction."""

    type: Literal["llm_token"]
    token: str


class CommandSentMessage(BaseModel):
    """Corrected command sent to tmux pane."""

    type: Literal["command_sent"]
    corrected_command: str


# ============================================================
# Voice Feedback (Backend -> Frontend via WebSocket, Sprint 3)
# ============================================================


class VoiceFeedbackMessage(BaseModel):
    """Voice feedback with TTS audio."""

    type: Literal["voice_feedback"]
    summary: str
    audio: str  # base64 encoded MP3


class VoiceErrorMessage(BaseModel):
    """Error message."""

    type: Literal["error"]
    message: str


# ============================================================
# Task Done API (Claude Code Stop Hook, Sprint 3)
# ============================================================


class TaskDoneRequest(BaseModel):
    """Request from Claude Code Stop hook."""

    session_id: str
    transcript_path: str
    # team_id/role_id are path params; keep optional in body for backward compatibility
    team_id: str | None = None
    role_id: str | None = None
    # role_name from @role_name tmux option (stable, set by setup-team.sh)
    # This is more reliable than pane_title which Claude Code overwrites
    role_name: str | None = None


class TaskDoneResponse(BaseModel):
    """Response to Stop hook."""

    success: bool
    summary: Optional[str] = None
    command_id: Optional[str] = None
    error: Optional[str] = None


# ============================================================
# Transcription API (Audio Upload)
# ============================================================


class TranscriptionResponse(BaseModel):
    """Response from POST /api/voice/transcribe."""

    transcription: str
    success: bool
    error: Optional[str] = None
