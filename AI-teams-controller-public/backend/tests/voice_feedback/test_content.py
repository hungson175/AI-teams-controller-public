# -*- coding: utf-8 -*-
"""Tests for voice_feedback.content module.

TDD: Tests for content processing functions (trim, filter, hash, dedup).
"""

from unittest.mock import MagicMock, patch

import pytest


class TestTrimToLastInput:
    """Tests for trim_to_last_input function."""

    def test_trim_with_multiple_prompts(self):
        """Should keep only content from second-to-last prompt onwards."""
        from app.services.voice_feedback.content import trim_to_last_input

        output = "> old command\nold output\n> new command\nnew output\n> "
        result = trim_to_last_input(output)

        assert "> new command" in result
        assert "new output" in result
        assert "old command" not in result

    def test_trim_with_exactly_two_prompts(self):
        """Should work with exactly two prompts."""
        from app.services.voice_feedback.content import trim_to_last_input

        output = "> command\noutput\n> "
        result = trim_to_last_input(output)

        assert "> command" in result
        assert "output" in result

    def test_trim_with_single_prompt(self):
        """Should return full output with less than 2 prompts."""
        from app.services.voice_feedback.content import trim_to_last_input

        output = "> single\noutput"
        result = trim_to_last_input(output)

        assert result == output

    def test_trim_with_no_prompts(self):
        """Should return full output with no prompts."""
        from app.services.voice_feedback.content import trim_to_last_input

        output = "no prompts here\njust text"
        result = trim_to_last_input(output)

        assert result == output

    def test_trim_with_indented_prompts(self):
        """Should detect indented prompts (stripped)."""
        from app.services.voice_feedback.content import trim_to_last_input

        output = "  > old\nold output\n  > new\nnew output\n  > "
        result = trim_to_last_input(output)

        assert "> new" in result or "new" in result.split("\n")[0]

    def test_trim_empty_string(self):
        """Should handle empty string gracefully."""
        from app.services.voice_feedback.content import trim_to_last_input

        result = trim_to_last_input("")
        assert result == ""


class TestFilterHooks:
    """Tests for filter_hooks function."""

    def test_filter_stop_hook(self):
        """Should truncate at Stop hook marker."""
        from app.services.voice_feedback.content import filter_hooks

        output = "Real output\nMore output\nStop hook fired\nHook message"
        result = filter_hooks(output)

        assert "Real output" in result
        assert "Stop hook" not in result

    def test_filter_system_reminder(self):
        """Should truncate at <system-reminder>."""
        from app.services.voice_feedback.content import filter_hooks

        output = "Output line\n<system-reminder>Don't include this"
        result = filter_hooks(output)

        assert "Output line" in result
        assert "<system-reminder>" not in result

    def test_filter_memory_store(self):
        """Should truncate at coder-memory-store marker."""
        from app.services.voice_feedback.content import filter_hooks

        output = "Task complete\ncoder-memory-store invoked\nMore text"
        result = filter_hooks(output)

        assert "Task complete" in result
        assert "coder-memory-store" not in result

    def test_filter_case_insensitive(self):
        """Should be case-insensitive for markers."""
        from app.services.voice_feedback.content import filter_hooks

        output = "Output\nSTOP HOOK fired\nHidden"
        result = filter_hooks(output)

        assert "Output" in result
        assert "STOP HOOK" not in result

    def test_filter_no_hooks(self):
        """Should return full output if no hooks present."""
        from app.services.voice_feedback.content import filter_hooks

        output = "Normal output\nNo hooks here\nAll good"
        result = filter_hooks(output)

        assert result == output

    def test_filter_empty_string(self):
        """Should handle empty string gracefully."""
        from app.services.voice_feedback.content import filter_hooks

        result = filter_hooks("")
        assert result == ""


class TestComputeContentHash:
    """Tests for compute_content_hash function."""

    def test_hash_returns_16_chars(self):
        """Should return 16-character hash."""
        from app.services.voice_feedback.content import compute_content_hash

        result = compute_content_hash("test content")
        assert len(result) == 16

    def test_hash_same_content_same_hash(self):
        """Should return same hash for same content."""
        from app.services.voice_feedback.content import compute_content_hash

        hash1 = compute_content_hash("identical content")
        hash2 = compute_content_hash("identical content")
        assert hash1 == hash2

    def test_hash_different_content_different_hash(self):
        """Should return different hash for different content."""
        from app.services.voice_feedback.content import compute_content_hash

        hash1 = compute_content_hash("content A")
        hash2 = compute_content_hash("content B")
        assert hash1 != hash2

    def test_hash_empty_string(self):
        """Should handle empty string."""
        from app.services.voice_feedback.content import compute_content_hash

        result = compute_content_hash("")
        assert len(result) == 16


class TestIsDuplicateContent:
    """Tests for is_duplicate_content function."""

    @patch("app.services.voice_feedback.content.get_redis_client")
    def test_new_content_returns_false(self, mock_get_redis):
        """Should return False for new content (not duplicate)."""
        from app.services.voice_feedback.content import is_duplicate_content

        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_get_redis.return_value = mock_redis

        result = is_duplicate_content("team1", "pane-0", "newhash123")

        assert result is False
        mock_redis.setex.assert_called_once()

    @patch("app.services.voice_feedback.content.get_redis_client")
    def test_existing_content_returns_true(self, mock_get_redis):
        """Should return True for duplicate content."""
        from app.services.voice_feedback.content import is_duplicate_content

        mock_redis = MagicMock()
        mock_redis.get.return_value = b"samehash123"
        mock_get_redis.return_value = mock_redis

        result = is_duplicate_content("team1", "pane-0", "samehash123")

        assert result is True

    @patch("app.services.voice_feedback.content.get_redis_client")
    def test_redis_error_returns_false(self, mock_get_redis):
        """Should return False (fail-open) on Redis error."""
        from app.services.voice_feedback.content import is_duplicate_content

        mock_get_redis.side_effect = Exception("Redis connection failed")

        result = is_duplicate_content("team1", "pane-0", "hash123")

        assert result is False  # Fail-open


class TestGetRedisClient:
    """Tests for get_redis_client function."""

    @patch("app.services.voice_feedback.content.redis.from_url")
    def test_returns_redis_client(self, mock_from_url):
        """Should return Redis client from URL."""
        from app.services.voice_feedback.content import get_redis_client

        mock_client = MagicMock()
        mock_from_url.return_value = mock_client

        result = get_redis_client()

        assert result == mock_client
        mock_from_url.assert_called_once()
