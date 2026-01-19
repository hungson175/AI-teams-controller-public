# -*- coding: utf-8 -*-
"""Tests for TmuxService.

All subprocess calls are mocked - no actual tmux interaction.
"""

from unittest.mock import patch, MagicMock

import pytest

from app.services.tmux_service import TmuxService


class TestTmuxServiceInit:
    """Test TmuxService initialization."""

    def test_default_capture_lines(self):
        """Should use default capture lines."""
        service = TmuxService()
        assert service.capture_lines == 100

    def test_custom_capture_lines(self):
        """Should accept custom capture lines."""
        service = TmuxService(capture_lines=50)
        assert service.capture_lines == 50


class TestSetCaptureLines:
    """Test set_capture_lines method (Sprint 6 - DIP fix)."""

    def test_set_capture_lines_updates_attribute(self):
        """Should update capture_lines attribute via setter method."""
        service = TmuxService(capture_lines=100)
        service.set_capture_lines(200)
        assert service.capture_lines == 200

    def test_set_capture_lines_accepts_valid_range(self):
        """Should accept values in valid range (50-500)."""
        service = TmuxService()
        # Test boundary values
        service.set_capture_lines(50)
        assert service.capture_lines == 50

        service.set_capture_lines(500)
        assert service.capture_lines == 500

        # Test middle value
        service.set_capture_lines(250)
        assert service.capture_lines == 250


class TestRunTmux:
    """Test _run_tmux helper method."""

    def test_successful_command(self, tmux_service):
        """Should return (True, output) on success."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="success output"
            )
            success, output = tmux_service._run_tmux(["list-sessions"])

            assert success is True
            assert output == "success output"
            mock_run.assert_called_once()

    def test_failed_command(self, tmux_service):
        """Should return (False, output) on failure."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="error output"
            )
            success, output = tmux_service._run_tmux(["invalid-cmd"])

            assert success is False

    def test_timeout(self, tmux_service):
        """Should handle timeout gracefully."""
        import subprocess

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="tmux", timeout=5)
            success, output = tmux_service._run_tmux(["list-sessions"])

            assert success is False
            assert "timed out" in output.lower()

    def test_tmux_not_found(self, tmux_service):
        """Should handle missing tmux binary."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("tmux not found")
            success, output = tmux_service._run_tmux(["list-sessions"])

            assert success is False
            assert "not found" in output.lower()


class TestGetTeams:
    """Test get_teams method."""

    def test_returns_sessions(self, tmux_service, mock_tmux_sessions):
        """Should parse tmux sessions correctly."""
        with patch.object(
            tmux_service, "_run_tmux",
            return_value=(True, mock_tmux_sessions)
        ):
            with patch.object(tmux_service, "get_roles", return_value=[]):
                teams = tmux_service.get_teams()

                assert len(teams) == 3
                assert teams[0] == {"id": "session1", "name": "session1", "isActive": False}
                assert teams[1] == {"id": "session2", "name": "session2", "isActive": False}
                assert teams[2] == {"id": "session3", "name": "session3", "isActive": False}

    def test_empty_sessions(self, tmux_service):
        """Should return empty list when no sessions."""
        with patch.object(tmux_service, "_run_tmux", return_value=(True, "")):
            teams = tmux_service.get_teams()
            assert teams == []

    def test_tmux_failure(self, tmux_service):
        """Should return empty list on tmux failure."""
        with patch.object(tmux_service, "_run_tmux", return_value=(False, "error")):
            teams = tmux_service.get_teams()
            assert teams == []

    def test_team_isActive_all_idle(self, tmux_service):
        """Should set isActive=False when all panes are idle."""
        with patch.object(tmux_service, "_run_tmux", return_value=(True, "team1")):
            with patch.object(tmux_service, "get_roles") as mock_get_roles:
                # All roles idle
                mock_get_roles.return_value = [
                    {"id": "pane-0", "name": "PM", "order": 1, "isActive": False},
                    {"id": "pane-1", "name": "SA", "order": 2, "isActive": False},
                ]
                teams = tmux_service.get_teams()

                assert len(teams) == 1
                assert teams[0]["id"] == "team1"
                assert teams[0]["isActive"] is False

    def test_team_isActive_some_active(self, tmux_service):
        """Should set isActive=True when at least one pane is active."""
        with patch.object(tmux_service, "_run_tmux", return_value=(True, "team1")):
            with patch.object(tmux_service, "get_roles") as mock_get_roles:
                # One role active, others idle
                mock_get_roles.return_value = [
                    {"id": "pane-0", "name": "PM", "order": 1, "isActive": False},
                    {"id": "pane-1", "name": "SA", "order": 2, "isActive": True},  # ACTIVE
                    {"id": "pane-2", "name": "BE", "order": 3, "isActive": False},
                ]
                teams = tmux_service.get_teams()

                assert len(teams) == 1
                assert teams[0]["isActive"] is True

    def test_team_isActive_all_active(self, tmux_service):
        """Should set isActive=True when all panes are active."""
        with patch.object(tmux_service, "_run_tmux", return_value=(True, "team1")):
            with patch.object(tmux_service, "get_roles") as mock_get_roles:
                # All roles active
                mock_get_roles.return_value = [
                    {"id": "pane-0", "name": "PM", "order": 1, "isActive": True},
                    {"id": "pane-1", "name": "SA", "order": 2, "isActive": True},
                ]
                teams = tmux_service.get_teams()

                assert len(teams) == 1
                assert teams[0]["isActive"] is True

    def test_team_isActive_no_roles(self, tmux_service):
        """Should set isActive=False when team has no roles."""
        with patch.object(tmux_service, "_run_tmux", return_value=(True, "team1")):
            with patch.object(tmux_service, "get_roles", return_value=[]):
                teams = tmux_service.get_teams()

                assert len(teams) == 1
                assert teams[0]["isActive"] is False


class TestGetRoles:
    """Test get_roles method."""

    def test_returns_panes(self, tmux_service, mock_tmux_panes):
        """Should parse tmux panes correctly."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            # _get_roles_basic: has-session, list-panes, role names
            # Then _get_pane_activity for each pane: capture-pane
            mock_run.side_effect = [
                (True, ""),  # has-session
                (True, mock_tmux_panes),  # list-panes
                (True, "PM"),  # get pane 0 role name
                (True, "SA"),  # get pane 1 role name
                (True, "BE"),  # get pane 2 role name
                (True, "pane 0 content"),  # capture-pane for pane-0 (isActive)
                (True, "pane 1 content"),  # capture-pane for pane-1 (isActive)
                (True, "pane 2 content"),  # capture-pane for pane-2 (isActive)
            ]

            roles = tmux_service.get_roles("test-session")

            assert len(roles) == 3
            assert roles[0]["id"] == "pane-0"
            assert roles[0]["name"] == "PM"
            assert roles[0]["_pane_id"] == "%17"
            assert "isActive" in roles[0]  # Sprint 29: activity status
            assert roles[1]["id"] == "pane-1"
            assert roles[2]["id"] == "pane-2"

    def test_session_not_found(self, tmux_service):
        """Should return empty list if session doesn't exist."""
        with patch.object(tmux_service, "_run_tmux", return_value=(False, "")):
            roles = tmux_service.get_roles("nonexistent")
            assert roles == []

    def test_empty_panes(self, tmux_service):
        """Should return empty list when no panes."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session
                (True, ""),  # list-panes (empty)
            ]
            roles = tmux_service.get_roles("test-session")
            assert roles == []


class TestGetPaneTarget:
    """Test _get_pane_target method."""

    def test_direct_pane_id(self, tmux_service):
        """Should return pane_id directly if starts with %."""
        result = tmux_service._get_pane_target("team", "%17")
        assert result == "%17"

    def test_lookup_by_role_id(self, tmux_service, mock_tmux_panes):
        """Should look up pane_id from role_id."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session
                (True, mock_tmux_panes),  # list-panes
                (True, "PM"),  # role name lookup
                (True, "SA"),
                (True, "BE"),
            ]

            result = tmux_service._get_pane_target("team", "pane-1")
            assert result == "%18"

    def test_invalid_role_id(self, tmux_service):
        """Should return None for invalid role_id."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session
                (True, "0|%17|PM"),  # list-panes
                (True, "PM"),  # role name
            ]

            result = tmux_service._get_pane_target("team", "pane-99")
            assert result is None


class TestSendMessage:
    """Test send_message method (Sprint 6: delegated to PaneStateService)."""

    def test_successful_send(self, tmux_service):
        """Should delegate to PaneStateService.send_message."""
        with patch.object(
            tmux_service._pane_state_service, "send_message",
            return_value={"success": True, "message": "sent", "sentAt": "2024-01-01T00:00:00"}
        ) as mock_send:
            result = tmux_service.send_message("team", "pane-0", "test message")

            assert result["success"] is True
            mock_send.assert_called_once_with("team", "pane-0", "test message")

    def test_pane_not_found(self, tmux_service):
        """Should return error if pane not found."""
        with patch.object(
            tmux_service._pane_state_service, "send_message",
            return_value={"success": False, "message": "Pane not found", "sentAt": "2024-01-01T00:00:00"}
        ):
            result = tmux_service.send_message("team", "invalid", "test")

            assert result["success"] is False
            assert "not found" in result["message"].lower()

    def test_send_failure(self, tmux_service):
        """Should return error on send failure."""
        with patch.object(
            tmux_service._pane_state_service, "send_message",
            return_value={"success": False, "message": "Failed to send", "sentAt": "2024-01-01T00:00:00"}
        ):
            result = tmux_service.send_message("team", "pane-0", "test")

            assert result["success"] is False
            assert "failed" in result["message"].lower()


class TestGetPaneState:
    """Test get_pane_state method (Sprint 6: delegated to PaneStateService)."""

    def test_successful_capture(self, tmux_service):
        """Should delegate to PaneStateService.get_pane_state."""
        with patch.object(
            tmux_service._pane_state_service, "get_pane_state",
            return_value={"output": "pane content line 1\nline 2", "lastUpdated": "12:00:00", "highlightText": None, "isActive": False}
        ) as mock_get:
            result = tmux_service.get_pane_state("team", "pane-0")

            assert "pane content" in result["output"]
            assert "lastUpdated" in result
            mock_get.assert_called_once_with("team", "pane-0")

    def test_pane_not_found(self, tmux_service):
        """Should return error message if pane not found."""
        with patch.object(
            tmux_service._pane_state_service, "get_pane_state",
            return_value={"output": "Pane not found: invalid in team", "lastUpdated": "12:00:00", "highlightText": None, "isActive": False}
        ):
            result = tmux_service.get_pane_state("team", "invalid")

            assert "not found" in result["output"].lower()

    def test_capture_failure(self, tmux_service):
        """Should return error on capture failure."""
        with patch.object(
            tmux_service._pane_state_service, "get_pane_state",
            return_value={"output": "Failed to capture pane", "lastUpdated": "12:00:00", "highlightText": None, "isActive": False}
        ):
            result = tmux_service.get_pane_state("team", "pane-0")

            assert "failed" in result["output"].lower()

    def test_highlight_text_after_send(self, tmux_service):
        """Should include highlight text after sending message."""
        # PaneStateService handles this internally - just verify delegation works
        with patch.object(
            tmux_service._pane_state_service, "get_pane_state",
            return_value={"output": "content", "lastUpdated": "12:00:00", "highlightText": "test message", "isActive": False}
        ):
            result = tmux_service.get_pane_state("team", "pane-0")

            assert result["highlightText"] is not None
            assert "test message" in result["highlightText"]


# ============================================================
# Commander Epic: Team Lifecycle Management Tests
# ============================================================
# NOTE: Detailed lifecycle tests moved to test_team_lifecycle_manager.py
# (31 comprehensive tests for TeamLifecycleManager class - Sprint 3 extraction)
#
# TmuxService now uses facade pattern - delegates to TeamLifecycleManager.
# Public API tests (kill_team, restart_team, create_terminal, list_available_teams)
# are integration-tested via API endpoint tests in test_routes.py.
# ============================================================


# ============================================================
# Sprint 1 Story 2: ANSI Color Support Tests
# ============================================================


class TestAnsiColorCapture:
    """Test ANSI escape sequence capture (Sprint 1 Story 2).

    Sprint 6: ANSI handling now in PaneStateService.
    These tests verify TmuxService still provides ANSI support via delegation.
    """

    def test_get_pane_state_uses_escape_flag(self, tmux_service):
        """get_pane_state should delegate to PaneStateService which uses -e flag."""
        # This is now tested in test_pane_state_service.py
        # Here we just verify delegation works
        with patch.object(
            tmux_service._pane_state_service, "get_pane_state",
            return_value={"output": "test output", "lastUpdated": "12:00:00", "highlightText": None, "isActive": False}
        ) as mock_get:
            tmux_service.get_pane_state("team", "pane-0")
            mock_get.assert_called_once_with("team", "pane-0")

    def test_get_pane_activity_uses_escape_flag(self, tmux_service):
        """_get_pane_activity should use -e flag to capture ANSI sequences."""
        with patch.object(tmux_service, "_run_tmux") as mock_run:
            mock_run.return_value = (True, "test output")

            tmux_service._get_pane_activity("team", "0")

            # Verify capture-pane was called with -e flag
            call_args = mock_run.call_args[0][0]
            assert "capture-pane" in call_args
            assert "-e" in call_args, "capture-pane must include -e flag for ANSI sequences"

    def test_ansi_sequences_preserved_in_output(self, tmux_service):
        """ANSI escape sequences should be preserved in output."""
        # Sample ANSI output: bold text, green text, reset
        ansi_output = "\x1b[1mBold\x1b[0m and \x1b[32mgreen\x1b[0m text"

        with patch.object(
            tmux_service._pane_state_service, "get_pane_state",
            return_value={"output": ansi_output, "lastUpdated": "12:00:00", "highlightText": None, "isActive": False}
        ):
            result = tmux_service.get_pane_state("team", "pane-0")

            # ANSI sequences should be in the output, not stripped
            assert "\x1b[1m" in result["output"], "Bold escape sequence should be preserved"
            assert "\x1b[32m" in result["output"], "Green color escape sequence should be preserved"
            assert "\x1b[0m" in result["output"], "Reset escape sequence should be preserved"

    def test_24bit_rgb_colors_preserved(self, tmux_service):
        """24-bit RGB ANSI colors should be preserved."""
        # 24-bit RGB: \x1b[38;2;R;G;Bm for foreground
        rgb_output = "\x1b[38;2;255;128;0mOrange text\x1b[0m"

        with patch.object(
            tmux_service._pane_state_service, "get_pane_state",
            return_value={"output": rgb_output, "lastUpdated": "12:00:00", "highlightText": None, "isActive": False}
        ):
            result = tmux_service.get_pane_state("team", "pane-0")

            assert "\x1b[38;2;255;128;0m" in result["output"], "RGB color should be preserved"
