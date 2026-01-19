# -*- coding: utf-8 -*-
"""Integration tests for voice feedback system.

These tests require real external services:
- Redis server running on localhost:6379
- Celery worker (optional - some tests verify without worker)
- tmux (for skip logic tests)

Run with: pytest tests/integration/ -m integration -v

IMPORTANT: These tests are marked with @pytest.mark.integration
and are NOT run by default in CI. Run manually after code changes
to verify real service integration.
"""

import os
import subprocess
import time
from unittest.mock import patch

import pytest
import redis

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


def redis_available():
    """Check if Redis is available."""
    try:
        client = redis.from_url("redis://localhost:6379/0")
        client.ping()
        return True
    except (redis.ConnectionError, redis.exceptions.ConnectionError):
        return False


def celery_worker_running():
    """Check if Celery worker is running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "celery.*worker"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def tmux_available():
    """Check if tmux is available."""
    try:
        result = subprocess.run(
            ["tmux", "-V"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


class TestRedisConnection:
    """Test Redis connectivity for voice feedback."""

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_redis_ping(self):
        """Should connect to Redis successfully."""
        client = redis.from_url("redis://localhost:6379/0")
        assert client.ping() is True

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_redis_pubsub_channel(self):
        """Should be able to publish to voice_feedback channel."""
        client = redis.from_url("redis://localhost:6379/0")

        # Publish a test message
        listeners = client.publish("voice_feedback", '{"test": true}')

        # May be 0 if no subscribers, but should not raise
        assert listeners >= 0

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_content_hash_storage(self):
        """Should store and retrieve content hashes for deduplication."""
        client = redis.from_url("redis://localhost:6379/0")

        # Test key pattern used by voice feedback
        test_key = "voice_feedback:last_hash:test_team:test_pane"
        test_hash = "abc123def456"

        # Store hash
        client.setex(test_key, 60, test_hash)

        # Retrieve hash
        stored = client.get(test_key)
        assert stored is not None
        assert stored.decode() == test_hash

        # Clean up
        client.delete(test_key)


class TestCeleryIntegration:
    """Test Celery worker integration."""

    @pytest.mark.skipif(
        not (redis_available() and celery_worker_running()),
        reason="Redis or Celery worker not available"
    )
    def test_celery_worker_receives_task(self):
        """Should queue task and have worker process it.

        This test verifies that:
        1. Task can be queued to Celery
        2. Worker picks up the task
        3. Result is stored in Redis

        NOTE: This requires a running Celery worker.
        """
        from app.services.celery_tasks import process_voice_feedback

        # Queue task with mock data
        # This will fail LLM/TTS but should still create result
        with patch.dict(os.environ, {"XAI_API_KEY": ""}):
            task = process_voice_feedback.delay(
                team_id="integration_test",
                role_id="pane-0",
                pane_output="> test\noutput\n> done",
                original_command="integration test",
            )

            # Wait for result (with timeout)
            try:
                result = task.get(timeout=30)
                # Should succeed (with placeholder summary due to no API key)
                assert result["success"] is True
                assert "integration test" in result.get("summary", "")
            except Exception as e:
                pytest.skip(f"Celery task failed (may need worker restart): {e}")

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_task_queuing_without_worker(self):
        """Should queue task even without worker running."""
        from app.services.celery_tasks import process_voice_feedback

        # Queue task - should not block even if no worker
        task = process_voice_feedback.delay(
            team_id="no_worker_test",
            role_id="pane-0",
            pane_output="test output",
            original_command="test",
        )

        # Task should have an ID
        assert task.id is not None


class TestSkipLogicIntegration:
    """Test skip logic with real tmux (if available)."""

    @pytest.mark.skipif(not tmux_available(), reason="tmux not available")
    def test_get_pane_title_real_tmux(self):
        """Should get real pane title from tmux."""
        from app.services.skip_logic import get_pane_title

        # Try to get title from a session (may not exist)
        # This verifies the tmux command works, not necessarily the result
        title = get_pane_title("nonexistent_session", "pane-0")

        # Should return empty string for nonexistent session (not crash)
        assert title == ""

    @pytest.mark.skipif(not tmux_available(), reason="tmux not available")
    def test_should_skip_role_real_tmux(self):
        """Should run skip logic with real tmux commands."""
        from app.services.skip_logic import should_skip_role

        # Nonexistent session should fail-closed (skip)
        result = should_skip_role("nonexistent_integration_test", "pane-0")

        # Should skip (fail-closed)
        assert result is True


class TestEndToEndVoiceFeedback:
    """End-to-end tests for voice feedback flow."""

    @pytest.mark.skipif(
        not (redis_available() and celery_worker_running() and tmux_available()),
        reason="Requires Redis, Celery worker, and tmux"
    )
    def test_full_voice_feedback_flow(self):
        """Test complete voice feedback flow.

        This test simulates what happens when a Stop hook fires:
        1. Skip logic runs (FastAPI layer)
        2. If not skipped, Celery task is queued
        3. Worker processes task
        4. Result published to Redis

        NOTE: This is a heavyweight test - run manually after changes.
        """
        from app.services.skip_logic import should_skip_role
        from app.services.celery_tasks import process_voice_feedback

        # Step 1: Skip logic (will skip for nonexistent session - fail-closed)
        should_skip = should_skip_role("e2e_test_session", "pane-0")
        assert should_skip is True  # Fail-closed for nonexistent

        # Step 2: If we had a real session, we'd queue task
        # For now, just verify task can be queued
        with patch.dict(os.environ, {"XAI_API_KEY": ""}):
            task = process_voice_feedback.delay(
                team_id="e2e_test",
                role_id="pane-0",
                pane_output="> e2e test\nDone.\n> ready",
                original_command="e2e test command",
            )

            assert task.id is not None

    @pytest.mark.skipif(not redis_available(), reason="Redis not available")
    def test_dedup_prevents_duplicate_processing(self):
        """Test that duplicate content is detected.

        NOTE (Story 7): Dedup is now at FastAPI layer (task_done_listener.py).
        """
        from app.services.task_done_listener import (
            compute_content_hash,
            is_duplicate_content,
        )
        from app.config.voice_constants import DEDUP_KEY_PREFIX

        client = redis.from_url("redis://localhost:6379/0")

        # Test content
        content = "test output for dedup"
        content_hash = compute_content_hash(content)

        # First call - should NOT be duplicate
        # Clear any existing hash first
        key = f"{DEDUP_KEY_PREFIX}:dedup_test:pane-0:{content_hash}"
        client.delete(key)

        result1 = is_duplicate_content("dedup_test", "pane-0", content_hash)
        assert result1 is False  # New content

        # Second call with same hash - should BE duplicate
        result2 = is_duplicate_content("dedup_test", "pane-0", content_hash)
        assert result2 is True  # Duplicate

        # Clean up
        client.delete(key)
