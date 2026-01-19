# -*- coding: utf-8 -*-
"""Tests for TmuxService behaviors that will be extracted in Sprint 2.

These tests verify existing behavior BEFORE refactoring.
After extraction, these same tests should still pass with extracted classes.

Components to be extracted:
1. ActivityDetector - Background polling and activity detection
2. MessageTracker - Message tracking and highlight text
3. TmuxRunner - Tmux command execution utility
"""

import time
import threading
from unittest.mock import patch, MagicMock

import pytest

from app.services.tmux_service import TmuxService


# ============================================================
# ActivityDetector Behavior Tests
# ============================================================


class TestActivityDetection:
    """Test activity detection behavior (will become ActivityDetector class)."""

    def test_pane_activity_first_check_always_false(self, tmux_service):
        """First activity check should return False (no previous state)."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            mock_run.return_value = (True, "pane output line 1\nline 2")

            is_active = tmux_service._get_pane_activity("team1", "0")

            assert is_active is False, "First check should be False (no previous state)"

    def test_pane_activity_unchanged_returns_false(self, tmux_service):
        """Unchanged pane output should return False."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            output = "pane output line 1\nline 2"
            mock_run.return_value = (True, output)

            # First check - stores state
            tmux_service._get_pane_activity("team1", "0")

            # Second check - same output
            is_active = tmux_service._get_pane_activity("team1", "0")

            assert is_active is False, "Unchanged output should be False"

    def test_pane_activity_changed_returns_true(self, tmux_service):
        """Changed pane output should return True."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            # First check
            mock_run.return_value = (True, "old output")
            tmux_service._get_pane_activity("team1", "0")

            # Second check - output changed
            mock_run.return_value = (True, "new output")
            is_active = tmux_service._get_pane_activity("team1", "0")

            assert is_active is True, "Changed output should be True"

    def test_pane_activity_last_20_lines_comparison(self, tmux_service):
        """Activity detection should compare last 20 lines only."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            # Generate output with 50 lines
            lines = [f"line {i}" for i in range(50)]
            output1 = "\n".join(lines)
            mock_run.return_value = (True, output1)

            # First check
            tmux_service._get_pane_activity("team1", "0")

            # Second check - only first 30 lines changed, last 20 same
            lines_changed = [f"CHANGED {i}" for i in range(30)] + lines[30:]
            output2 = "\n".join(lines_changed)
            mock_run.return_value = (True, output2)

            is_active = tmux_service._get_pane_activity("team1", "0")

            # Last 20 lines are same, should be False
            assert is_active is False, "Only last 20 lines should be compared"

    def test_pane_activity_last_20_lines_changed(self, tmux_service):
        """Activity detection should detect changes in last 20 lines."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            # Generate output with 50 lines
            lines = [f"line {i}" for i in range(50)]
            output1 = "\n".join(lines)
            mock_run.return_value = (True, output1)

            # First check
            tmux_service._get_pane_activity("team1", "0")

            # Second check - last 5 lines changed
            lines_changed = lines[:45] + [f"NEW line {i}" for i in range(45, 50)]
            output2 = "\n".join(lines_changed)
            mock_run.return_value = (True, output2)

            is_active = tmux_service._get_pane_activity("team1", "0")

            # Last 20 lines changed, should be True
            assert is_active is True, "Changes in last 20 lines should be detected"

    def test_pane_activity_different_panes_tracked_separately(self, tmux_service):
        """Different panes should have separate activity tracking."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            # Pane 0 - first check
            mock_run.return_value = (True, "pane 0 output")
            tmux_service._get_pane_activity("team1", "0")

            # Pane 1 - first check
            mock_run.return_value = (True, "pane 1 output")
            tmux_service._get_pane_activity("team1", "1")

            # Pane 0 - second check, changed
            mock_run.return_value = (True, "pane 0 NEW output")
            is_active_0 = tmux_service._get_pane_activity("team1", "0")

            # Pane 1 - second check, unchanged
            mock_run.return_value = (True, "pane 1 output")
            is_active_1 = tmux_service._get_pane_activity("team1", "1")

            assert is_active_0 is True, "Pane 0 should be active"
            assert is_active_1 is False, "Pane 1 should be idle"

    def test_pane_activity_capture_failure_returns_false(self, tmux_service):
        """Failed pane capture should return False."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            mock_run.return_value = (False, "capture failed")

            is_active = tmux_service._get_pane_activity("team1", "0")

            assert is_active is False, "Failed capture should return False"


class TestBackgroundPolling:
    """Test background polling behavior (will become ActivityDetector methods)."""

    def test_start_background_polling_creates_thread(self, tmux_service):
        """start_background_polling should create and start daemon thread."""
        with patch.object(tmux_service, "_poll_all_panes"):
            tmux_service.start_background_polling()

            # Access thread through _activity_detector (Sprint 2 refactor)
            thread = tmux_service._activity_detector._polling_thread
            assert thread is not None
            assert thread.is_alive()
            assert thread.daemon is True
            assert thread.name == "tmux-activity-poller"

            # Cleanup
            tmux_service.stop_background_polling()

    def test_start_background_polling_already_running(self, tmux_service):
        """Starting polling when already running should be a no-op."""
        with patch.object(tmux_service, "_poll_all_panes"):
            tmux_service.start_background_polling()
            # Access thread through _activity_detector (Sprint 2 refactor)
            thread1 = tmux_service._activity_detector._polling_thread

            # Try to start again
            tmux_service.start_background_polling()
            thread2 = tmux_service._activity_detector._polling_thread

            assert thread1 is thread2, "Should reuse existing thread"

            # Cleanup
            tmux_service.stop_background_polling()

    def test_stop_background_polling_stops_thread(self, tmux_service):
        """stop_background_polling should signal thread to stop and join."""
        with patch.object(tmux_service, "_poll_all_panes"):
            tmux_service.start_background_polling()
            # Access thread through _activity_detector (Sprint 2 refactor)
            thread = tmux_service._activity_detector._polling_thread
            assert thread.is_alive()

            tmux_service.stop_background_polling()

            # Thread should stop within timeout
            time.sleep(0.5)
            assert not thread.is_alive()

    def test_stop_background_polling_when_not_running(self, tmux_service):
        """Stopping polling when not running should be safe."""
        # Should not raise exception
        tmux_service.stop_background_polling()

    def test_poll_all_panes_calls_get_pane_activity(self, tmux_service):
        """_poll_all_panes should call _get_pane_activity for all panes."""
        with patch.object(tmux_service, "get_teams") as mock_get_teams:
            with patch.object(tmux_service, "_get_roles_basic") as mock_get_roles:
                with patch.object(tmux_service, "_get_pane_activity") as mock_activity:
                    # Mock 2 teams with 2 panes each
                    mock_get_teams.return_value = [
                        {"id": "team1", "name": "team1"},
                        {"id": "team2", "name": "team2"},
                    ]
                    mock_get_roles.side_effect = [
                        [{"id": "pane-0", "_pane_index": "0"}, {"id": "pane-1", "_pane_index": "1"}],
                        [{"id": "pane-0", "_pane_index": "0"}, {"id": "pane-1", "_pane_index": "1"}],
                    ]

                    tmux_service._poll_all_panes()

                    # Should call _get_pane_activity 4 times (2 teams × 2 panes)
                    assert mock_activity.call_count == 4
                    # Verify calls
                    mock_activity.assert_any_call("team1", "0")
                    mock_activity.assert_any_call("team1", "1")
                    mock_activity.assert_any_call("team2", "0")
                    mock_activity.assert_any_call("team2", "1")

    def test_poll_loop_handles_errors_gracefully(self, tmux_service):
        """Background poll loop should handle errors without crashing."""
        poll_count = 0
        error_raised = False

        def mock_poll():
            nonlocal poll_count, error_raised
            poll_count += 1
            if poll_count == 1:
                error_raised = True
                raise Exception("Test error")
            # Let thread continue after error

        with patch.object(tmux_service, "_poll_all_panes", side_effect=mock_poll):
            # Set very short poll interval for testing (must be int)
            # Access through _activity_detector (Sprint 2 refactor)
            tmux_service._activity_detector.poll_interval = 1
            tmux_service.start_background_polling()

            # Wait for at least 2 polls
            time.sleep(2.5)

            tmux_service.stop_background_polling()

            # Should have called poll multiple times despite error
            assert poll_count >= 2, "Poll should continue after error"
            assert error_raised is True, "Error should have been raised"


# ============================================================
# MessageTracker Behavior Tests
# ============================================================


class TestMessageTracking:
    """Test message tracking behavior (will become MessageTracker class)."""

    def test_send_message_stores_message_and_timestamp(self, tmux_service):
        """send_message should store message and timestamp for highlight."""
        with patch.object(tmux_service, "_get_pane_index", return_value="0"):
            with patch.object(tmux_service, "_run_tmux", return_value=(True, "")):
                result = tmux_service.send_message("team1", "pane-0", "test message")

                assert result["success"] is True

                # Check message was stored (Sprint 2 refactor: access via _message_tracker)
                highlight_text = tmux_service._message_tracker.get_highlight_text("team1", "pane-0")
                assert highlight_text is not None
                assert "test message" in highlight_text
                assert "BOSS" in highlight_text

    def test_get_pane_state_includes_highlight_text(self, tmux_service):
        """get_pane_state should include highlightText from tracked messages."""
        with patch.object(tmux_service, "_get_pane_index", return_value="0"):
            with patch.object(tmux_service, "_run_tmux", return_value=(True, "output")):
                # Send a message first
                tmux_service.send_message("team1", "pane-0", "test command")

                # Get pane state
                state = tmux_service.get_pane_state("team1", "pane-0")

                assert state["highlightText"] is not None
                assert "BOSS" in state["highlightText"]
                assert "test command" in state["highlightText"]

    def test_get_pane_state_no_highlight_when_no_message_sent(self, tmux_service):
        """get_pane_state should have None highlightText when no message sent."""
        with patch.object(tmux_service, "_get_pane_index", return_value="0"):
            with patch.object(tmux_service, "_run_tmux", return_value=(True, "output")):
                state = tmux_service.get_pane_state("team1", "pane-0")

                assert state["highlightText"] is None

    def test_highlight_text_format(self, tmux_service):
        """Highlight text should follow format: BOSS [HH:MM]: message."""
        with patch.object(tmux_service, "_get_pane_index", return_value="0"):
            with patch.object(tmux_service, "_run_tmux", return_value=(True, "output")):
                # Sprint 2 refactor: mock datetime in message_tracker module
                with patch("app.services.message_tracker.datetime") as mock_dt:
                    # Mock timestamp
                    mock_dt.now.return_value.strftime.return_value = "14:30"

                    tmux_service.send_message("team1", "pane-0", "deploy now")
                    state = tmux_service.get_pane_state("team1", "pane-0")

                    assert state["highlightText"] == "BOSS [14:30]: deploy now"

    def test_message_tracking_per_pane(self, tmux_service):
        """Each pane should have separate message tracking."""
        with patch.object(tmux_service, "_get_pane_index") as mock_index:
            with patch.object(tmux_service, "_run_tmux", return_value=(True, "output")):
                # Send to pane-0
                mock_index.return_value = "0"
                tmux_service.send_message("team1", "pane-0", "message for pane 0")

                # Send to pane-1
                mock_index.return_value = "1"
                tmux_service.send_message("team1", "pane-1", "message for pane 1")

                # Check pane-0 state
                mock_index.return_value = "0"
                state0 = tmux_service.get_pane_state("team1", "pane-0")
                assert "message for pane 0" in state0["highlightText"]

                # Check pane-1 state
                mock_index.return_value = "1"
                state1 = tmux_service.get_pane_state("team1", "pane-1")
                assert "message for pane 1" in state1["highlightText"]

    def test_message_tracking_overwrite_on_new_message(self, tmux_service):
        """Sending new message should overwrite previous tracked message."""
        with patch.object(tmux_service, "_get_pane_index", return_value="0"):
            with patch.object(tmux_service, "_run_tmux", return_value=(True, "output")):
                # Send first message
                tmux_service.send_message("team1", "pane-0", "first message")

                # Send second message
                tmux_service.send_message("team1", "pane-0", "second message")

                # Check state - should have second message only
                state = tmux_service.get_pane_state("team1", "pane-0")
                assert "second message" in state["highlightText"]
                assert "first message" not in state["highlightText"]


# ============================================================
# TmuxRunner Behavior Tests (already tested in test_tmux_service.py)
# ============================================================


class TestTmuxRunner:
    """Test tmux command execution (will become TmuxRunner class).

    Note: TestRunTmux in test_tmux_service.py already covers this.
    Adding a few integration-style tests here for completeness.
    """

    def test_run_tmux_success_returns_output(self, tmux_service):
        """_run_tmux should return (True, output) on success."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="session1\nsession2",
            )

            success, output = tmux_service._run_tmux(["list-sessions"])

            assert success is True
            assert "session1" in output
            assert "session2" in output

    def test_run_tmux_constructs_command_correctly(self, tmux_service):
        """_run_tmux should prepend 'tmux' to args."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")

            tmux_service._run_tmux(["list-sessions", "-F", "#{session_name}"])

            # Verify subprocess.run was called with correct command
            call_args = mock_run.call_args[0][0]
            assert call_args[0] == "tmux"
            assert "list-sessions" in call_args
            assert "-F" in call_args

    def test_run_tmux_timeout_parameter(self, tmux_service):
        """_run_tmux should use 5 second timeout."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")

            tmux_service._run_tmux(["list-sessions"])

            # Verify timeout was set
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["timeout"] == 5
