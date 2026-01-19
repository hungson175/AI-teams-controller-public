# -*- coding: utf-8 -*-
"""Tests for voice_feedback.broadcast module.

TDD: Tests for Redis pub/sub broadcasting.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestFormatTeamName:
    """Tests for format_team_name function."""

    def test_format_underscores(self):
        """Should replace underscores with spaces."""
        from app.services.voice_feedback.broadcast import format_team_name

        result = format_team_name("ai_controller_full_team")
        assert result == "ai controller full team"

    def test_format_hyphens(self):
        """Should replace hyphens with spaces."""
        from app.services.voice_feedback.broadcast import format_team_name

        result = format_team_name("project-foo-bar")
        assert result == "project foo bar"

    def test_format_mixed_separators(self):
        """Should handle both underscores and hyphens."""
        from app.services.voice_feedback.broadcast import format_team_name

        result = format_team_name("my_team-name")
        assert result == "my team name"

    def test_format_simple_name(self):
        """Should leave simple names unchanged."""
        from app.services.voice_feedback.broadcast import format_team_name

        result = format_team_name("simplename")
        assert result == "simplename"

    def test_format_empty_string(self):
        """Should handle empty string."""
        from app.services.voice_feedback.broadcast import format_team_name

        result = format_team_name("")
        assert result == ""


class TestBroadcastFeedback:
    """Tests for broadcast_feedback function."""

    @patch("app.services.voice_feedback.broadcast.get_redis_client")
    def test_broadcast_publishes_to_redis(self, mock_get_redis):
        """Should publish message to Redis channel."""
        from app.services.voice_feedback.broadcast import (
            VOICE_FEEDBACK_CHANNEL,
            broadcast_feedback,
        )

        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        broadcast_feedback(
            team_id="team1",
            role_id="pane-0",
            summary="Task done",
            audio="audiodata",
        )

        mock_redis.publish.assert_called_once()
        call_args = mock_redis.publish.call_args
        assert call_args[0][0] == VOICE_FEEDBACK_CHANNEL

    @patch("app.services.voice_feedback.broadcast.get_redis_client")
    def test_broadcast_message_format(self, mock_get_redis):
        """Should publish correctly formatted JSON message."""
        from app.services.voice_feedback.broadcast import broadcast_feedback

        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        broadcast_feedback(
            team_id="team1",
            role_id="pane-0",
            summary="Summary text",
            audio="base64audio",
            team_name_formatted="team one",
            team_name_audio="teamaudio",
        )

        # Parse the published message
        call_args = mock_redis.publish.call_args
        message = json.loads(call_args[0][1])

        assert message["type"] == "voice_feedback"
        assert message["team_id"] == "team1"
        assert message["role_id"] == "pane-0"
        assert message["summary"] == "Summary text"
        assert message["audio"] == "base64audio"
        assert message["team_name_formatted"] == "team one"
        assert message["team_name_audio"] == "teamaudio"
        assert "timestamp" in message

    @patch("app.services.voice_feedback.broadcast.get_redis_client")
    def test_broadcast_includes_timestamp(self, mock_get_redis):
        """Should include timestamp in message."""
        from app.services.voice_feedback.broadcast import broadcast_feedback

        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        broadcast_feedback("team", "pane", "summary", "audio")

        call_args = mock_redis.publish.call_args
        message = json.loads(call_args[0][1])

        assert "timestamp" in message
        assert isinstance(message["timestamp"], int)
        assert message["timestamp"] > 0

    @patch("app.services.voice_feedback.broadcast.get_redis_client")
    def test_broadcast_redis_failure_raises(self, mock_get_redis):
        """Should raise exception on Redis failure."""
        from app.services.voice_feedback.broadcast import broadcast_feedback

        mock_redis = MagicMock()
        mock_redis.publish.side_effect = Exception("Redis error")
        mock_get_redis.return_value = mock_redis

        with pytest.raises(Exception, match="Redis error"):
            broadcast_feedback("team", "pane", "summary", "audio")

    @patch("app.services.voice_feedback.broadcast.get_redis_client")
    def test_broadcast_optional_team_name_fields(self, mock_get_redis):
        """Should handle optional team_name fields."""
        from app.services.voice_feedback.broadcast import broadcast_feedback

        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        # Call without optional fields
        broadcast_feedback("team", "pane", "summary", "audio")

        call_args = mock_redis.publish.call_args
        message = json.loads(call_args[0][1])

        assert message["team_name_formatted"] == ""
        assert message["team_name_audio"] == ""


class TestGetRedisClient:
    """Tests for get_redis_client function."""

    @patch("app.services.voice_feedback.broadcast.redis.from_url")
    def test_returns_redis_client(self, mock_from_url):
        """Should return Redis client from URL."""
        from app.services.voice_feedback.broadcast import get_redis_client

        mock_client = MagicMock()
        mock_from_url.return_value = mock_client

        result = get_redis_client()

        assert result == mock_client
        mock_from_url.assert_called_once()
