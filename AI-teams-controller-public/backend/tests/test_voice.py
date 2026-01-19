# -*- coding: utf-8 -*-
"""Tests for voice command REST API.

TDD approach - tests written before full implementation.
Phase 2: Mock tests (no LLM cost)
Phase 3: Non-LLM tests (local only)
Phase 4: LLM tests (require Boss approval)

NOTE: Most endpoint tests moved to test_voice_routes.py for proper auth handling.
This file contains non-endpoint tests and LLM integration tests.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.auth_routes import SESSION_TOKEN


client = TestClient(app, headers={"Authorization": f"Bearer {SESSION_TOKEN}"})


# ============================================================
# Phase 2: Mock Tests (No API Calls)
# ============================================================


class TestVoiceTokenEndpoint:
    """Tests for POST /api/voice/token."""

    def test_token_endpoint_exists(self):
        """Verify endpoint exists and accepts POST."""
        # Without OPENAI_API_KEY, should return 500
        response = client.post("/api/voice/token")
        # Either 500 (no key) or 200 (with key) - not 404
        assert response.status_code != 404

    def test_token_without_api_key(self):
        """Should return 500 when OPENAI_API_KEY not set."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            with patch("app.api.voice_routes.os.environ.get", return_value=None):
                response = client.post("/api/voice/token")
                assert response.status_code == 500
                assert "OPENAI_API_KEY" in response.json()["detail"]

    def test_token_with_mocked_openai(self):
        """Should return token when OpenAI API mocked."""
        import httpx
        from unittest.mock import AsyncMock

        mock_response_data = {
            "client_secret": {
                "value": "ek_test_123",
                "expires_at": 1234567890,
            },
            "model": "gpt-4o-realtime-preview",
            "modalities": ["text", "audio"],
        }

        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        # Create async mock for client.post
        mock_post = AsyncMock(return_value=mock_response)

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.post = mock_post
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_class.return_value = mock_client

                response = client.post("/api/voice/token")
                assert response.status_code == 200
                data = response.json()
                assert "client_secret" in data
                assert data["client_secret"]["value"] == "ek_test_123"


class TestVoiceCommandEndpoint:
    """Tests for POST /api/voice/command/{team_id}/{role_id}."""

    def test_command_endpoint_exists(self):
        """Verify endpoint exists and accepts POST with body."""
        response = client.post(
            "/api/voice/command/test-team/0",
            json={"raw_command": "test go go", "transcript": "test"},
        )
        # Should not be 404
        assert response.status_code != 404

    def test_command_request_validation(self):
        """Should validate request body."""
        # Missing required fields
        response = client.post("/api/voice/command/test-team/0", json={})
        assert response.status_code == 422  # Validation error

        # Valid body structure
        response = client.post(
            "/api/voice/command/test-team/0",
            json={"raw_command": "test go go", "transcript": "test"},
        )
        # Not a validation error
        assert response.status_code != 422

    def test_command_with_mocked_llm_and_tmux(self):
        """Should process command with mocked LLM and tmux."""
        from app.api.voice_routes import RoutedCommand

        mock_result = RoutedCommand(corrected_command="corrected test", is_backlog_task=False)
        with patch(
            "app.api.voice_routes.correct_voice_command", return_value=mock_result
        ):
            with patch("app.api.voice_routes.send_to_tmux_pane", return_value=True):
                with patch(
                    "app.api.voice_routes.get_tmux_pane_content",
                    return_value="mock context",
                ):
                    response = client.post(
                        "/api/voice/command/test-team/0",
                        json={"raw_command": "test go go", "transcript": "test"},
                    )
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True
                    assert data["corrected_command"] == "corrected test"

    def test_command_tmux_failure(self):
        """Should report error when tmux send fails."""
        from app.api.voice_routes import RoutedCommand

        mock_result = RoutedCommand(corrected_command="corrected test", is_backlog_task=False)
        with patch(
            "app.api.voice_routes.correct_voice_command",
            return_value=mock_result,
        ):
            with patch("app.api.voice_routes.send_to_tmux_pane", return_value=False):
                with patch(
                    "app.api.voice_routes.get_tmux_pane_content",
                    return_value="mock context",
                ):
                    response = client.post(
                        "/api/voice/command/test-team/0",
                        json={"raw_command": "test go go", "transcript": "test"},
                    )
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is False
                    assert "tmux" in data["error"].lower()


# ============================================================
# Phase 3: Non-LLM Tests (Local Only)
# ============================================================


class TestTmuxIntegration:
    """Tests for tmux helper functions (no API cost)."""

    def test_get_tmux_pane_content_no_tmux(self):
        """Should handle missing tmux gracefully."""
        from app.api.voice_routes import get_tmux_pane_content

        # Mock get_pane_id to return a valid pane_id
        with patch("app.api.voice_routes.get_pane_id", return_value="%17"):
            with patch("app.api.voice_routes.subprocess.run") as mock_run:
                mock_run.side_effect = FileNotFoundError("tmux not found")
                result = get_tmux_pane_content("test-session", "pane-0")
                assert "tmux not found" in result

    def test_get_tmux_pane_content_success(self):
        """Should return pane content on success."""
        from app.api.voice_routes import get_tmux_pane_content

        # Mock get_pane_id to return a valid pane_id
        with patch("app.api.voice_routes.get_pane_id", return_value="%17"):
            with patch("app.api.voice_routes.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0, stdout="mock pane content\n"
                )
                result = get_tmux_pane_content("test-session", "pane-0")
                assert result == "mock pane content"

    def test_send_to_tmux_pane_success(self):
        """Should return True on successful send."""
        from app.api.voice_routes import send_to_tmux_pane

        # Mock get_pane_id to return a valid pane_id
        with patch("app.api.voice_routes.get_pane_id", return_value="%17"):
            with patch("app.api.voice_routes.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = send_to_tmux_pane("test-session", "pane-0", "test command")
                assert result is True
                # Should call twice (two-enter rule)
                assert mock_run.call_count == 2

    def test_send_to_tmux_pane_failure(self):
        """Should return False on failed send."""
        from app.api.voice_routes import send_to_tmux_pane

        # Mock get_pane_id to return a valid pane_id
        with patch("app.api.voice_routes.get_pane_id", return_value="%17"):
            with patch("app.api.voice_routes.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1)
                result = send_to_tmux_pane("test-session", "pane-0", "test command")
                assert result is False

    def test_send_to_tmux_pane_not_found(self):
        """Should return False when pane not found."""
        from app.api.voice_routes import send_to_tmux_pane

        # Mock get_pane_id to return None (pane not found)
        with patch("app.api.voice_routes.get_pane_id", return_value=None):
            result = send_to_tmux_pane("test-session", "invalid-pane", "test command")
            assert result is False


class TestSchemaValidation:
    """Tests for Pydantic schema validation."""

    def test_voice_command_request_valid(self):
        """Should accept valid request."""
        from app.models.voice_schemas import VoiceCommandRequest

        req = VoiceCommandRequest(
            raw_command="fix bug go go", transcript="fix bug"
        )
        assert req.raw_command == "fix bug go go"
        assert req.transcript == "fix bug"

    def test_voice_command_response_success(self):
        """Should serialize success response."""
        from app.models.voice_schemas import VoiceCommandResponse

        resp = VoiceCommandResponse(
            success=True, corrected_command="Fix the bug"
        )
        assert resp.success is True
        assert resp.corrected_command == "Fix the bug"
        assert resp.error is None

    def test_voice_command_response_error(self):
        """Should serialize error response."""
        from app.models.voice_schemas import VoiceCommandResponse

        resp = VoiceCommandResponse(
            success=False, error="Something went wrong"
        )
        assert resp.success is False
        assert resp.error == "Something went wrong"

    def test_ephemeral_token_response(self):
        """Should serialize token response."""
        from app.models.voice_schemas import EphemeralTokenResponse, ClientSecret

        secret = ClientSecret(value="ek_test", expires_at=123)
        resp = EphemeralTokenResponse(
            client_secret=secret,
            model="gpt-4o-realtime-preview",
            modalities=["text", "audio"],
        )
        assert resp.client_secret.value == "ek_test"
        assert resp.model == "gpt-4o-realtime-preview"


# ============================================================
# Sprint 4: Task Done + Voice Feedback Tests
# ============================================================


class TestTaskDoneEndpoint:
    """Tests for POST /api/voice/task-done/{team_id}/{role_id}."""

    def test_task_done_endpoint_exists(self):
        """Verify endpoint exists and accepts POST."""
        response = client.post(
            "/api/voice/task-done/test-team/0",
            json={
                "session_id": "test-session",
                "transcript_path": "/tmp/test.jsonl",
                "team_id": "test-team",
                "role_id": "0",
            },
        )
        # Should not be 404
        assert response.status_code != 404

    def test_task_done_queues_celery_task(self):
        """Should queue Celery task for processing (stateless architecture)."""
        from unittest.mock import AsyncMock

        # Mock Celery task and pane content
        with patch(
            "app.api.voice_routes.get_tmux_pane_content",
            return_value="mock pane output",
        ):
            with patch(
                "app.api.voice_routes.get_task_done_listener"
            ) as mock_listener:
                mock_listener.return_value.stop_hook_fired = AsyncMock(
                    return_value={
                        "success": True,
                        "task_id": "celery-task-123",
                    }
                )

                response = client.post(
                    "/api/voice/task-done/mock-team/0",
                    json={
                        "session_id": "test-session",
                        "transcript_path": "/tmp/test.jsonl",
                        "team_id": "mock-team",
                        "role_id": "0",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestTaskDoneListener:
    """Tests for TaskDoneListener service.

    NOTE: Comprehensive tests are in test_task_done_listener.py.
    This class keeps only the basic smoke tests.
    """

    def test_command_sent_stores_command(self):
        """Should store command for later retrieval."""
        from app.services.task_done_listener import TaskDoneListener

        listener = TaskDoneListener()
        cmd_id = listener.command_sent(
            team_id="test-team",
            role_id="0",
            raw_command="test go go",
            corrected_command="Test command",
        )

        assert cmd_id is not None
        pending = listener.get_pending_command("test-team", "0")
        assert pending is not None
        assert pending.corrected_command == "Test command"


# ============================================================
# Phase 4: LLM Tests (REQUIRE BOSS APPROVAL)
# ============================================================


class TestLLMIntegration:
    """Tests that call actual LLM APIs.

    WARNING: These tests cost money!
    DO NOT run without Boss approval.
    """

    def test_correct_voice_command_real(self):
        """Test actual LLM correction (COSTS MONEY - Boss approved)."""
        import os

        if not os.environ.get("XAI_API_KEY"):
            pytest.skip("XAI_API_KEY not set - LLM test requires Boss approval")

        from app.api.voice_routes import correct_voice_command

        result = correct_voice_command(
            "run cross code to fix the bug",
            "Session: test\nRunning claude-code CLI",
        )
        # Should correct "cross code" to "claude-code" or similar
        assert "claude" in result.corrected_command.lower() or "code" in result.corrected_command.lower()

    def test_token_endpoint_real(self):
        """Test actual OpenAI token generation (COSTS MONEY - Boss approved)."""
        import os

        if not os.environ.get("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        response = client.post("/api/voice/token")
        assert response.status_code == 200
        data = response.json()
        assert "client_secret" in data
        assert data["client_secret"]["value"].startswith("ek_")
