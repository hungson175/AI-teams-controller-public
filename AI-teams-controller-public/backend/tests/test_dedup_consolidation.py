# -*- coding: utf-8 -*-
"""Tests for dedup consolidation (Story 7).

TDD: Tests for consolidated deduplication at FastAPI layer.
Dedup should happen ONLY at FastAPI entry point, not in Celery.
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestFastAPILayerDedup:
    """Tests for deduplication at FastAPI layer (task_done_listener.py)."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = MagicMock()
        mock.get.return_value = None  # No duplicate by default
        return mock

    @pytest.fixture
    def listener(self):
        """Create TaskDoneListener instance with cleared state."""
        from app.services.task_done_listener import TaskDoneListener

        instance = TaskDoneListener()
        instance._last_task_done.clear()
        instance._last_commands.clear()
        return instance

    @pytest.mark.asyncio
    async def test_dedup_check_at_fastapi_layer(self, listener, mock_redis):
        """Should check content dedup at FastAPI layer before queueing Celery task."""
        with patch("app.services.task_done_listener.get_dedup_redis_client", return_value=mock_redis):
            with patch("app.services.celery_tasks.process_voice_feedback") as mock_task:
                mock_task.delay.return_value = MagicMock(id="task-123")

                # First call - should process
                result = await listener.stop_hook_fired(
                    team_id="team1",
                    role_id="pane-0",
                    pane_output="> cmd\noutput\n> "
                )

                assert result["success"] is True
                assert "task_id" in result
                mock_task.delay.assert_called_once()

    @pytest.mark.asyncio
    async def test_duplicate_content_skipped(self, listener, mock_redis):
        """Should skip duplicate content within TTL window."""
        # Simulate Redis returning existing hash (duplicate)
        mock_redis.get.return_value = b"1"  # Key exists = duplicate

        with patch("app.services.task_done_listener.get_dedup_redis_client", return_value=mock_redis):
            with patch("app.services.celery_tasks.process_voice_feedback") as mock_task:
                result = await listener.stop_hook_fired(
                    team_id="team1",
                    role_id="pane-0",
                    pane_output="> cmd\noutput\n> "
                )

                assert result["success"] is True
                assert result.get("skipped") is True
                assert result.get("reason") == "duplicate_content"
                mock_task.delay.assert_not_called()

    @pytest.mark.asyncio
    async def test_dedup_key_format(self, listener, mock_redis):
        """Should use correct dedup key format: voice_feedback:dedup:{team}:{role}:{hash}."""
        with patch("app.services.task_done_listener.get_dedup_redis_client", return_value=mock_redis):
            with patch("app.services.task_done_listener.compute_content_hash", return_value="abc123"):
                with patch("app.services.celery_tasks.process_voice_feedback") as mock_task:
                    mock_task.delay.return_value = MagicMock(id="task-123")

                    await listener.stop_hook_fired(
                        team_id="myteam",
                        role_id="pane-0",
                        pane_output="> cmd\noutput\n> "
                    )

                    # Verify Redis was queried with correct key format
                    expected_key = "voice_feedback:dedup:myteam:pane-0:abc123"
                    mock_redis.get.assert_called_with(expected_key)

    @pytest.mark.asyncio
    async def test_dedup_ttl_30_seconds(self, listener, mock_redis):
        """Should set dedup key with 30 second TTL."""
        with patch("app.services.task_done_listener.get_dedup_redis_client", return_value=mock_redis):
            with patch("app.services.task_done_listener.compute_content_hash", return_value="abc123"):
                with patch("app.services.celery_tasks.process_voice_feedback") as mock_task:
                    mock_task.delay.return_value = MagicMock(id="task-123")

                    await listener.stop_hook_fired(
                        team_id="team1",
                        role_id="pane-0",
                        pane_output="> cmd\noutput\n> "
                    )

                    # Verify setex called with 30 second TTL
                    mock_redis.setex.assert_called_once()
                    call_args = mock_redis.setex.call_args
                    assert call_args[0][1] == 30  # TTL

    @pytest.mark.asyncio
    async def test_redis_error_fails_open(self, listener, mock_redis):
        """Should proceed with processing on Redis error (fail-open)."""
        mock_redis.get.side_effect = Exception("Redis connection error")

        with patch("app.services.task_done_listener.get_dedup_redis_client", return_value=mock_redis):
            with patch("app.services.celery_tasks.process_voice_feedback") as mock_task:
                mock_task.delay.return_value = MagicMock(id="task-123")

                result = await listener.stop_hook_fired(
                    team_id="team1",
                    role_id="pane-0",
                    pane_output="> cmd\noutput\n> "
                )

                # Should still process despite Redis error
                assert result["success"] is True
                mock_task.delay.assert_called_once()


class TestCeleryNoDedup:
    """Tests to verify Celery no longer performs deduplication."""

    def test_celery_task_no_dedup_check(self):
        """Celery task should NOT check for duplicate content."""
        from unittest.mock import MagicMock, patch

        mock_tts = MagicMock()
        mock_tts.generate_speech_base64.return_value = "audio"

        mock_redis = MagicMock()

        with patch.dict("os.environ", {"XAI_API_KEY": ""}):
            with patch("app.services.tts_providers.TTSProviderFactory.create", return_value=mock_tts):
                with patch("app.services.voice_feedback.broadcast.get_redis_client", return_value=mock_redis):
                    from app.services.celery_tasks import process_voice_feedback

                    result = process_voice_feedback.run(
                        team_id="team1",
                        role_id="pane-0",
                        pane_output="> cmd\noutput\n> ",
                        original_command="test",
                    )

                    # Task should process without dedup check
                    assert result["success"] is True
                    # Verify summary is returned (was processed, not skipped)
                    assert "summary" in result
                    assert result.get("skipped") is not True

    def test_celery_task_no_is_duplicate_import(self):
        """Celery task should not import is_duplicate_content after Story 7."""
        # This test verifies the refactoring is complete
        from app.services import celery_tasks

        # After Story 7, is_duplicate_content should NOT be used in process_voice_feedback
        # The function should be removed from imports (or at least not called)
        import inspect

        source = inspect.getsource(celery_tasks.process_voice_feedback)

        # The orchestrator should NOT contain dedup logic
        assert "is_duplicate_content" not in source
        assert "duplicate_content" not in source


class TestDedupConstants:
    """Tests for dedup timing constants."""

    def test_dedup_ttl_constant(self):
        """Should have CONTENT_DEDUP_TTL = 30 in voice_constants.py."""
        from app.config.voice_constants import CONTENT_DEDUP_TTL

        assert CONTENT_DEDUP_TTL == 30

    def test_dedup_key_prefix_constant(self):
        """Should have DEDUP_KEY_PREFIX in voice_constants.py."""
        from app.config.voice_constants import DEDUP_KEY_PREFIX

        assert DEDUP_KEY_PREFIX == "voice_feedback:dedup"


class TestComputeContentHash:
    """Tests for content hash computation used in dedup."""

    def test_hash_consistent(self):
        """Same content should produce same hash."""
        from app.services.task_done_listener import compute_content_hash

        content = "> cmd\noutput\n> "
        hash1 = compute_content_hash(content)
        hash2 = compute_content_hash(content)

        assert hash1 == hash2

    def test_hash_different_content(self):
        """Different content should produce different hash."""
        from app.services.task_done_listener import compute_content_hash

        hash1 = compute_content_hash("> cmd1\noutput1\n> ")
        hash2 = compute_content_hash("> cmd2\noutput2\n> ")

        assert hash1 != hash2

    def test_hash_uses_trimmed_content(self):
        """Hash should be computed on trimmed content."""
        from app.services.task_done_listener import compute_content_hash, trim_to_last_input

        # Long content with multiple prompts
        full_content = "old stuff\n> old cmd\nold output\n> new cmd\nnew output\n> "
        trimmed = trim_to_last_input(full_content)

        # Verify trimming happened
        assert len(trimmed) < len(full_content)

        # Hash should be based on trimmed content
        hash_trimmed = compute_content_hash(trimmed)
        assert len(hash_trimmed) == 16  # MD5 prefix
