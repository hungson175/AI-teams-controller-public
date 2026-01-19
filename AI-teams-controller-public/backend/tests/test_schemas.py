# -*- coding: utf-8 -*-
"""Tests for Pydantic schemas.

Validates schema structure and field types.
"""

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    Team,
    Role,
    TeamsResponse,
    RolesResponse,
    SendMessageRequest,
    SendMessageResponse,
    LastMessage,
    PaneStateResponse,
)
from app.models.voice_schemas import (
    SonioxTokenResponse,
    VoiceCommandRequest,
    VoiceCommandResponse,
    LLMTokenMessage,
    CommandSentMessage,
    VoiceFeedbackMessage,
    VoiceErrorMessage,
    TaskDoneRequest,
    TaskDoneResponse,
)


class TestTeamSchema:
    """Test Team schema."""

    def test_valid_team(self):
        """Should create Team with valid data."""
        team = Team(id="team1", name="Team One")
        assert team.id == "team1"
        assert team.name == "Team One"

    def test_team_from_dict(self):
        """Should create Team from dict."""
        team = Team(**{"id": "team2", "name": "Team Two"})
        assert team.id == "team2"

    def test_team_missing_fields(self):
        """Should raise error for missing fields."""
        with pytest.raises(ValidationError):
            Team(id="team1")  # Missing name


class TestRoleSchema:
    """Test Role schema."""

    def test_valid_role(self):
        """Should create Role with valid data."""
        role = Role(id="pane-0", name="PM", order=0)
        assert role.id == "pane-0"
        assert role.name == "PM"
        assert role.order == 0

    def test_role_from_dict(self):
        """Should create Role from dict."""
        role = Role(**{"id": "pane-1", "name": "BE", "order": 1})
        assert role.name == "BE"

    def test_role_missing_order(self):
        """Should raise error for missing order."""
        with pytest.raises(ValidationError):
            Role(id="pane-0", name="PM")


class TestTeamsResponse:
    """Test TeamsResponse schema."""

    def test_teams_response(self):
        """Should create TeamsResponse with list of teams."""
        resp = TeamsResponse(teams=[
            Team(id="t1", name="T1"),
            Team(id="t2", name="T2"),
        ])
        assert len(resp.teams) == 2

    def test_teams_response_empty(self):
        """Should allow empty teams list."""
        resp = TeamsResponse(teams=[])
        assert resp.teams == []


class TestRolesResponse:
    """Test RolesResponse schema."""

    def test_roles_response(self):
        """Should create RolesResponse with team and roles."""
        resp = RolesResponse(
            teamId="team1",
            roles=[Role(id="p0", name="PM", order=0)]
        )
        assert resp.teamId == "team1"
        assert len(resp.roles) == 1


class TestSendMessageRequest:
    """Test SendMessageRequest schema."""

    def test_valid_request(self):
        """Should create request with message."""
        req = SendMessageRequest(message="test message")
        assert req.message == "test message"

    def test_empty_message(self):
        """Should allow empty message."""
        req = SendMessageRequest(message="")
        assert req.message == ""

    def test_missing_message(self):
        """Should raise error for missing message."""
        with pytest.raises(ValidationError):
            SendMessageRequest()


class TestSendMessageResponse:
    """Test SendMessageResponse schema."""

    def test_valid_response(self):
        """Should create response with all fields."""
        resp = SendMessageResponse(
            success=True,
            message="Sent",
            sentAt="2024-01-01T00:00:00Z"
        )
        assert resp.success is True
        assert resp.message == "Sent"


class TestPaneStateResponse:
    """Test PaneStateResponse schema."""

    def test_minimal_response(self):
        """Should create response with required fields."""
        resp = PaneStateResponse(
            output="content",
            lastUpdated="2024-01-01T00:00:00Z"
        )
        assert resp.output == "content"
        assert resp.highlightText is None

    def test_with_highlight(self):
        """Should include optional highlightText."""
        resp = PaneStateResponse(
            output="content",
            lastUpdated="2024-01-01T00:00:00Z",
            highlightText="highlighted"
        )
        assert resp.highlightText == "highlighted"


class TestSonioxTokenResponse:
    """Test SonioxTokenResponse schema."""

    def test_valid_response(self):
        """Should create response with api_key."""
        resp = SonioxTokenResponse(api_key="soniox-key")
        assert resp.api_key == "soniox-key"


class TestVoiceCommandRequest:
    """Test VoiceCommandRequest schema."""

    def test_valid_request(self):
        """Should create request with both fields."""
        req = VoiceCommandRequest(
            raw_command="fix bug go go",
            transcript="fix bug"
        )
        assert req.raw_command == "fix bug go go"
        assert req.transcript == "fix bug"

    def test_missing_transcript(self):
        """Should raise error for missing transcript."""
        with pytest.raises(ValidationError):
            VoiceCommandRequest(raw_command="fix bug go go")


class TestVoiceCommandResponse:
    """Test VoiceCommandResponse schema."""

    def test_success_response(self):
        """Should create success response."""
        resp = VoiceCommandResponse(
            success=True,
            corrected_command="Fix the bug"
        )
        assert resp.success is True
        assert resp.error is None

    def test_error_response(self):
        """Should create error response."""
        resp = VoiceCommandResponse(
            success=False,
            error="Connection failed"
        )
        assert resp.success is False
        assert resp.error == "Connection failed"


class TestLLMTokenMessage:
    """Test LLMTokenMessage schema."""

    def test_valid_message(self):
        """Should create message with type and token."""
        msg = LLMTokenMessage(type="llm_token", token="Fix")
        assert msg.type == "llm_token"
        assert msg.token == "Fix"


class TestCommandSentMessage:
    """Test CommandSentMessage schema."""

    def test_valid_message(self):
        """Should create message with corrected_command."""
        msg = CommandSentMessage(
            type="command_sent",
            corrected_command="Fix the bug"
        )
        assert msg.type == "command_sent"


class TestVoiceFeedbackMessage:
    """Test VoiceFeedbackMessage schema."""

    def test_valid_message(self):
        """Should create message with summary and audio."""
        msg = VoiceFeedbackMessage(
            type="voice_feedback",
            summary="Done. Task completed.",
            audio="base64encodedaudio"
        )
        assert msg.type == "voice_feedback"
        assert msg.summary == "Done. Task completed."


class TestVoiceErrorMessage:
    """Test VoiceErrorMessage schema."""

    def test_valid_message(self):
        """Should create error message."""
        msg = VoiceErrorMessage(type="error", message="Something went wrong")
        assert msg.type == "error"


class TestTaskDoneRequest:
    """Test TaskDoneRequest schema."""

    def test_valid_request(self):
        """Should create request with all fields."""
        req = TaskDoneRequest(
            session_id="session-123",
            transcript_path="/tmp/transcript.txt",
            team_id="team1",
            role_id="pane-0"
        )
        assert req.session_id == "session-123"
        assert req.team_id == "team1"


class TestTaskDoneResponse:
    """Test TaskDoneResponse schema."""

    def test_success_response(self):
        """Should create success response with summary."""
        resp = TaskDoneResponse(
            success=True,
            summary="Done. Task completed.",
            command_id="cmd-123"
        )
        assert resp.success is True
        assert resp.summary == "Done. Task completed."

    def test_error_response(self):
        """Should create error response."""
        resp = TaskDoneResponse(
            success=False,
            error="Processing failed"
        )
        assert resp.success is False
        assert resp.error == "Processing failed"

    def test_minimal_response(self):
        """Should create response with only required field."""
        resp = TaskDoneResponse(success=True)
        assert resp.success is True
        assert resp.summary is None
        assert resp.error is None
