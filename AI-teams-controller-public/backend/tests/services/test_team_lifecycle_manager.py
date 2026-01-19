# -*- coding: utf-8 -*-
"""Characterization tests for Team Lifecycle methods in TmuxService.

Sprint 3 Tech Debt - BE-1: TeamLifecycleManager Extraction
These tests establish baseline behavior BEFORE extracting lifecycle methods.
All tests should pass with current TmuxService implementation.

Methods under test:
- kill_team()
- restart_team()
- create_terminal()
- list_available_teams()
- _find_setup_script()
- _validate_team_exists()
- _check_team_active()
"""

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest

from app.services.tmux_service import TmuxService


@pytest.fixture
def tmux_service():
    """Fixture for TmuxService instance."""
    return TmuxService()


@pytest.fixture
def lifecycle_manager():
    """Fixture for TeamLifecycleManager instance (Sprint 3 extraction)."""
    from app.services.team_lifecycle_manager import TeamLifecycleManager
    return TeamLifecycleManager()


# ========== Tests for _validate_team_exists() ==========


class TestValidateTeamExists:
    """Test _validate_team_exists() method."""

    def test_validate_team_exists_returns_true_when_session_exists(self, lifecycle_manager):
        """When tmux has-session succeeds, should return True."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.return_value = (True, "")

            result = lifecycle_manager._validate_team_exists("test-team")

            assert result is True
            mock_run.assert_called_once_with(["has-session", "-t", "test-team"])

    def test_validate_team_exists_returns_false_when_session_missing(self, lifecycle_manager):
        """When tmux has-session fails, should return False."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.return_value = (False, "session not found")

            result = lifecycle_manager._validate_team_exists("missing-team")

            assert result is False


# ========== Tests for kill_team() ==========


class TestKillTeam:
    """Test kill_team() method."""

    def test_kill_team_success(self, lifecycle_manager):
        """Successful team kill should return success response."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            # Mock has-session (validate) and kill-session
            mock_run.side_effect = [
                (True, ""),  # has-session succeeds
                (True, ""),  # kill-session succeeds
            ]

            result = lifecycle_manager.kill_team("test-team")

            assert result["success"] is True
            assert "terminated" in result["message"].lower()
            assert mock_run.call_count == 2

    def test_kill_team_not_found(self, lifecycle_manager):
        """Killing non-existent team should return error."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.return_value = (False, "session not found")

            result = lifecycle_manager.kill_team("missing-team")

            assert result["success"] is False
            assert "not found" in result["message"].lower()

    def test_kill_team_command_fails(self, lifecycle_manager):
        """When kill-session fails, should return error."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session succeeds
                (False, "permission denied"),  # kill-session fails
            ]

            result = lifecycle_manager.kill_team("test-team")

            assert result["success"] is False
            assert "failed" in result["message"].lower()


# ========== Tests for create_terminal() ==========


class TestCreateTerminal:
    """Test create_terminal() method."""

    def test_create_terminal_success_with_name(self, lifecycle_manager):
        """Creating terminal with custom name should succeed."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            with patch("os.path.isdir", return_value=True):
                with patch("os.path.expanduser", side_effect=lambda x: x.replace("~", "/home/user")):
                    mock_run.side_effect = [
                        (False, ""),  # has-session fails (doesn't exist)
                        (True, ""),   # new-session succeeds
                    ]

                    result = lifecycle_manager.create_terminal(name="my-terminal", directory="~/dev")

                    assert result["success"] is True
                    assert result["teamId"] == "my-terminal"
                    assert "created" in result["message"].lower()

    def test_create_terminal_auto_generates_name(self, lifecycle_manager):
        """Creating terminal without name should auto-generate."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            with patch("os.path.isdir", return_value=True):
                with patch("os.path.expanduser", return_value="/home/user"):
                    mock_run.side_effect = [
                        (False, ""),  # has-session fails
                        (True, ""),   # new-session succeeds
                    ]

                    result = lifecycle_manager.create_terminal()

                    assert result["success"] is True
                    assert result["teamId"].startswith("terminal-")

    def test_create_terminal_sanitizes_name(self, lifecycle_manager):
        """Terminal name should be sanitized (only alphanumeric, hyphens, underscores)."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            with patch("os.path.isdir", return_value=True):
                with patch("os.path.expanduser", return_value="/home/user"):
                    mock_run.side_effect = [
                        (False, ""),
                        (True, ""),
                    ]

                    result = lifecycle_manager.create_terminal(name="my@terminal#123!")

                    # Should remove special characters
                    assert "@" not in result["teamId"]
                    assert "#" not in result["teamId"]
                    assert "!" not in result["teamId"]

    def test_create_terminal_rejects_invalid_name(self, lifecycle_manager):
        """Terminal name with only special characters should fail."""
        result = lifecycle_manager.create_terminal(name="@#$%")

        assert result["success"] is False
        assert "invalid" in result["message"].lower()

    def test_create_terminal_rejects_duplicate_name(self, lifecycle_manager):
        """Creating terminal with existing name should fail."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.return_value = (True, "")  # has-session succeeds

            result = lifecycle_manager.create_terminal(name="existing-terminal")

            assert result["success"] is False
            assert "already exists" in result["message"].lower()

    def test_create_terminal_rejects_nonexistent_directory(self, lifecycle_manager):
        """Creating terminal in non-existent directory should fail."""
        with patch("os.path.isdir", return_value=False):
            with patch("os.path.expanduser", return_value="/nonexistent/path"):
                result = lifecycle_manager.create_terminal(directory="/nonexistent/path")

                assert result["success"] is False
                assert "does not exist" in result["message"].lower()

    def test_create_terminal_command_fails(self, lifecycle_manager):
        """When new-session fails, should return error."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            with patch("os.path.isdir", return_value=True):
                with patch("os.path.expanduser", return_value="/home/user"):
                    mock_run.side_effect = [
                        (False, ""),  # has-session fails
                        (False, "tmux server not running"),  # new-session fails
                    ]

                    result = lifecycle_manager.create_terminal()

                    assert result["success"] is False
                    assert "failed" in result["message"].lower()


# ========== Tests for _check_team_active() ==========


class TestCheckTeamActive:
    """Test _check_team_active() method."""

    def test_check_team_active_returns_true_when_session_running(self, lifecycle_manager):
        """When team is in active sessions list, should return True."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.return_value = (True, "team1\nteam2\ntest-team\nteam3")

            result = lifecycle_manager._check_team_active("test-team")

            assert result is True

    def test_check_team_active_returns_false_when_session_not_running(self, lifecycle_manager):
        """When team is not in active sessions, should return False."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.return_value = (True, "team1\nteam2\nteam3")

            result = lifecycle_manager._check_team_active("missing-team")

            assert result is False

    def test_check_team_active_returns_false_when_command_fails(self, lifecycle_manager):
        """When list-sessions fails, should return False."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.return_value = (False, "no server running")

            result = lifecycle_manager._check_team_active("test-team")

            assert result is False

    def test_check_team_active_handles_empty_output(self, lifecycle_manager):
        """When no sessions exist, should handle empty output."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.return_value = (True, "")

            result = lifecycle_manager._check_team_active("test-team")

            assert result is False


# ========== Tests for _find_setup_script() ==========


class TestFindSetupScript:
    """Test _find_setup_script() method."""

    def test_find_setup_script_success(self, lifecycle_manager):
        """When setup-team.sh exists and is in README, should return path."""
        readme_content = """
        # Team Setup

        Run the setup script:
        ```bash
        ./setup-team.sh
        ```
        """
        with patch("os.path.exists") as mock_exists:
            with patch("builtins.open", mock_open(read_data=readme_content)):
                mock_exists.side_effect = lambda p: True  # All paths exist

                result = lifecycle_manager._find_setup_script("/path/to/README.md")

                assert result is not None
                assert "setup-team.sh" in result

    def test_find_setup_script_returns_none_when_readme_missing(self, lifecycle_manager):
        """When README doesn't exist, should return None."""
        with patch("os.path.exists", return_value=False):
            result = lifecycle_manager._find_setup_script("/nonexistent/README.md")

            assert result is None

    def test_find_setup_script_returns_none_when_script_not_in_readme(self, lifecycle_manager):
        """When README doesn't mention setup script, should return None."""
        readme_content = "# Team Docs\n\nNo setup script here."
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=readme_content)):
                result = lifecycle_manager._find_setup_script("/path/to/README.md")

                assert result is None

    def test_find_setup_script_returns_none_when_script_file_missing(self, lifecycle_manager):
        """When script mentioned in README but file doesn't exist, should return None."""
        readme_content = "Run: ./setup-team.sh"
        with patch("os.path.exists") as mock_exists:
            with patch("builtins.open", mock_open(read_data=readme_content)):
                # README exists, but script file doesn't
                mock_exists.side_effect = lambda p: "README" in p

                result = lifecycle_manager._find_setup_script("/path/to/README.md")

                assert result is None

    def test_find_setup_script_handles_read_error(self, lifecycle_manager):
        """When README read fails, should return None."""
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", side_effect=IOError("permission denied")):
                result = lifecycle_manager._find_setup_script("/path/to/README.md")

                assert result is None


# ========== Tests for restart_team() ==========


class TestRestartTeam:
    """Test restart_team() method."""

    def test_restart_team_not_found(self, lifecycle_manager):
        """Restarting non-existent team should return error."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.return_value = (False, "session not found")

            result = lifecycle_manager.restart_team("missing-team")

            assert result["success"] is False
            assert "not found" in result["message"].lower()
            assert result["setupScriptRun"] is False

    def test_restart_team_kill_fails(self, lifecycle_manager):
        """When kill fails during restart, should return error."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session succeeds
                (False, "permission denied"),  # kill-session fails
            ]

            result = lifecycle_manager.restart_team("test-team")

            assert result["success"] is False
            assert "failed to kill" in result["message"].lower()
            assert result["setupScriptRun"] is False

    def test_restart_team_no_readme(self, lifecycle_manager):
        """When README doesn't exist, should kill but not run script."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            with patch("os.path.exists", return_value=False):
                mock_run.side_effect = [
                    (True, ""),  # has-session
                    (True, ""),  # kill-session
                ]

                result = lifecycle_manager.restart_team("test-team")

                assert result["success"] is True
                assert "no README" in result["message"]
                assert result["setupScriptRun"] is False

    def test_restart_team_no_setup_script_in_readme(self, lifecycle_manager):
        """When README exists but no setup script, should kill but not run."""
        readme_content = "# Team\n\nNo setup here."
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            with patch("os.path.exists", return_value=True):
                with patch("builtins.open", mock_open(read_data=readme_content)):
                    mock_run.side_effect = [(True, ""), (True, "")]

                    result = lifecycle_manager.restart_team("test-team")

                    assert result["success"] is True
                    assert "no setup script" in result["message"].lower()
                    assert result["setupScriptRun"] is False

    def test_restart_team_setup_script_success(self, lifecycle_manager):
        """When setup script runs successfully, should return success."""
        readme_content = "Run: ./setup-team.sh"
        mock_subprocess_result = Mock()
        mock_subprocess_result.returncode = 0
        mock_subprocess_result.stdout = "Setup complete"
        mock_subprocess_result.stderr = ""

        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            with patch("os.path.exists", return_value=True):
                with patch("builtins.open", mock_open(read_data=readme_content)):
                    with patch("subprocess.run", return_value=mock_subprocess_result):
                        mock_run.side_effect = [(True, ""), (True, "")]

                        result = lifecycle_manager.restart_team("test-team")

                        assert result["success"] is True
                        assert "restarted successfully" in result["message"]
                        assert result["setupScriptRun"] is True

    def test_restart_team_setup_script_fails(self, lifecycle_manager):
        """When setup script fails, should return error."""
        readme_content = "Run: ./setup-team.sh"
        mock_subprocess_result = Mock()
        mock_subprocess_result.returncode = 1
        mock_subprocess_result.stdout = ""
        mock_subprocess_result.stderr = "Setup failed: permission error"

        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            with patch("os.path.exists", return_value=True):
                with patch("builtins.open", mock_open(read_data=readme_content)):
                    with patch("subprocess.run", return_value=mock_subprocess_result):
                        mock_run.side_effect = [(True, ""), (True, "")]

                        result = lifecycle_manager.restart_team("test-team")

                        assert result["success"] is False
                        assert "setup script failed" in result["message"].lower()
                        assert result["setupScriptRun"] is True

    def test_restart_team_setup_script_timeout(self, lifecycle_manager):
        """When setup script times out, should return error."""
        readme_content = "Run: ./setup-team.sh"

        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            with patch("os.path.exists", return_value=True):
                with patch("builtins.open", mock_open(read_data=readme_content)):
                    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("bash", 60)):
                        mock_run.side_effect = [(True, ""), (True, "")]

                        result = lifecycle_manager.restart_team("test-team")

                        assert result["success"] is False
                        assert "timed out" in result["message"].lower()
                        assert result["setupScriptRun"] is True


# ========== Tests for list_available_teams() ==========


class TestListAvailableTeams:
    """Test list_available_teams() method."""

    def test_list_available_teams_returns_empty_when_no_docs_dir(self, lifecycle_manager):
        """When docs/tmux doesn't exist, should return empty list."""
        with patch("pathlib.Path.exists", return_value=False):
            result = lifecycle_manager.list_available_teams()

            assert result == []

    def test_list_available_teams_returns_teams_with_metadata(self, lifecycle_manager):
        """Should return list of teams with setup script and active status."""
        # Mock directory structure with proper __lt__ for sorting
        mock_team1 = Mock()
        mock_team1.name = "team1"
        mock_team1.is_dir.return_value = True
        mock_team1.relative_to.return_value = Path("docs/tmux/team1")
        mock_team1.__truediv__ = lambda self, other: Mock(exists=Mock(return_value=True))
        mock_team1.__lt__ = lambda self, other: self.name < other.name

        mock_team2 = Mock()
        mock_team2.name = "team2"
        mock_team2.is_dir.return_value = True
        mock_team2.relative_to.return_value = Path("docs/tmux/team2")
        mock_team2.__truediv__ = lambda self, other: Mock(exists=Mock(return_value=False))
        mock_team2.__lt__ = lambda self, other: self.name < other.name

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.iterdir", return_value=[mock_team1, mock_team2]):
                with patch.object(lifecycle_manager, "_check_team_active") as mock_check:
                    mock_check.side_effect = [True, False]  # team1 active, team2 not

                    result = lifecycle_manager.list_available_teams()

                    assert len(result) == 2
                    # Active team should be first
                    assert result[0]["name"] == "team1"
                    assert result[0]["isActive"] is True
                    assert result[0]["hasSetupScript"] is True
                    assert result[1]["name"] == "team2"
                    assert result[1]["isActive"] is False

    def test_list_available_teams_skips_files(self, lifecycle_manager):
        """Should skip files and only include directories."""
        mock_dir = Mock()
        mock_dir.name = "team1"
        mock_dir.is_dir.return_value = True
        mock_dir.relative_to.return_value = Path("docs/tmux/team1")
        mock_dir.__truediv__ = lambda self, other: Mock(exists=Mock(return_value=False))
        mock_dir.__lt__ = lambda self, other: True  # Simple comparison for single item

        mock_file = Mock()
        mock_file.is_dir.return_value = False
        mock_file.__lt__ = lambda self, other: False

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.iterdir", return_value=[mock_dir, mock_file]):
                with patch.object(lifecycle_manager, "_check_team_active", return_value=False):
                    result = lifecycle_manager.list_available_teams()

                    assert len(result) == 1
                    assert result[0]["name"] == "team1"


# ========== Tests for restart_role() ==========


class TestRestartRole:
    """Test restart_role() method."""

    def test_restart_role_team_not_found(self, lifecycle_manager):
        """Restarting role in non-existent team should return error."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.return_value = (False, "session not found")

            result = lifecycle_manager.restart_role("missing-team", "TL")

            assert result["success"] is False
            assert "not found" in result["message"].lower()

    def test_restart_role_list_panes_fails(self, lifecycle_manager):
        """When list-panes fails, should return error."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session succeeds
                (False, "permission denied"),  # list-panes fails
            ]

            result = lifecycle_manager.restart_role("test-team", "TL")

            assert result["success"] is False
            assert "failed to list panes" in result["message"].lower()

    def test_restart_role_role_not_found(self, lifecycle_manager):
        """When role doesn't exist in team, should return error."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session succeeds
                (True, "%1 PO\n%2 SM\n%3 FE"),  # list-panes output (no TL)
            ]

            result = lifecycle_manager.restart_role("test-team", "TL")

            assert result["success"] is False
            assert "not found" in result["message"].lower()

    def test_restart_role_success(self, lifecycle_manager):
        """Successful role restart should return success with pane_id."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session succeeds
                (True, "%1 PO\n%2 TL\n%3 FE"),  # list-panes output
                (True, ""),  # send-keys Ctrl+C
                (True, ""),  # send-keys claude command
                (True, ""),  # send-keys /init-role
            ]

            result = lifecycle_manager.restart_role("test-team", "TL")

            assert result["success"] is True
            assert result["role"] == "TL"
            assert result["pane_id"] == "%2"
            assert "restarted successfully" in result["message"].lower()
            # Verify model mapping (TL = opus)
            assert mock_run.call_count == 5

    def test_restart_role_model_mapping_sm(self, lifecycle_manager):
        """SM role should use opus model."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session
                (True, "%1 SM"),  # list-panes
                (True, ""),  # Ctrl+C
                (True, ""),  # claude command
                (True, ""),  # /init-role
            ]

            lifecycle_manager.restart_role("test-team", "SM")

            # Check that claude --model opus was sent
            calls = mock_run.call_args_list
            claude_call = calls[3][0][0]
            assert "claude --model opus" in claude_call

    def test_restart_role_model_mapping_qa(self, lifecycle_manager):
        """QA role should use haiku model."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session
                (True, "%5 QA"),  # list-panes
                (True, ""),  # Ctrl+C
                (True, ""),  # claude command
                (True, ""),  # /init-role
            ]

            lifecycle_manager.restart_role("test-team", "QA")

            # Check that claude --model haiku was sent
            calls = mock_run.call_args_list
            claude_call = calls[3][0][0]
            assert "claude --model haiku" in claude_call

    def test_restart_role_model_mapping_be(self, lifecycle_manager):
        """BE role should use sonnet model (default)."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session
                (True, "%4 BE"),  # list-panes
                (True, ""),  # Ctrl+C
                (True, ""),  # claude command
                (True, ""),  # /init-role
            ]

            lifecycle_manager.restart_role("test-team", "BE")

            # Check that claude --model sonnet was sent
            calls = mock_run.call_args_list
            claude_call = calls[3][0][0]
            assert "claude --model sonnet" in claude_call

    def test_restart_role_unknown_role_uses_sonnet(self, lifecycle_manager):
        """Unknown role should default to sonnet model."""
        with patch("app.services.tmux_runner.TmuxRunner.run") as mock_run:
            mock_run.side_effect = [
                (True, ""),  # has-session
                (True, "%9 UNKNOWN"),  # list-panes
                (True, ""),  # Ctrl+C
                (True, ""),  # claude command
                (True, ""),  # /init-role
            ]

            lifecycle_manager.restart_role("test-team", "UNKNOWN")

            # Check that claude --model sonnet was sent (default)
            calls = mock_run.call_args_list
            claude_call = calls[3][0][0]
            assert "claude --model sonnet" in claude_call
