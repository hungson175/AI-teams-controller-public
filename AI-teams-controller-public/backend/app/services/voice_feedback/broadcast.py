# -*- coding: utf-8 -*-
"""Broadcasting for voice feedback.

Single Responsibility: Broadcast voice feedback to clients via Redis pub/sub.
"""

import json
import logging
import os
import time

import redis

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
VOICE_FEEDBACK_CHANNEL = "voice_feedback"


def get_redis_client() -> redis.Redis:
    """Get Redis client for pub/sub."""
    return redis.from_url(REDIS_URL)


def format_team_name(team_id: str) -> str:
    """Format team name for speech.

    Converts team IDs to natural speech format:
    - 'ai_controller_full_team' -> 'ai controller full team'
    - 'project-foo-bar' -> 'project foo bar'

    Args:
        team_id: Raw team ID (tmux session name)

    Returns:
        Formatted team name for TTS
    """
    return team_id.replace("_", " ").replace("-", " ")


def broadcast_feedback(
    team_id: str,
    role_id: str,
    summary: str,
    audio: str,
    team_name_formatted: str = "",
    team_name_audio: str = "",
) -> None:
    """Broadcast voice feedback to all connected clients via Redis pub/sub.

    All WebSocket clients subscribed to VOICE_FEEDBACK_CHANNEL will receive
    this message, regardless of which team they're currently viewing.

    Args:
        team_id: tmux session name
        role_id: pane index
        summary: Task completion summary (for Voice mode)
        audio: Base64 MP3 of full summary (for Voice mode)
        team_name_formatted: Formatted team name (e.g., "ai controller full team")
        team_name_audio: Base64 MP3 of team name only (for Team Name mode)

    Raises:
        Exception: If Redis publish fails
    """
    message = json.dumps(
        {
            "type": "voice_feedback",
            "team_id": team_id,
            "role_id": role_id,
            "summary": summary,
            "audio": audio,
            "team_name_formatted": team_name_formatted,
            "team_name_audio": team_name_audio,
            "timestamp": int(time.time() * 1000),
        }
    )

    try:
        r = get_redis_client()
        num_subscribers = r.publish(VOICE_FEEDBACK_CHANNEL, message)
        logger.info(f"[BROADCAST] Published to {VOICE_FEEDBACK_CHANNEL} | subscribers={num_subscribers} | audio_len={len(audio)}")
    except Exception as e:
        logger.error(f"[BROADCAST] Redis publish FAILED: {e}")
        raise
