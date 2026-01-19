# -*- coding: utf-8 -*-
"""Tests for voice API routes (voice_routes.py).

All external APIs (OpenAI, xAI, Redis, subprocess) are mocked.
"""

from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app


from app.api.auth_routes import SESSION_TOKEN


@pytest.fixture
def client():
    """Test client with auth header."""
    return TestClient(app, headers={"Authorization": f"Bearer {SESSION_TOKEN}"})


class TestGetVoiceToken:
    """Test POST /api/voice/token endpoint."""

    def test_token_success(self, client):
        """Should return ephemeral token from OpenAI."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "client_secret": {"value": "test-secret", "expires_at": 1234567890},
            "model": "gpt-4o-mini-realtime-preview",
            "modalities": ["text", "audio"],
        }

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False):
            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = client.post("/api/voice/token")

                assert response.status_code == 200
                data = response.json()
                assert "client_secret" in data

    def test_token_no_api_key(self, client):
        """Should return 500 when OPENAI_API_KEY not set."""
        # Save original and set to empty
        import os
        original = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = ""
        try:
            response = client.post("/api/voice/token")
            assert response.status_code == 500
            assert "OPENAI_API_KEY" in response.json()["detail"]
        finally:
            if original:
                os.environ["OPENAI_API_KEY"] = original

    def test_token_openai_error(self, client):
        """Should return error on OpenAI API failure."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False):
            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = client.post("/api/voice/token")

                assert response.status_code == 401

    def test_token_timeout(self, client):
        """Should return 504 on timeout."""
        import httpx

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False):
            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = client.post("/api/voice/token")

                assert response.status_code == 504
                assert "timeout" in response.json()["detail"].lower()

    def test_token_request_error(self, client):
        """Should return 502 on request error."""
        import httpx

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False):
            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(side_effect=httpx.RequestError("connection failed"))
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = client.post("/api/voice/token")

                assert response.status_code == 502


class TestGetSonioxToken:
    """Test POST /api/voice/token/soniox endpoint."""

    def test_soniox_token_success(self, client):
        """Should return Soniox API key."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-soniox-key"
        try:
            response = client.post("/api/voice/token/soniox")

            assert response.status_code == 200
            data = response.json()
            assert data["api_key"] == "test-soniox-key"
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original
            else:
                os.environ.pop("SONIOX_API_KEY", None)

    def test_soniox_token_no_api_key(self, client):
        """Should return 500 when SONIOX_API_KEY not set."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = ""
        try:
            response = client.post("/api/voice/token/soniox")
            assert response.status_code == 500
            assert "SONIOX_API_KEY" in response.json()["detail"]
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original


class TestProcessVoiceCommand:
    """Test POST /api/voice/command/{team_id}/{role_id} endpoint."""

    def test_command_success(self, client):
        """Should process voice command and send to tmux."""
        import os
        original = os.environ.get("XAI_API_KEY")
        os.environ["XAI_API_KEY"] = "test-key"
        try:
            # Create mock LLM that returns structured output with RoutedCommand schema
            mock_structured = MagicMock()
            mock_structured.corrected_command = "Fix the bug"
            mock_structured.is_backlog_task = False
            mock_llm = MagicMock()
            mock_llm.with_structured_output.return_value.invoke.return_value = mock_structured

            with patch(
                "app.api.voice_routes.command_routes.get_tmux_pane_content",
                return_value="pane context"
            ):
                with patch(
                    "app.api.voice_routes.command_routes.send_to_tmux_pane",
                    return_value=True
                ):
                    with patch(
                        "langchain.chat_models.init_chat_model",
                        return_value=mock_llm
                    ):
                        with patch(
                            "app.api.voice_routes.task_routes.get_task_done_listener"
                        ) as mock_listener:
                            mock_listener.return_value.command_sent.return_value = "cmd-id"

                            response = client.post(
                                "/api/voice/command/team1/pane-0",
                                json={
                                    "raw_command": "fix bug go go",
                                    "transcript": "fix bug",
                                }
                            )

                            assert response.status_code == 200
                            data = response.json()
                            assert data["success"] is True
                            assert "corrected_command" in data
        finally:
            if original:
                os.environ["XAI_API_KEY"] = original

    def test_command_tmux_failure(self, client):
        """Should return error when tmux send fails."""
        import os
        original = os.environ.get("XAI_API_KEY")
        os.environ["XAI_API_KEY"] = "test-key"
        try:
            # Create mock LLM that returns structured output with RoutedCommand schema
            mock_structured = MagicMock()
            mock_structured.corrected_command = "Test command"
            mock_structured.is_backlog_task = False
            mock_llm = MagicMock()
            mock_llm.with_structured_output.return_value.invoke.return_value = mock_structured

            with patch(
                "app.api.voice_routes.command_routes.get_tmux_pane_content",
                return_value="context"
            ):
                with patch(
                    "app.api.voice_routes.command_routes.send_to_tmux_pane",
                    return_value=False
                ):
                    with patch(
                        "langchain.chat_models.init_chat_model",
                        return_value=mock_llm
                    ):
                        response = client.post(
                            "/api/voice/command/team1/pane-0",
                            json={
                                "raw_command": "test",
                                "transcript": "test",
                            }
                        )

                        assert response.status_code == 200
                        data = response.json()
                        assert data["success"] is False
                        assert "error" in data
        finally:
            if original:
                os.environ["XAI_API_KEY"] = original

    def test_command_without_llm_key(self, client):
        """Should use original transcript without XAI_API_KEY."""
        import os
        original = os.environ.get("XAI_API_KEY")
        os.environ["XAI_API_KEY"] = ""
        try:
            with patch(
                "app.api.voice_routes.command_routes.get_tmux_pane_content",
                return_value="context"
            ):
                with patch(
                    "app.api.voice_routes.command_routes.send_to_tmux_pane",
                    return_value=True
                ):
                    with patch(
                        "app.api.voice_routes.task_routes.get_task_done_listener"
                    ) as mock_listener:
                        mock_listener.return_value.command_sent.return_value = "id"

                        response = client.post(
                            "/api/voice/command/team1/pane-0",
                            json={
                                "raw_command": "original command",
                                "transcript": "original command",
                            }
                        )

                        assert response.status_code == 200
                        data = response.json()
                        assert data["success"] is True
                        # Should return original transcript as corrected
                        assert data["corrected_command"] == "original command"
        finally:
            if original:
                os.environ["XAI_API_KEY"] = original


class TestTaskDone:
    """Test POST /api/voice/task-done/{team_id}/{role_id} endpoint."""

    def test_task_done_success(self, client):
        """Should process task done and return summary."""
        with patch(
            "app.api.voice_routes.task_routes.should_skip_role",
            return_value=False  # Don't skip - process the request
        ):
            with patch(
                "app.api.voice_routes.command_routes.get_tmux_pane_content",
                return_value="pane output"
            ):
                with patch(
                    "app.api.voice_routes.task_routes.get_task_done_listener"
                ) as mock_listener:
                    mock_listener.return_value.stop_hook_fired = AsyncMock(
                        return_value={
                            "success": True,
                            "summary": "Done. Task completed.",
                            "command_id": "cmd-123",
                        }
                    )

                    response = client.post(
                        "/api/voice/task-done/team1/pane-0",
                        json={
                            "session_id": "session-123",
                            "transcript_path": "/tmp/transcript.txt",
                            "team_id": "team1",
                            "role_id": "pane-0",
                        }
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True
                    assert data["summary"] == "Done. Task completed."

    def test_task_done_rejects_mismatched_body_ids(self, client):
        """Should return 400 when body team/role don't match path."""
        response = client.post(
            "/api/voice/task-done/team1/pane-0",
            json={
                "session_id": "session-123",
                "transcript_path": "/tmp/transcript.txt",
                "team_id": "other-team",
                "role_id": "pane-1",
            }
        )

        assert response.status_code == 400
        assert "does not match" in response.json()["detail"]

    def test_task_done_listener_error(self, client):
        """Should return error on listener failure."""
        with patch(
            "app.api.voice_routes.task_routes.should_skip_role",
            return_value=False  # Don't skip - process the request
        ):
            with patch(
                "app.api.voice_routes.command_routes.get_tmux_pane_content",
                return_value="output"
            ):
                with patch(
                    "app.api.voice_routes.task_routes.get_task_done_listener"
                ) as mock_listener:
                    mock_listener.return_value.stop_hook_fired = AsyncMock(
                        return_value={
                            "success": False,
                            "error": "Celery connection failed",
                        }
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

                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is False
                    assert "error" in data

    def test_task_done_debounced(self, client):
        """Should return success with skipped flag when debounced."""
        with patch(
            "app.api.voice_routes.task_routes.should_skip_role",
            return_value=False  # Don't skip - process the request
        ):
            with patch(
                "app.api.voice_routes.command_routes.get_tmux_pane_content",
                return_value="output"
            ):
                with patch(
                    "app.api.voice_routes.task_routes.get_task_done_listener"
                ) as mock_listener:
                    mock_listener.return_value.stop_hook_fired = AsyncMock(
                        return_value={
                            "success": True,
                            "skipped": True,
                            "reason": "debounced",
                        }
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

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True


class TestGetPaneId:
    """Test get_pane_id helper function."""

    def test_returns_pane_id(self):
        """Should look up pane ID from role ID."""
        from app.api.voice_routes.command_routes import get_pane_id

        with patch("app.services.tmux_service.TmuxService._get_pane_target") as mock_target:
            mock_target.return_value = "%17"
            result = get_pane_id("team1", "pane-0")

            assert result == "%17"

    def test_returns_none_for_invalid(self):
        """Should return None for invalid role ID."""
        from app.api.voice_routes.command_routes import get_pane_id

        with patch("app.services.tmux_service.TmuxService._get_pane_target") as mock_target:
            mock_target.return_value = None
            result = get_pane_id("team1", "invalid")

            assert result is None


class TestGetTmuxPaneContent:
    """Test get_tmux_pane_content helper function."""

    def test_captures_content(self):
        """Should capture pane content via subprocess."""
        with patch("app.api.voice_routes.command_routes.get_pane_id", return_value="%17"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="pane content"
                )

                from app.api.voice_routes.command_routes import get_tmux_pane_content
                result = get_tmux_pane_content("team1", "pane-0")

                assert result == "pane content"

    def test_returns_error_on_failure(self):
        """Should return error message on capture failure."""
        with patch("app.api.voice_routes.command_routes.get_pane_id", return_value="%17"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1,
                    stderr="capture error"
                )

                from app.api.voice_routes.command_routes import get_tmux_pane_content
                result = get_tmux_pane_content("team1", "pane-0")

                assert "Error" in result

    def test_returns_not_found_for_invalid_pane(self):
        """Should return not found for invalid pane."""
        with patch("app.api.voice_routes.command_routes.get_pane_id", return_value=None):
            from app.api.voice_routes.command_routes import get_tmux_pane_content
            result = get_tmux_pane_content("team1", "invalid")

            assert "not found" in result.lower()

    def test_handles_timeout(self):
        """Should return timeout message on subprocess timeout."""
        import subprocess

        with patch("app.api.voice_routes.command_routes.get_pane_id", return_value="%17"):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired(cmd="tmux", timeout=5)

                from app.api.voice_routes.command_routes import get_tmux_pane_content
                result = get_tmux_pane_content("team1", "pane-0")

                assert "timed out" in result.lower()

    def test_handles_generic_exception(self):
        """Should return error message on generic exception."""
        with patch("app.api.voice_routes.command_routes.get_pane_id", return_value="%17"):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = RuntimeError("Unexpected error")

                from app.api.voice_routes.command_routes import get_tmux_pane_content
                result = get_tmux_pane_content("team1", "pane-0")

                assert "Error" in result


class TestSendToTmuxPane:
    """Test send_to_tmux_pane helper function."""

    def test_sends_command_success(self):
        """Should send command to pane."""
        with patch("app.api.voice_routes.command_routes.get_pane_id", return_value="%17"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                with patch("time.sleep"):  # Skip delay

                    from app.api.voice_routes.command_routes import send_to_tmux_pane
                    result = send_to_tmux_pane("team1", "pane-0", "test cmd")

                    assert result is True
                    # Should call twice (command + second Enter)
                    assert mock_run.call_count == 2

    def test_returns_false_on_failure(self):
        """Should return False on send failure."""
        with patch("app.api.voice_routes.command_routes.get_pane_id", return_value="%17"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1)

                from app.api.voice_routes.command_routes import send_to_tmux_pane
                result = send_to_tmux_pane("team1", "pane-0", "cmd")

                assert result is False

    def test_returns_false_for_invalid_pane(self):
        """Should return False for invalid pane."""
        with patch("app.api.voice_routes.command_routes.get_pane_id", return_value=None):
            from app.api.voice_routes.command_routes import send_to_tmux_pane
            result = send_to_tmux_pane("team1", "invalid", "cmd")

            assert result is False

    def test_returns_false_on_second_enter_failure(self):
        """Should return False when second Enter fails."""
        with patch("app.api.voice_routes.command_routes.get_pane_id", return_value="%17"):
            with patch("subprocess.run") as mock_run:
                # First call succeeds, second fails
                mock_run.side_effect = [
                    MagicMock(returncode=0),
                    MagicMock(returncode=1),
                ]
                with patch("time.sleep"):

                    from app.api.voice_routes.command_routes import send_to_tmux_pane
                    result = send_to_tmux_pane("team1", "pane-0", "cmd")

                    assert result is False

    def test_handles_generic_exception(self):
        """Should return False on generic exception."""
        with patch("app.api.voice_routes.command_routes.get_pane_id", return_value="%17"):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = RuntimeError("Unexpected error")

                from app.api.voice_routes.command_routes import send_to_tmux_pane
                result = send_to_tmux_pane("team1", "pane-0", "cmd")

                assert result is False


class TestProcessVoiceCommandException:
    """Test exception handling in process_voice_command."""

    def test_command_exception_returns_error(self, client):
        """Should return error response on exception."""
        import os
        original = os.environ.get("XAI_API_KEY")
        os.environ["XAI_API_KEY"] = "test-key"
        try:
            with patch(
                "app.api.voice_routes.command_routes.get_tmux_pane_content",
                side_effect=RuntimeError("Unexpected error"),
            ):
                response = client.post(
                    "/api/voice/command/team1/pane-0",
                    json={
                        "raw_command": "test",
                        "transcript": "test",
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert "error" in data
        finally:
            if original:
                os.environ["XAI_API_KEY"] = original


class TestHandleTaskDoneException:
    """Test exception handling in handle_task_done."""

    def test_task_done_exception_returns_error(self, client):
        """Should return error response on exception."""
        with patch(
            "app.api.voice_routes.task_routes.should_skip_role",
            return_value=False  # Don't skip - process the request
        ):
            with patch(
                "app.api.voice_routes.command_routes.get_tmux_pane_content",
                side_effect=RuntimeError("Unexpected error"),
            ):
                response = client.post(
                    "/api/voice/task-done/team1/pane-0",
                    json={
                        "session_id": "session",
                        "transcript_path": "/tmp/path",
                        "team_id": "team1",
                        "role_id": "pane-0",
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert "error" in data


class TestVoiceFeedbackWebSocket:
    """Test voice feedback WebSocket endpoints."""

    def test_feedback_websocket_connect(self):
        """Should connect and handle ping/pong."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        with patch("app.api.voice_routes.task_routes.get_task_done_listener") as mock_listener:
            mock_listener.return_value.register_websocket = MagicMock()
            mock_listener.return_value.unregister_websocket = MagicMock()

            with client.websocket_connect("/api/voice/ws/feedback/team1/pane-0") as ws:
                # Send ping
                ws.send_text("ping")

                # Should receive pong
                response = ws.receive_text()
                assert response == "pong"

                # Close gracefully
                ws.close()

    def test_feedback_websocket_disconnect(self):
        """Should handle disconnection gracefully."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        with patch("app.api.voice_routes.task_routes.get_task_done_listener") as mock_listener:
            mock_listener.return_value.register_websocket = MagicMock()
            mock_listener.return_value.unregister_websocket = MagicMock()

            with client.websocket_connect("/api/voice/ws/feedback/team1/pane-0") as ws:
                ws.close()

            # Should have called unregister
            mock_listener.return_value.unregister_websocket.assert_called_once()


class TestGlobalVoiceFeedbackWebSocket:
    """Test global voice feedback WebSocket endpoint."""

    def test_global_feedback_websocket_connect(self):
        """Should connect to global feedback endpoint."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        with patch("app.api.voice_routes.task_routes.get_task_done_listener") as mock_listener:
            mock_listener.return_value.ws_manager.register = AsyncMock()
            mock_listener.return_value.ws_manager.unregister = AsyncMock()

            with client.websocket_connect("/api/voice/ws/feedback/global") as ws:
                # Send ping
                ws.send_text("ping")

                # Should receive pong
                response = ws.receive_text()
                assert response == "pong"

                ws.close()

    def test_global_feedback_websocket_disconnect(self):
        """Should unregister on disconnect."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        with patch("app.api.voice_routes.task_routes.get_task_done_listener") as mock_listener:
            mock_ws_manager = MagicMock()
            mock_ws_manager.register = AsyncMock()
            mock_ws_manager.unregister = AsyncMock()
            mock_listener.return_value.ws_manager = mock_ws_manager

            with client.websocket_connect("/api/voice/ws/feedback/global") as ws:
                ws.close()

            # Should have called unregister
            mock_ws_manager.unregister.assert_called_once()


class TestTranscribeAudio:
    """Test POST /api/voice/transcribe endpoint."""

    def test_transcribe_success(self, client):
        """Should transcribe audio file successfully."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-soniox-key"
        try:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "transcript": "Hello world, this is a test",
            }

            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                # Create a test audio file
                audio_content = b"fake audio data"
                response = client.post(
                    "/api/voice/transcribe",
                    files={"audio": ("test.wav", audio_content, "audio/wav")},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["transcription"] == "Hello world, this is a test"
                assert "error" not in data or data["error"] is None
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original
            else:
                os.environ.pop("SONIOX_API_KEY", None)

    def test_transcribe_no_api_key(self, client):
        """Should return 500 when SONIOX_API_KEY not set."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = ""
        try:
            audio_content = b"fake audio"
            response = client.post(
                "/api/voice/transcribe",
                files={"audio": ("test.wav", audio_content, "audio/wav")},
            )

            assert response.status_code == 500
            assert "SONIOX_API_KEY" in response.json()["detail"]
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original

    def test_transcribe_empty_file(self, client):
        """Should return 400 when audio file is empty."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-key"
        try:
            # Send empty file
            response = client.post(
                "/api/voice/transcribe",
                files={"audio": ("test.wav", b"", "audio/wav")},
            )

            assert response.status_code == 400
            assert "empty" in response.json()["detail"].lower()
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original

    def test_transcribe_no_filename(self, client):
        """Should return 400 when audio has no filename."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-key"
        try:
            # Upload without filename - FastAPI will reject it before endpoint
            # But let's test the error handling
            response = client.post(
                "/api/voice/transcribe",
                files={"audio": ("", b"audio data", "audio/wav")},
            )

            # FastAPI requires filename, so this should be caught at form validation
            # Either 400 or 422 depending on validation level
            assert response.status_code in [400, 422]
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original

    def test_transcribe_soniox_api_error(self, client):
        """Should handle Soniox API error responses."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-key"
        try:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"

            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = client.post(
                    "/api/voice/transcribe",
                    files={"audio": ("test.wav", b"audio data", "audio/wav")},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert "401" in data["error"]
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original

    def test_transcribe_empty_response(self, client):
        """Should handle empty transcription from Soniox."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-key"
        try:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"transcript": ""}

            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = client.post(
                    "/api/voice/transcribe",
                    files={"audio": ("test.wav", b"audio data", "audio/wav")},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert "No speech detected" in data["error"]
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original

    def test_transcribe_whitespace_response(self, client):
        """Should handle whitespace-only transcription from Soniox."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-key"
        try:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"transcript": "   \n\t  "}

            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = client.post(
                    "/api/voice/transcribe",
                    files={"audio": ("test.wav", b"audio data", "audio/wav")},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert "No speech detected" in data["error"]
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original

    def test_transcribe_timeout(self, client):
        """Should handle Soniox API timeout."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-key"
        try:
            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(
                    side_effect=Exception("timeout")
                )
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = client.post(
                    "/api/voice/transcribe",
                    files={"audio": ("test.wav", b"audio data", "audio/wav")},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert "error" in data
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original

    def test_transcribe_request_error(self, client):
        """Should handle request errors."""
        import os
        import httpx

        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-key"
        try:
            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(
                    side_effect=httpx.RequestError("connection failed")
                )
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = client.post(
                    "/api/voice/transcribe",
                    files={"audio": ("test.wav", b"audio data", "audio/wav")},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert "Request error" in data["error"]
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original

    def test_transcribe_missing_audio_field(self, client):
        """Should return 422 when audio field is missing."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-key"
        try:
            # Send request without audio file
            response = client.post("/api/voice/transcribe")

            # FastAPI will reject missing required file
            assert response.status_code == 422
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original

    def test_transcribe_with_special_characters(self, client):
        """Should handle transcriptions with special characters."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-key"
        try:
            special_text = "Hello! @#$%^&*() 你好 مرحبا"
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"transcript": special_text}

            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = client.post(
                    "/api/voice/transcribe",
                    files={"audio": ("test.wav", b"audio data", "audio/wav")},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["transcription"] == special_text
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original

    def test_transcribe_large_file(self, client):
        """Should handle large audio files."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-key"
        try:
            # Create 10MB of fake audio data
            large_audio = b"x" * (10 * 1024 * 1024)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"transcript": "Large audio test"}

            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                response = client.post(
                    "/api/voice/transcribe",
                    files={"audio": ("large.wav", large_audio, "audio/wav")},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original

    def test_transcribe_different_audio_formats(self, client):
        """Should accept different audio formats."""
        import os
        original = os.environ.get("SONIOX_API_KEY")
        os.environ["SONIOX_API_KEY"] = "test-key"
        try:
            formats = [
                ("test.mp3", "audio/mpeg"),
                ("test.wav", "audio/wav"),
                ("test.m4a", "audio/mp4"),
                ("test.ogg", "audio/ogg"),
            ]

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"transcript": "Test audio"}

            with patch("app.api.voice_routes.token_routes.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_instance

                for filename, content_type in formats:
                    response = client.post(
                        "/api/voice/transcribe",
                        files={
                            "audio": (filename, b"audio data", content_type)
                        },
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True
        finally:
            if original:
                os.environ["SONIOX_API_KEY"] = original
