"""Tests for restart team endpoints (Work Item 1)."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.auth_routes import get_current_user_from_token


client = TestClient(app)


# Mock user dict for auth bypass
mock_user_dict = {"id": 1, "email": "test@example.com", "username": "testuser", "is_active": True}


class TestRestartTeamEndpoints:
    """Tests for POST /api/teams/{team}/restart endpoint."""

    def test_restart_team_success(self):
        """Full team restart should succeed when team exists."""
        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user_dict

        try:
            with patch("app.services.team_lifecycle_manager.TeamLifecycleManager.restart_team") as mock_restart:
                mock_restart.return_value = {
                    "success": True,
                    "message": "Team 'command-center' restarted",
                    "setupScriptRun": True,
                }

                response = client.post(
                    "/api/teams/command-center/restart",
                    headers={"Authorization": "Bearer fake-token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["setupScriptRun"] is True
        finally:
            app.dependency_overrides.clear()

    def test_restart_team_not_found(self):
        """Restart should fail for non-existent team."""
        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user_dict

        try:
            with patch("app.services.team_lifecycle_manager.TeamLifecycleManager.restart_team") as mock_restart:
                mock_restart.return_value = {
                    "success": False,
                    "message": "Team not found: nonexistent",
                    "setupScriptRun": False,
                }

                response = client.post(
                    "/api/teams/nonexistent/restart",
                    headers={"Authorization": "Bearer fake-token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert "not found" in data["message"].lower()
        finally:
            app.dependency_overrides.clear()


class TestRestartRoleEndpoints:
    """Tests for POST /api/teams/{team}/roles/{role}/restart endpoint."""

    def test_restart_role_success(self):
        """Per-role restart should succeed when role exists."""
        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user_dict

        try:
            with patch("app.services.team_lifecycle_manager.TeamLifecycleManager.restart_role") as mock_restart:
                mock_restart.return_value = {
                    "success": True,
                    "role": "TL",
                    "pane_id": "%142",
                    "message": "Role 'TL' restarted successfully",
                }

                response = client.post(
                    "/api/teams/command-center/roles/TL/restart",
                    headers={"Authorization": "Bearer fake-token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["role"] == "TL"
                assert data["pane_id"] == "%142"
        finally:
            app.dependency_overrides.clear()

    def test_restart_role_invalid(self):
        """Restart should fail for invalid role."""
        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user_dict

        try:
            with patch("app.services.team_lifecycle_manager.TeamLifecycleManager.restart_role") as mock_restart:
                mock_restart.return_value = {
                    "success": False,
                    "message": "Role 'INVALID' not found in team 'command-center'",
                }

                response = client.post(
                    "/api/teams/command-center/roles/INVALID/restart",
                    headers={"Authorization": "Bearer fake-token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert "not found" in data["message"].lower()
        finally:
            app.dependency_overrides.clear()

    def test_restart_role_team_not_found(self):
        """Restart should fail when team doesn't exist."""
        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user_dict

        try:
            with patch("app.services.team_lifecycle_manager.TeamLifecycleManager.restart_role") as mock_restart:
                mock_restart.return_value = {
                    "success": False,
                    "message": "Team 'nonexistent' not found",
                }

                response = client.post(
                    "/api/teams/nonexistent/roles/TL/restart",
                    headers={"Authorization": "Bearer fake-token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert "not found" in data["message"].lower()
        finally:
            app.dependency_overrides.clear()
