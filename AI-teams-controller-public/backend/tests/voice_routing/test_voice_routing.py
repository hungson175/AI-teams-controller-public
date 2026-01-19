# -*- coding: utf-8 -*-
"""Tests for voice command routing to BL (Backlog Organizer) pane.

Story 5: Routing tests for Backlog Organizer Epic.

These tests verify that:
- CREATE/UPDATE/DELETE operations → is_backlog_task=True → route to BL
- READ operations → is_backlog_task=False → route to selected pane
- Non-backlog commands → is_backlog_task=False → route to selected pane
"""

from unittest.mock import MagicMock, patch

import pytest


class TestRoutedCommand:
    """Tests for RoutedCommand class."""

    def test_routed_command_default_is_backlog_false(self):
        """Default is_backlog_task should be False."""
        from app.api.voice_routes import RoutedCommand

        cmd = RoutedCommand(corrected_command="fix the bug")
        assert cmd.corrected_command == "fix the bug"
        assert cmd.is_backlog_task is False

    def test_routed_command_with_backlog_true(self):
        """Should accept is_backlog_task=True."""
        from app.api.voice_routes import RoutedCommand

        cmd = RoutedCommand(
            corrected_command="add dark mode to backlog",
            is_backlog_task=True,
        )
        assert cmd.corrected_command == "add dark mode to backlog"
        assert cmd.is_backlog_task is True


class TestGetBlPaneId:
    """Tests for get_bl_pane_id helper function."""

    def test_get_bl_pane_id_found(self):
        """Should return BL pane ID when BL pane exists."""
        from app.api.voice_routes import get_bl_pane_id

        mock_roles = [
            {"id": "pane-0", "name": "PM"},
            {"id": "pane-1", "name": "SA"},
            {"id": "pane-6", "name": "BL"},
        ]

        # Patch at the source module where tmux_service is defined
        with patch("app.services.tmux_service.tmux_service") as mock_tmux:
            mock_tmux.get_roles.return_value = mock_roles
            result = get_bl_pane_id("test_team")
            assert result == "pane-6"

    def test_get_bl_pane_id_not_found(self):
        """Should return None when BL pane doesn't exist."""
        from app.api.voice_routes import get_bl_pane_id

        mock_roles = [
            {"id": "pane-0", "name": "PM"},
            {"id": "pane-1", "name": "SA"},
        ]

        # Patch at the source module where tmux_service is defined
        with patch("app.services.tmux_service.tmux_service") as mock_tmux:
            mock_tmux.get_roles.return_value = mock_roles
            result = get_bl_pane_id("test_team")
            assert result is None


class TestVoiceRoutingLogic:
    """Tests for voice command routing logic in process_voice_command.

    These tests mock correct_voice_command to test routing behavior
    without calling the actual LLM.
    """

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all external dependencies for routing tests."""
        with patch("app.api.voice_routes.get_tmux_pane_content") as mock_context, \
             patch("app.api.voice_routes.correct_voice_command") as mock_correct, \
             patch("app.api.voice_routes.send_to_tmux_pane") as mock_send, \
             patch("app.api.voice_routes.get_task_done_listener") as mock_listener, \
             patch("app.api.voice_routes.get_bl_pane_id") as mock_bl:

            mock_context.return_value = "some context"
            mock_send.return_value = True
            mock_listener.return_value = MagicMock()

            yield {
                "context": mock_context,
                "correct": mock_correct,
                "send": mock_send,
                "listener": mock_listener,
                "bl_pane": mock_bl,
            }

    @pytest.mark.asyncio
    async def test_backlog_task_routes_to_bl_pane(self, mock_dependencies):
        """Commands with is_backlog_task=True should route to BL pane."""
        from app.api.voice_routes import RoutedCommand, process_voice_command
        from app.models.voice_schemas import VoiceCommandRequest

        # Setup: correct_voice_command returns is_backlog_task=True
        mock_dependencies["correct"].return_value = RoutedCommand(
            corrected_command="add dark mode to backlog",
            is_backlog_task=True,
        )
        mock_dependencies["bl_pane"].return_value = "pane-6"

        request = VoiceCommandRequest(
            raw_command="add dark mode to backlog",
            transcript="add dark mode to backlog",
        )

        response = await process_voice_command("test_team", "pane-0", request)

        # Should route to BL pane (pane-6), not selected pane (pane-0)
        mock_dependencies["send"].assert_called_once_with(
            "test_team", "pane-6", "add dark mode to backlog"
        )
        assert response.success is True

    @pytest.mark.asyncio
    async def test_backlog_task_falls_back_when_bl_not_found(self, mock_dependencies):
        """Should fall back to selected pane when BL pane not found."""
        from app.api.voice_routes import RoutedCommand, process_voice_command
        from app.models.voice_schemas import VoiceCommandRequest

        # Setup: correct_voice_command returns is_backlog_task=True but BL not found
        mock_dependencies["correct"].return_value = RoutedCommand(
            corrected_command="add feature to backlog",
            is_backlog_task=True,
        )
        mock_dependencies["bl_pane"].return_value = None  # BL not found

        request = VoiceCommandRequest(
            raw_command="add feature to backlog",
            transcript="add feature to backlog",
        )

        response = await process_voice_command("test_team", "pane-0", request)

        # Should fall back to selected pane (pane-0)
        mock_dependencies["send"].assert_called_once_with(
            "test_team", "pane-0", "add feature to backlog"
        )
        assert response.success is True

    @pytest.mark.asyncio
    async def test_non_backlog_task_routes_to_selected_pane(self, mock_dependencies):
        """Commands with is_backlog_task=False should route to selected pane."""
        from app.api.voice_routes import RoutedCommand, process_voice_command
        from app.models.voice_schemas import VoiceCommandRequest

        # Setup: correct_voice_command returns is_backlog_task=False
        mock_dependencies["correct"].return_value = RoutedCommand(
            corrected_command="fix the login bug",
            is_backlog_task=False,
        )

        request = VoiceCommandRequest(
            raw_command="fix the login bug",
            transcript="fix the login bug",
        )

        response = await process_voice_command("test_team", "pane-2", request)

        # Should route to selected pane (pane-2)
        mock_dependencies["send"].assert_called_once_with(
            "test_team", "pane-2", "fix the login bug"
        )
        # BL pane lookup should NOT be called for non-backlog tasks
        mock_dependencies["bl_pane"].assert_not_called()
        assert response.success is True


class TestRoutingDecisionExamples:
    """Example-based tests for routing decisions.

    These test the expected behavior based on ADR Section 8.
    Note: These mock the LLM response, not actual LLM calls.
    """

    @pytest.fixture
    def mock_all(self):
        """Mock all dependencies."""
        with patch("app.api.voice_routes.get_tmux_pane_content") as mock_ctx, \
             patch("app.api.voice_routes.send_to_tmux_pane") as mock_send, \
             patch("app.api.voice_routes.get_task_done_listener") as mock_listener, \
             patch("app.api.voice_routes.get_bl_pane_id") as mock_bl:

            mock_ctx.return_value = ""
            mock_send.return_value = True
            mock_listener.return_value = MagicMock()
            mock_bl.return_value = "pane-6"

            yield {
                "send": mock_send,
                "bl_pane": mock_bl,
            }

    @pytest.mark.asyncio
    async def test_create_commands_route_to_bl(self, mock_all):
        """CREATE operations should route to BL."""
        from app.api.voice_routes import RoutedCommand, process_voice_command
        from app.models.voice_schemas import VoiceCommandRequest

        create_commands = [
            "add dark mode to backlog",
            "note feature idea for caching",
            "backlog add search improvement",
        ]

        for cmd in create_commands:
            with patch("app.api.voice_routes.correct_voice_command") as mock_correct:
                mock_correct.return_value = RoutedCommand(
                    corrected_command=cmd,
                    is_backlog_task=True,  # CREATE → True
                )

                request = VoiceCommandRequest(raw_command=cmd, transcript=cmd)
                await process_voice_command("test_team", "pane-0", request)

                # Should route to BL (pane-6)
                mock_all["send"].assert_called_with("test_team", "pane-6", cmd)
                mock_all["send"].reset_mock()

    @pytest.mark.asyncio
    async def test_update_commands_route_to_bl(self, mock_all):
        """UPDATE operations should route to BL."""
        from app.api.voice_routes import RoutedCommand, process_voice_command
        from app.models.voice_schemas import VoiceCommandRequest

        update_commands = [
            "change priority of X to P0",
            "move that task to high priority",
            "update the caching item",
        ]

        for cmd in update_commands:
            with patch("app.api.voice_routes.correct_voice_command") as mock_correct:
                mock_correct.return_value = RoutedCommand(
                    corrected_command=cmd,
                    is_backlog_task=True,  # UPDATE → True
                )

                request = VoiceCommandRequest(raw_command=cmd, transcript=cmd)
                await process_voice_command("test_team", "pane-0", request)

                # Should route to BL (pane-6)
                mock_all["send"].assert_called_with("test_team", "pane-6", cmd)
                mock_all["send"].reset_mock()

    @pytest.mark.asyncio
    async def test_delete_commands_route_to_bl(self, mock_all):
        """DELETE operations should route to BL."""
        from app.api.voice_routes import RoutedCommand, process_voice_command
        from app.models.voice_schemas import VoiceCommandRequest

        delete_commands = [
            "remove X from backlog",
            "delete that completed task",
            "archive the done items",
        ]

        for cmd in delete_commands:
            with patch("app.api.voice_routes.correct_voice_command") as mock_correct:
                mock_correct.return_value = RoutedCommand(
                    corrected_command=cmd,
                    is_backlog_task=True,  # DELETE → True
                )

                request = VoiceCommandRequest(raw_command=cmd, transcript=cmd)
                await process_voice_command("test_team", "pane-0", request)

                # Should route to BL (pane-6)
                mock_all["send"].assert_called_with("test_team", "pane-6", cmd)
                mock_all["send"].reset_mock()

    @pytest.mark.asyncio
    async def test_read_commands_stay_in_selected_pane(self, mock_all):
        """READ operations should NOT route to BL."""
        from app.api.voice_routes import RoutedCommand, process_voice_command
        from app.models.voice_schemas import VoiceCommandRequest

        read_commands = [
            "check the backlog",
            "what tasks are pending",
            "show me the priority list",
            "pull tasks to do",
        ]

        for cmd in read_commands:
            with patch("app.api.voice_routes.correct_voice_command") as mock_correct:
                mock_correct.return_value = RoutedCommand(
                    corrected_command=cmd,
                    is_backlog_task=False,  # READ → False
                )

                request = VoiceCommandRequest(raw_command=cmd, transcript=cmd)
                await process_voice_command("test_team", "pane-0", request)

                # Should stay in selected pane (pane-0)
                mock_all["send"].assert_called_with("test_team", "pane-0", cmd)
                mock_all["send"].reset_mock()

    @pytest.mark.asyncio
    async def test_non_backlog_commands_stay_in_selected_pane(self, mock_all):
        """Non-backlog commands should NOT route to BL."""
        from app.api.voice_routes import RoutedCommand, process_voice_command
        from app.models.voice_schemas import VoiceCommandRequest

        non_backlog_commands = [
            "fix the login bug",
            "build the search feature",
            "run the tests",
        ]

        for cmd in non_backlog_commands:
            with patch("app.api.voice_routes.correct_voice_command") as mock_correct:
                mock_correct.return_value = RoutedCommand(
                    corrected_command=cmd,
                    is_backlog_task=False,  # Non-backlog → False
                )

                request = VoiceCommandRequest(raw_command=cmd, transcript=cmd)
                await process_voice_command("test_team", "pane-2", request)

                # Should stay in selected pane (pane-2, e.g., BE)
                mock_all["send"].assert_called_with("test_team", "pane-2", cmd)
                mock_all["send"].reset_mock()
