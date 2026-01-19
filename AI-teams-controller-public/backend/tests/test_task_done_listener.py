# -*- coding: utf-8 -*-
"""Tests for TaskDoneListener service.

All external dependencies (Redis, Celery) are mocked.
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from app.services.task_done_listener import (
    TaskDoneListener,
    GlobalWebSocketManager,
    PendingCommand,
    get_task_done_listener,
)


class TestPendingCommand:
    """Test PendingCommand dataclass."""

    def test_create_pending_command(self):
        """Should create PendingCommand with all fields."""
        cmd = PendingCommand(
            command_id="test-id",
            team_id="team1",
            role_id="pane-0",
            raw_command="fix bug go go",
            corrected_command="Fix the bug",
            timestamp=datetime.now(),
        )

        assert cmd.command_id == "test-id"
        assert cmd.team_id == "team1"
        assert cmd.corrected_command == "Fix the bug"


class TestGlobalWebSocketManager:
    """Test GlobalWebSocketManager."""

    @pytest.fixture
    def ws_manager(self):
        """Get fresh WebSocketManager."""
        return GlobalWebSocketManager()

    async def test_register_websocket(self, ws_manager):
        """Should register WebSocket."""
        mock_ws = MagicMock()
        await ws_manager.register(mock_ws)
        assert mock_ws in ws_manager._websockets

    async def test_unregister_websocket(self, ws_manager):
        """Should unregister WebSocket."""
        mock_ws = MagicMock()
        await ws_manager.register(mock_ws)
        await ws_manager.unregister(mock_ws)
        assert mock_ws not in ws_manager._websockets

    async def test_broadcast_to_all(self, ws_manager):
        """Should broadcast to all connected WebSockets."""
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws1.send_json = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        await ws_manager.register(mock_ws1)
        await ws_manager.register(mock_ws2)

        message = {"type": "test", "data": "hello"}
        await ws_manager.broadcast(message)

        mock_ws1.send_json.assert_called_once_with(message)
        mock_ws2.send_json.assert_called_once_with(message)

    async def test_broadcast_removes_failed(self, ws_manager):
        """Should remove WebSockets that fail to send."""
        mock_ws_good = AsyncMock()
        mock_ws_bad = AsyncMock()
        mock_ws_good.send_json = AsyncMock()
        mock_ws_bad.send_json = AsyncMock(side_effect=Exception("Connection closed"))

        await ws_manager.register(mock_ws_good)
        await ws_manager.register(mock_ws_bad)

        await ws_manager.broadcast({"type": "test"})

        # Bad WebSocket should be removed
        assert mock_ws_bad not in ws_manager._websockets
        assert mock_ws_good in ws_manager._websockets

    async def test_broadcast_empty(self, ws_manager):
        """Should handle broadcast with no WebSockets."""
        # Should not raise
        await ws_manager.broadcast({"type": "test"})


class TestTaskDoneListenerCommandFlow:
    """Test command storage and retrieval."""

    def test_command_sent_stores_command(self, task_done_listener):
        """Should store command for retrieval."""
        cmd_id = task_done_listener.command_sent(
            team_id="team1",
            role_id="pane-0",
            raw_command="test go go",
            corrected_command="Test command",
        )

        assert cmd_id is not None
        pending = task_done_listener.get_pending_command("team1", "pane-0")
        assert pending is not None
        assert pending.corrected_command == "Test command"

    def test_command_sent_with_custom_id(self, task_done_listener):
        """Should use custom command_id if provided."""
        cmd_id = task_done_listener.command_sent(
            team_id="team1",
            role_id="pane-0",
            raw_command="test",
            corrected_command="Test",
            command_id="custom-id",
        )

        assert cmd_id == "custom-id"

    def test_command_overwrites_previous(self, task_done_listener):
        """Should overwrite previous command for same pane."""
        task_done_listener.command_sent(
            team_id="team1",
            role_id="pane-0",
            raw_command="first",
            corrected_command="First",
        )
        task_done_listener.command_sent(
            team_id="team1",
            role_id="pane-0",
            raw_command="second",
            corrected_command="Second",
        )

        pending = task_done_listener.get_pending_command("team1", "pane-0")
        assert pending.corrected_command == "Second"

    def test_get_pending_command_nonexistent(self, task_done_listener):
        """Should return None for nonexistent pane."""
        pending = task_done_listener.get_pending_command("fake", "fake")
        assert pending is None


class TestTaskDoneListenerStopHook:
    """Test stop_hook_fired method."""

    async def test_stop_hook_queues_celery_task(self, task_done_listener):
        """Should queue Celery task on stop hook."""
        # Store a pending command
        task_done_listener.command_sent(
            team_id="team1",
            role_id="pane-0",
            raw_command="test",
            corrected_command="Test",
        )

        with patch(
            "app.services.celery_tasks.process_voice_feedback"
        ) as mock_task:
            mock_task.delay.return_value = MagicMock(id="celery-task-id")

            result = await task_done_listener.stop_hook_fired(
                team_id="team1",
                role_id="pane-0",
                pane_output="mock output",
            )

            assert result["success"] is True
            assert result["task_id"] == "celery-task-id"
            mock_task.delay.assert_called_once()

    async def test_stop_hook_consumes_command(self, task_done_listener):
        """Should consume pending command on stop hook."""
        task_done_listener.command_sent(
            team_id="team1",
            role_id="pane-0",
            raw_command="test",
            corrected_command="Test",
        )

        with patch(
            "app.services.celery_tasks.process_voice_feedback"
        ) as mock_task:
            mock_task.delay.return_value = MagicMock(id="id")

            await task_done_listener.stop_hook_fired(
                team_id="team1",
                role_id="pane-0",
                pane_output="output",
            )

        # Command should be consumed
        pending = task_done_listener.get_pending_command("team1", "pane-0")
        assert pending is None

    async def test_stop_hook_no_pending_command(self, task_done_listener):
        """Should still process even without pending command."""
        with patch(
            "app.services.celery_tasks.process_voice_feedback"
        ) as mock_task:
            mock_task.delay.return_value = MagicMock(id="id")

            result = await task_done_listener.stop_hook_fired(
                team_id="team1",
                role_id="pane-0",
                pane_output="output",
            )

            # Should still succeed (uses default "task" as command)
            assert result["success"] is True

    async def test_stop_hook_celery_failure(self, task_done_listener):
        """Should handle Celery queue failure."""
        with patch(
            "app.services.task_done_listener.is_duplicate_content",
            return_value=False
        ):
            with patch(
                "app.services.celery_tasks.process_voice_feedback"
            ) as mock_task:
                mock_task.delay.side_effect = Exception("Celery connection failed")

                result = await task_done_listener.stop_hook_fired(
                    team_id="team1",
                    role_id="pane-0",
                    pane_output="output",
                )

                assert result["success"] is False
                assert "error" in result


class TestTaskDoneListenerDebounce:
    """Test debounce logic.

    NOTE (Story 7): These tests mock is_duplicate_content to isolate
    time-based debounce testing from content-based dedup testing.
    """

    async def test_debounce_within_window(self, task_done_listener):
        """Should skip duplicate stop hooks within debounce window."""
        with patch(
            "app.services.task_done_listener.is_duplicate_content",
            return_value=False
        ):
            with patch(
                "app.services.celery_tasks.process_voice_feedback"
            ) as mock_task:
                mock_task.delay.return_value = MagicMock(id="id")

                # First call - should process
                result1 = await task_done_listener.stop_hook_fired(
                    team_id="team1",
                    role_id="pane-0",
                    pane_output="output",
                )

                # Second call immediately - should be debounced
                result2 = await task_done_listener.stop_hook_fired(
                    team_id="team1",
                    role_id="pane-0",
                    pane_output="output",
                )

                assert result1["success"] is True
                assert "skipped" not in result1

                assert result2["success"] is True
                assert result2.get("skipped") is True
                assert result2.get("reason") == "debounced"

                # Celery task should only be called once
                assert mock_task.delay.call_count == 1

    async def test_debounce_different_panes(self, task_done_listener):
        """Should not debounce different panes."""
        with patch(
            "app.services.task_done_listener.is_duplicate_content",
            return_value=False
        ):
            with patch(
                "app.services.celery_tasks.process_voice_feedback"
            ) as mock_task:
                mock_task.delay.return_value = MagicMock(id="id")

                result1 = await task_done_listener.stop_hook_fired(
                    team_id="team1",
                    role_id="pane-0",
                    pane_output="output",
                )
                result2 = await task_done_listener.stop_hook_fired(
                    team_id="team1",
                    role_id="pane-1",  # Different pane
                    pane_output="output",
                )

                assert result1["success"] is True
                assert result2["success"] is True
                assert "skipped" not in result1
                assert "skipped" not in result2

                # Both should be processed
                assert mock_task.delay.call_count == 2

    async def test_debounce_exact_window_boundary(self, task_done_listener):
        """Should respect exact TASK_DONE_DEBOUNCE_MS window (10 seconds).

        This test verifies the actual 10-second debounce window:
        - Calls within 10 seconds: debounced
        - Calls after 10 seconds: processed
        """
        with patch(
            "app.services.task_done_listener.is_duplicate_content",
            return_value=False
        ):
            with patch(
                "app.services.celery_tasks.process_voice_feedback"
            ) as mock_task:
                mock_task.delay.return_value = MagicMock(id="id")

                # First call - should process
                result1 = await task_done_listener.stop_hook_fired(
                    team_id="team1",
                    role_id="pane-0",
                    pane_output="output",
                )
                assert result1["success"] is True
                assert "skipped" not in result1

                # Simulate call 9 seconds later (within 10-second window)
                # Manually set timestamp to 9 seconds ago
                pane_key = "team1:pane-0"
                now = datetime.now()
                task_done_listener._last_task_done[pane_key] = now - timedelta(seconds=9)

                result2 = await task_done_listener.stop_hook_fired(
                    team_id="team1",
                    role_id="pane-0",
                    pane_output="output",
                )
                # Should be debounced (9 seconds < 10 seconds)
                assert result2["success"] is True
                assert result2.get("skipped") is True
                assert result2.get("reason") == "debounced"

                # Simulate call 11 seconds later (beyond 10-second window)
                # Set timestamp to 11 seconds ago
                task_done_listener._last_task_done[pane_key] = now - timedelta(seconds=11)

                result3 = await task_done_listener.stop_hook_fired(
                    team_id="team1",
                    role_id="pane-0",
                    pane_output="output",
                )
                # Should NOT be debounced (11 seconds > 10 seconds)
                assert result3["success"] is True
                assert "skipped" not in result3

                # Celery task should be called twice (first + third, second was debounced)
                assert mock_task.delay.call_count == 2


class TestGetTaskDoneListener:
    """Test singleton getter."""

    def test_returns_singleton(self):
        """Should return same instance."""
        # Reset singleton for test
        import app.services.task_done_listener as module
        module._listener = None

        listener1 = get_task_done_listener()
        listener2 = get_task_done_listener()

        assert listener1 is listener2

    def test_creates_instance_if_none(self):
        """Should create instance if none exists."""
        import app.services.task_done_listener as module
        module._listener = None

        listener = get_task_done_listener()

        assert listener is not None
        assert isinstance(listener, TaskDoneListener)


class TestPubSubListener:
    """Test Redis pub/sub listener methods."""

    async def test_start_pubsub_listener(self, task_done_listener):
        """Should start pub/sub listener task."""
        with patch("redis.asyncio.from_url") as mock_redis:
            mock_pubsub = AsyncMock()
            mock_pubsub.subscribe = AsyncMock()
            # Create async iterator that yields nothing (immediately exits)
            async def empty_iterator():
                return
                yield  # Make it a generator
            mock_pubsub.listen = empty_iterator
            mock_redis.return_value.pubsub.return_value = mock_pubsub

            await task_done_listener.start_pubsub_listener()

            # Task should be created
            assert task_done_listener._pubsub_task is not None

            # Clean up
            task_done_listener._pubsub_task.cancel()
            try:
                await task_done_listener._pubsub_task
            except asyncio.CancelledError:
                pass

    async def test_start_pubsub_listener_already_running(self, task_done_listener):
        """Should not start if already running (task.done() == False)."""
        # Set up a fake running task - done() returns False (still running)
        mock_task = MagicMock()
        mock_task.done.return_value = False
        task_done_listener._pubsub_task = mock_task

        await task_done_listener.start_pubsub_listener()

        # Should not create a new task (still same mock)
        assert task_done_listener._pubsub_task is mock_task

    async def test_start_pubsub_listener_restarts_crashed(self, task_done_listener):
        """Should restart if previous task crashed (task.done() == True).

        This tests the liveness check pattern: if the pub/sub listener task
        has completed (either normally or via exception), it should be
        automatically restarted instead of silently failing.
        """
        # Set up a crashed task - done() returns True (task completed/crashed)
        mock_crashed_task = MagicMock()
        mock_crashed_task.done.return_value = True
        task_done_listener._pubsub_task = mock_crashed_task

        with patch("redis.asyncio.from_url") as mock_redis:
            mock_pubsub = AsyncMock()
            mock_pubsub.subscribe = AsyncMock()

            # Create async iterator that yields nothing (immediately exits)
            async def empty_iterator():
                return
                yield  # Make it a generator

            mock_pubsub.listen = empty_iterator
            mock_redis.return_value.pubsub.return_value = mock_pubsub

            await task_done_listener.start_pubsub_listener()

            # Should have created a NEW task (not the crashed mock)
            assert task_done_listener._pubsub_task is not mock_crashed_task
            assert task_done_listener._pubsub_task is not None

            # Clean up
            task_done_listener._pubsub_task.cancel()
            try:
                await task_done_listener._pubsub_task
            except asyncio.CancelledError:
                pass

    async def test_stop_pubsub_listener(self, task_done_listener):
        """Should stop pub/sub listener task."""
        # Create a real asyncio.Task that will be cancelled
        async def dummy_loop():
            await asyncio.sleep(100)

        task_done_listener._pubsub_task = asyncio.create_task(dummy_loop())

        await task_done_listener.stop_pubsub_listener()

        assert task_done_listener._pubsub_task is None

    async def test_stop_pubsub_listener_no_task(self, task_done_listener):
        """Should handle stop when no task running."""
        task_done_listener._pubsub_task = None

        # Should not raise
        await task_done_listener.stop_pubsub_listener()

    async def test_pubsub_loop_broadcasts_messages(self, task_done_listener):
        """Should broadcast messages received from Redis."""
        # Create a message that will be yielded
        test_message = {
            "type": "message",
            "data": '{"type": "voice_feedback", "team_id": "team1", "role_id": "pane-0"}',
        }

        with patch("redis.asyncio.from_url") as mock_redis:
            mock_pubsub = AsyncMock()
            mock_pubsub.subscribe = AsyncMock()

            # Create async iterator that yields one message then raises CancelledError
            async def message_iterator():
                yield test_message
                raise asyncio.CancelledError()

            mock_pubsub.listen = message_iterator
            mock_redis.return_value.pubsub.return_value = mock_pubsub

            # Mock the broadcast
            task_done_listener.ws_manager.broadcast = AsyncMock()

            # Run the loop (should cancel after one message)
            try:
                await task_done_listener._pubsub_loop()
            except asyncio.CancelledError:
                pass

            # Should have broadcasted the message
            task_done_listener.ws_manager.broadcast.assert_called_once()

    async def test_pubsub_loop_handles_json_error(self, task_done_listener):
        """Should handle invalid JSON in pub/sub message."""
        # Create a message with invalid JSON
        test_message = {
            "type": "message",
            "data": "not valid json",
        }

        with patch("redis.asyncio.from_url") as mock_redis:
            mock_pubsub = AsyncMock()
            mock_pubsub.subscribe = AsyncMock()

            async def message_iterator():
                yield test_message
                raise asyncio.CancelledError()

            mock_pubsub.listen = message_iterator
            mock_redis.return_value.pubsub.return_value = mock_pubsub

            task_done_listener.ws_manager.broadcast = AsyncMock()

            # Should not raise, just log error
            try:
                await task_done_listener._pubsub_loop()
            except asyncio.CancelledError:
                pass

            # Should not have broadcasted (invalid JSON)
            task_done_listener.ws_manager.broadcast.assert_not_called()


class TestLegacyWebSocketMethods:
    """Test legacy WebSocket registration methods."""

    async def test_register_websocket(self, task_done_listener):
        """Should delegate to ws_manager."""
        mock_ws = MagicMock()

        with patch.object(task_done_listener.ws_manager, "register", new_callable=AsyncMock) as mock_register:
            task_done_listener.register_websocket("team1", "pane-0", mock_ws)

            # Give the event loop a chance to run the created task
            await asyncio.sleep(0.1)

            # Should have called register
            mock_register.assert_called_once_with(mock_ws)

    def test_unregister_websocket(self, task_done_listener):
        """Should log unregister (no actual removal without WS reference)."""
        # Just verify code path works (logs a warning about limitation)
        task_done_listener.unregister_websocket("team1", "pane-0")
