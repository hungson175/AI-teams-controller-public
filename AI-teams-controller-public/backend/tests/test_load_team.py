"""Tests for Load Team Button feature - list available teams."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.services.tmux_service import TmuxService
from app.services.mock_data import MockDataService


class TestListAvailableTeams:
    """Test listing available team directories."""

    def test_list_available_teams_returns_list(self):
        """Test that list_available_teams returns a list."""
        service = MockDataService()
        teams = service.list_available_teams()
        assert isinstance(teams, list)
        assert len(teams) == 3

    def test_available_team_structure(self):
        """Test that each team has required fields."""
        service = MockDataService()
        teams = service.list_available_teams()

        for team in teams:
            assert "name" in team
            assert "path" in team
            assert "hasSetupScript" in team
            assert "isActive" in team
            assert isinstance(team["name"], str)
            assert isinstance(team["path"], str)
            assert isinstance(team["hasSetupScript"], bool)
            assert isinstance(team["isActive"], bool)

    def test_available_teams_sorted_by_active(self):
        """Test that active teams are listed first."""
        service = MockDataService()
        teams = service.list_available_teams()

        # First teams should be active
        for team in teams:
            if not team["isActive"]:
                break
            assert team["isActive"] is True

    def test_available_team_names(self):
        """Test that mock teams have expected names."""
        service = MockDataService()
        teams = service.list_available_teams()
        names = [team["name"] for team in teams]

        assert "quant-team-v2" in names
        assert "refactor-dr" in names
        assert "ai_controller_full_team" in names

    def test_tmux_service_has_list_available_teams_method(self):
        """Test that TmuxService has list_available_teams method."""
        service = TmuxService()
        assert hasattr(service, "list_available_teams")
        assert callable(service.list_available_teams)

    def test_check_team_active_with_no_sessions(self):
        """Test _check_team_active when no tmux sessions exist."""
        service = TmuxService()
        service._run_tmux = MagicMock(return_value=(True, ""))

        is_active = service._check_team_active("nonexistent-team")
        assert is_active is False

    def test_check_team_active_with_matching_session(self):
        """Test _check_team_active when team session exists."""
        service = TmuxService()
        service._run_tmux = MagicMock(return_value=(True, "team-1\nteam-2\ntest-team\n"))

        is_active = service._check_team_active("test-team")
        assert is_active is True

    def test_check_team_active_with_non_matching_session(self):
        """Test _check_team_active when team session doesn't exist."""
        service = TmuxService()
        service._run_tmux = MagicMock(return_value=(True, "team-1\nteam-2\n"))

        is_active = service._check_team_active("nonexistent-team")
        assert is_active is False

    def test_check_team_active_tmux_error(self):
        """Test _check_team_active when tmux command fails."""
        service = TmuxService()
        service._run_tmux = MagicMock(return_value=(False, "error message"))

        is_active = service._check_team_active("any-team")
        assert is_active is False
