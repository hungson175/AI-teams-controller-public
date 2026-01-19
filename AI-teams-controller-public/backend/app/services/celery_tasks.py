# -*- coding: utf-8 -*-
"""Celery tasks for voice feedback processing.

These tasks run in a separate Celery worker process,
independent of the FastAPI server and UI state.

Architecture:
    Stop Hook → POST /api/voice/task-done → Celery Task Queue
                                                ↓
                                        Background Worker
                                                ↓
                                        LLM Summary + TTS
                                                ↓
                                        Redis Pub/Sub → All WebSocket clients

SRP Refactoring (Story 4):
    Voice feedback logic is now split into focused modules:
    - content.py: trim_to_last_input, filter_hooks (dedup moved to FastAPI - Story 7)
    - summary.py: generate_summary (LLM)
    - audio.py: generate_tts (TTS provider)
    - broadcast.py: broadcast_feedback, format_team_name

Story 7: Dedup consolidated to FastAPI layer (task_done_listener.py).
    Celery no longer checks for duplicates - that's handled before queueing.
"""

import logging

from celery_config import celery_app

# Import from SRP-refactored voice_feedback module
from app.services.voice_feedback.audio import generate_tts
from app.services.voice_feedback.broadcast import broadcast_feedback, format_team_name
from app.services.voice_feedback.content import (
    REDIS_URL,
    compute_content_hash,
    get_redis_client,
    trim_to_last_input,
)
from app.services.voice_feedback.summary import generate_summary

logger = logging.getLogger(__name__)

# Re-export for backward compatibility with existing tests
_trim_to_last_input = trim_to_last_input
_compute_content_hash = compute_content_hash
_generate_summary = generate_summary
_generate_tts = generate_tts
_broadcast_feedback = broadcast_feedback


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=5,
    acks_late=True,
)
def process_voice_feedback(
    self,
    team_id: str,
    role_id: str,
    pane_output: str,
    original_command: str = "task",
    request_id: str = "",
    speed: float = 1.0,  # TTS speech speed (0.5-2.0, default 1.0 = normal)
) -> dict:
    """Orchestrate voice feedback: summary + TTS + broadcast.

    This is the main Celery task that coordinates the SRP-refactored modules.
    Logic is delegated to focused sub-modules for testability and maintainability.

    Note (Story 7): Dedup is handled at FastAPI layer before queueing.
    This task assumes content is NOT a duplicate.
    """
    task_id = self.request.id
    log_prefix = f"[CELERY:{request_id}]" if request_id else "[CELERY]"
    logger.info(f"{log_prefix} TASK-START: {team_id}/{role_id} (celery_task={task_id})")

    try:
        # Step 1: Content processing - trim for summarization
        trimmed = trim_to_last_input(pane_output)
        logger.info(f"{log_prefix} CONTENT-TRIMMED: {len(pane_output)} -> {len(trimmed)} chars")

        # Step 2: Generate summary and audio
        summary = generate_summary(original_command, pane_output, trimmed)
        logger.info(f"{log_prefix} SUMMARY-GENERATED: {len(summary)} chars")
        audio = generate_tts(summary, speed=speed)  # Pass speed to TTS
        logger.info(f"{log_prefix} TTS-GENERATED: {len(audio)} bytes audio")

        # Step 3: Generate team name audio
        team_name = format_team_name(team_id)
        team_audio = generate_tts(team_name, speed=speed)  # Pass speed to TTS

        # Step 4: Broadcast to clients
        broadcast_feedback(team_id, role_id, summary, audio, team_name, team_audio)
        logger.info(f"{log_prefix} BROADCAST-DONE: {team_id}/{role_id}")

        logger.info(f"{log_prefix} TASK-COMPLETE: {team_id}/{role_id}")
        return {"success": True, "team_id": team_id, "role_id": role_id, "summary": summary}

    except Exception as e:
        logger.error(f"{log_prefix} TASK-FAILED: {team_id}/{role_id} | error={e}")
        return {"success": False, "team_id": team_id, "role_id": role_id, "error": str(e)[:200]}
