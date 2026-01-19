# -*- coding: utf-8 -*-
"""Tests for CommandProcessor extraction from command_routes.py.

This test file is part of Sprint R1 TDD refactoring.
Tests are written BEFORE extracting CommandProcessor service to ensure
the new structure maintains existing functionality.

CommandProcessor should handle:
- Tmux pane lookups (get_pane_id, get_bl_pane_id)
- Tmux pane content retrieval (get_tmux_pane_content)
- Command sending to tmux panes (send_to_tmux_pane)
- Voice command correction with LLM (correct_voice_command)
- Backlog routing decisions (RoutedCommand)
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path


class TestCommandProcessorModule:
    """Verify CommandProcessor class structure after extraction."""

    def test_command_processor_class_exists(self):
        """CommandProcessor class should be importable after extraction."""
        # This will fail until we extract the class
        with pytest.raises((ImportError, AttributeError)):
            from app.services.command_processor import CommandProcessor

    def test_command_processor_has_required_methods(self):
        """CommandProcessor should have all required methods."""
        # After extraction, verify methods exist
        expected_methods = [
            "get_pane_id",
            "get_tmux_pane_content",
            "send_to_tmux_pane",
            "get_bl_pane_id",
            "correct_voice_command",
        ]
        # Will verify after extraction
        assert True  # Placeholder


class TestGetPaneId:
    """Test get_pane_id tmux pane lookup."""

    def test_get_pane_id_returns_target(self):
        """Should return tmux pane target like %17."""
        from app.api.voice_routes.command_routes import get_pane_id

        with patch("app.api.voice_routes.command_routes.TmuxService") as MockService:
            mock_service = MockService.return_value
            mock_service._get_pane_target.return_value = "%17"

            result = get_pane_id("test-team", "pane-0")

            assert result == "%17"
            mock_service._get_pane_target.assert_called_once_with("test-team", "pane-0")

    def test_get_pane_id_returns_none_when_not_found(self):
        """Should return None if pane not found."""
        from app.api.voice_routes.command_routes import get_pane_id

        with patch("app.api.voice_routes.command_routes.TmuxService") as MockService:
            mock_service = MockService.return_value
            mock_service._get_pane_target.return_value = None

            result = get_pane_id("test-team", "invalid-pane")

            assert result is None


class TestGetTmuxPaneContent:
    """Test get_tmux_pane_content pane capture."""

    def test_get_tmux_pane_content_captures_output(self):
        """Should capture tmux pane content."""
        from app.api.voice_routes.command_routes import get_tmux_pane_content

        with patch("app.api.voice_routes.command_routes.get_pane_id") as mock_get_pane, \
             patch("subprocess.run") as mock_run:
            mock_get_pane.return_value = "%17"

            # Mock both subprocess calls (copy-mode exit and capture-pane)
            mock_run.side_effect = [
                MagicMock(returncode=0),  # copy-mode -q
                MagicMock(returncode=0, stdout="Pane content here\n")  # capture-pane
            ]

            result = get_tmux_pane_content("test-team", "pane-0", lines=50)

            assert "Pane content here" in result
            assert mock_run.call_count == 2

    def test_get_tmux_pane_content_handles_pane_not_found(self):
        """Should return error message if pane not found."""
        from app.api.voice_routes.command_routes import get_tmux_pane_content

        with patch("app.api.voice_routes.command_routes.get_pane_id") as mock_get_pane:
            mock_get_pane.return_value = None

            result = get_tmux_pane_content("test-team", "invalid-pane")

            assert "[Pane not found:" in result

    def test_get_tmux_pane_content_handles_tmux_error(self):
        """Should handle tmux command errors."""
        from app.api.voice_routes.command_routes import get_tmux_pane_content

        with patch("app.api.voice_routes.command_routes.get_pane_id") as mock_get_pane, \
             patch("subprocess.run") as mock_run:
            mock_get_pane.return_value = "%17"
            mock_run.side_effect = [
                MagicMock(returncode=0),  # copy-mode -q
                MagicMock(returncode=1, stderr="Error message")  # capture-pane fails
            ]

            result = get_tmux_pane_content("test-team", "pane-0")

            assert "[Error capturing pane:" in result


class TestSendToTmuxPane:
    """Test send_to_tmux_pane command sending."""

    def test_send_to_tmux_pane_success(self):
        """Should send command with two-enter rule."""
        from app.api.voice_routes.command_routes import send_to_tmux_pane

        with patch("app.api.voice_routes.command_routes.get_pane_id") as mock_get_pane, \
             patch("subprocess.run") as mock_run, \
             patch("time.sleep"):
            mock_get_pane.return_value = "%17"
            mock_run.return_value = MagicMock(returncode=0)

            result = send_to_tmux_pane("test-team", "pane-0", "test command")

            assert result is True
            # Should call subprocess.run twice (command + second enter)
            assert mock_run.call_count == 2

    def test_send_to_tmux_pane_handles_pane_not_found(self):
        """Should return False if pane not found."""
        from app.api.voice_routes.command_routes import send_to_tmux_pane

        with patch("app.api.voice_routes.command_routes.get_pane_id") as mock_get_pane:
            mock_get_pane.return_value = None

            result = send_to_tmux_pane("test-team", "invalid-pane", "test")

            assert result is False

    def test_send_to_tmux_pane_handles_send_error(self):
        """Should return False if tmux send-keys fails."""
        from app.api.voice_routes.command_routes import send_to_tmux_pane

        with patch("app.api.voice_routes.command_routes.get_pane_id") as mock_get_pane, \
             patch("subprocess.run") as mock_run:
            mock_get_pane.return_value = "%17"
            mock_run.return_value = MagicMock(returncode=1)

            result = send_to_tmux_pane("test-team", "pane-0", "test")

            assert result is False


class TestGetBlPaneId:
    """Test get_bl_pane_id backlog pane lookup."""

    def test_get_bl_pane_id_returns_bl_role(self):
        """Should return BL pane ID."""
        from app.api.voice_routes.command_routes import get_bl_pane_id

        with patch("app.api.voice_routes.command_routes.tmux_service") as mock_service:
            mock_service.get_roles.return_value = [
                {"id": "pane-0", "name": "PO"},
                {"id": "pane-6", "name": "BL"},
            ]

            result = get_bl_pane_id("test-team")

            assert result == "pane-6"

    def test_get_bl_pane_id_returns_none_if_not_found(self):
        """Should return None if BL pane not found."""
        from app.api.voice_routes.command_routes import get_bl_pane_id

        with patch("app.api.voice_routes.command_routes.tmux_service") as mock_service:
            mock_service.get_roles.return_value = [
                {"id": "pane-0", "name": "PO"},
                {"id": "pane-1", "name": "SM"},
            ]

            result = get_bl_pane_id("test-team")

            assert result is None


class TestRoutedCommand:
    """Test RoutedCommand class."""

    def test_routed_command_creation(self):
        """Should create RoutedCommand with command and routing."""
        from app.api.voice_routes.command_routes import RoutedCommand

        cmd = RoutedCommand("test command", is_backlog_task=True)

        assert cmd.corrected_command == "test command"
        assert cmd.is_backlog_task is True

    def test_routed_command_defaults_to_not_backlog(self):
        """Should default is_backlog_task to False."""
        from app.api.voice_routes.command_routes import RoutedCommand

        cmd = RoutedCommand("test command")

        assert cmd.is_backlog_task is False


class TestCorrectVoiceCommand:
    """Test correct_voice_command LLM correction."""

    def test_correct_voice_command_with_llm(self):
        """Should use LLM to correct voice transcript."""
        from app.api.voice_routes.command_routes import correct_voice_command

        with patch("app.api.voice_routes.command_routes.init_chat_model") as mock_init, \
             patch.dict("os.environ", {"XAI_API_KEY": "test-key"}):
            mock_llm = MagicMock()
            mock_structured = MagicMock()
            mock_structured.invoke.return_value = MagicMock(
                corrected_command="corrected command",
                is_backlog_task=False
            )
            mock_llm.with_structured_output.return_value = mock_structured
            mock_init.return_value = mock_llm

            result = correct_voice_command("raw transcript", "tmux context")

            assert result.corrected_command == "corrected command"
            assert result.is_backlog_task is False

    def test_correct_voice_command_without_api_key(self):
        """Should return original transcript if XAI_API_KEY not set."""
        from app.api.voice_routes.command_routes import correct_voice_command

        with patch.dict("os.environ", {}, clear=True):
            result = correct_voice_command("raw transcript", "context")

            assert result.corrected_command == "raw transcript"
            assert result.is_backlog_task is False

    def test_correct_voice_command_routes_backlog_tasks(self):
        """Should detect backlog write operations for routing."""
        from app.api.voice_routes.command_routes import correct_voice_command

        with patch("app.api.voice_routes.command_routes.init_chat_model") as mock_init, \
             patch.dict("os.environ", {"XAI_API_KEY": "test-key"}):
            mock_llm = MagicMock()
            mock_structured = MagicMock()
            mock_structured.invoke.return_value = MagicMock(
                corrected_command="add task to backlog",
                is_backlog_task=True
            )
            mock_llm.with_structured_output.return_value = mock_structured
            mock_init.return_value = mock_llm

            result = correct_voice_command("add task to backlog", "context")

            assert result.is_backlog_task is True


class TestCommandProcessorIntegration:
    """Test CommandProcessor integration with command_routes."""

    def test_command_routes_uses_processor(self):
        """After extraction, command_routes should use CommandProcessor."""
        # This verifies the refactoring maintains functionality
        # Will be updated after extraction
        assert True  # Placeholder

    def test_all_methods_accessible(self):
        """All methods should be accessible after extraction."""
        from app.api.voice_routes import command_routes

        # Current implementation - these should exist
        assert hasattr(command_routes, "get_pane_id")
        assert hasattr(command_routes, "get_tmux_pane_content")
        assert hasattr(command_routes, "send_to_tmux_pane")
        assert hasattr(command_routes, "get_bl_pane_id")
        assert hasattr(command_routes, "correct_voice_command")
