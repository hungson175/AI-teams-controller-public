# -*- coding: utf-8 -*-
"""Voice feedback processing module.

SRP Refactoring: Each submodule has a single responsibility.

Modules:
    content: Output trimming and filtering (trim_to_last_input, filter_hooks)
    summary: LLM summary generation (generate_summary)
    audio: TTS audio generation (generate_tts)
    broadcast: Redis pub/sub broadcasting (broadcast_feedback)

Usage:
    from app.services.voice_feedback import process_voice_feedback
    result = process_voice_feedback(team_id, role_id, pane_output, original_command)

Architecture (Story 4 - Voice Feedback Epic):
    Stop Hook -> FastAPI (skip check) -> Celery Task -> voice_feedback module
                                                            |
                                                            v
                                            content.prepare_content()
                                                            |
                                                            v
                                            summary.generate_summary()
                                                            |
                                                            v
                                            audio.generate_tts()
                                                            |
                                                            v
                                            broadcast.broadcast_feedback()
"""

from app.services.voice_feedback.content import (
    compute_content_hash,
    filter_hooks,
    is_duplicate_content,
    trim_to_last_input,
)
from app.services.voice_feedback.summary import generate_summary
from app.services.voice_feedback.audio import generate_tts
from app.services.voice_feedback.broadcast import (
    broadcast_feedback,
    format_team_name,
)

__all__ = [
    # Content processing
    "trim_to_last_input",
    "filter_hooks",
    "compute_content_hash",
    "is_duplicate_content",
    # Summary generation
    "generate_summary",
    # Audio generation
    "generate_tts",
    # Broadcasting
    "broadcast_feedback",
    "format_team_name",
]
