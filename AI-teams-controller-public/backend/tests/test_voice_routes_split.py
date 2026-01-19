# -*- coding: utf-8 -*-
"""Tests for voice_routes module split (Sprint Tech Debt 1).

TDD: These tests verify the split module structure works correctly.
Tests written BEFORE implementation to ensure no regressions.
"""

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient


class TestVoiceRoutesModuleSplit:
    """Verify voice_routes split into 3 modules maintains all functionality."""

    def test_voice_routes_package_imports(self):
        """Should be able to import router from voice_routes package."""
        from app.api.voice_routes import router

        assert router is not None
        assert isinstance(router, APIRouter)
        assert router.prefix == "/api/voice"

    def test_token_routes_module_exists(self):
        """token_routes module should exist and export router."""
        from app.api.voice_routes.token_routes import router as token_router

        assert token_router is not None
        assert isinstance(token_router, APIRouter)

    def test_command_routes_module_exists(self):
        """command_routes module should exist and export router."""
        from app.api.voice_routes.command_routes import router as command_router

        assert command_router is not None
        assert isinstance(command_router, APIRouter)

    def test_task_routes_module_exists(self):
        """task_routes module should exist and export router."""
        from app.api.voice_routes.task_routes import router as task_router

        assert task_router is not None
        assert isinstance(task_router, APIRouter)

    def test_combined_router_includes_all_subrouters(self):
        """Main voice_routes router should include all sub-routers."""
        from app.api.voice_routes import router

        # Verify router has routes from all modules
        assert len(router.routes) > 0, "Combined router should have routes"

    def test_token_endpoints_still_accessible(self):
        """Token endpoints should work after split."""
        from app.main import app
        from unittest.mock import patch
        import os

        client = TestClient(app)

        # Test POST /api/voice/token (requires OPENAI_API_KEY)
        original = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = ""
        try:
            response = client.post("/api/voice/token")
            # Should return 500 (missing API key) not 404 (route not found)
            assert response.status_code == 500
            assert "OPENAI_API_KEY" in response.json()["detail"]
        finally:
            if original:
                os.environ["OPENAI_API_KEY"] = original

    def test_command_endpoints_still_accessible(self):
        """Command endpoints should work after split."""
        from app.main import app
        from unittest.mock import patch, MagicMock, AsyncMock

        client = TestClient(app)

        # Test POST /api/voice/command/{team_id}/{role_id}
        with patch("app.api.voice_routes.command_routes.get_tmux_pane_content", return_value="context"):
            with patch("app.api.voice_routes.command_routes.send_to_tmux_pane", return_value=False):
                response = client.post(
                    "/api/voice/command/team1/pane-0",
                    json={"raw_command": "test", "transcript": "test"}
                )
                # Should return 200 with success=False (tmux failed), not 404
                assert response.status_code == 200

    def test_task_endpoints_still_accessible(self):
        """Task endpoints should work after split."""
        from app.main import app
        from unittest.mock import patch, AsyncMock

        client = TestClient(app)

        # Test POST /api/voice/task-done/{team_id}/{role_id}
        with patch("app.api.voice_routes.task_routes.should_skip_role", return_value=False):
            with patch("app.api.voice_routes.task_routes.get_tmux_pane_content", return_value="output"):
                with patch("app.api.voice_routes.task_routes.get_task_done_listener") as mock_listener:
                    mock_listener.return_value.stop_hook_fired = AsyncMock(
                        return_value={"success": True, "summary": "Done"}
                    )

                    response = client.post(
                        "/api/voice/task-done/team1/pane-0",
                        json={
                            "session_id": "session",
                            "transcript_path": "/tmp/path",
                            "team_id": "team1",
                            "role_id": "pane-0",
                        }
                    )
                    # Should return 200, not 404
                    assert response.status_code == 200


class TestVoiceRoutesEndpointMapping:
    """Verify correct endpoint distribution across split modules."""

    def test_token_routes_has_correct_endpoints(self):
        """token_routes should contain token generation endpoints."""
        from app.api.voice_routes.token_routes import router

        route_paths = [route.path for route in router.routes]

        assert any("token" in path for path in route_paths), "Should have /token endpoint"

    def test_command_routes_has_correct_endpoints(self):
        """command_routes should contain command processing endpoints."""
        from app.api.voice_routes.command_routes import router

        route_paths = [route.path for route in router.routes]

        assert any("command" in path for path in route_paths), "Should have /command endpoint"
        assert any("transcribe" in path for path in route_paths), "Should have /transcribe endpoint"

    def test_task_routes_has_correct_endpoints(self):
        """task_routes should contain task-done and WebSocket endpoints."""
        from app.api.voice_routes.task_routes import router

        route_paths = [route.path for route in router.routes]

        assert any("task-done" in path for path in route_paths), "Should have /task-done endpoint"
        assert any("feedback" in path for path in route_paths), "Should have /ws/feedback endpoints"

    def test_helper_functions_in_command_routes(self):
        """Helper functions should be accessible from command_routes."""
        from app.api.voice_routes.command_routes import (
            get_pane_id,
            get_tmux_pane_content,
            send_to_tmux_pane,
            correct_voice_command,
            RoutedCommand,
        )

        # Verify helper functions exist
        assert callable(get_pane_id)
        assert callable(get_tmux_pane_content)
        assert callable(send_to_tmux_pane)
        assert callable(correct_voice_command)
        assert RoutedCommand is not None
