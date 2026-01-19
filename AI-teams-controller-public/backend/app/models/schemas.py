from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Team(BaseModel):
    id: str
    name: str
    isActive: bool = False  # True if any pane in team has recent activity


class Role(BaseModel):
    id: str
    name: str
    order: int
    isActive: bool = False  # Sprint 29: True if pane content changed since last check


class TeamsResponse(BaseModel):
    teams: list[Team]


class RolesResponse(BaseModel):
    teamId: str
    roles: list[Role]


class SendMessageRequest(BaseModel):
    message: str


class SendMessageResponse(BaseModel):
    success: bool
    message: str
    sentAt: str


class LastMessage(BaseModel):
    message: str
    timestamp: str


class PaneStateResponse(BaseModel):
    output: str
    lastUpdated: str
    highlightText: Optional[str] = None
    isActive: bool = False  # Sprint 29: True if pane content changed since last check


# Commander Epic - Team Lifecycle Management (Story 1)
class TeamActionResponse(BaseModel):
    """Response for kill_team and restart_team actions."""
    success: bool
    message: str
    setupScriptRun: Optional[bool] = None  # Only set for restart_team


class CreateTerminalRequest(BaseModel):
    """Request for creating a new terminal session."""
    name: Optional[str] = None  # Auto-generate if not provided
    directory: Optional[str] = None  # Starting directory (default: home)


class CreateTerminalResponse(BaseModel):
    """Response for create_terminal action."""
    success: bool
    teamId: str
    message: str


# Team Creator Epic - Template Management (Story 4)
class TemplateRole(BaseModel):
    """Role definition within a template."""
    id: str
    name: str
    description: str
    optional: bool = False


class TeamTemplate(BaseModel):
    """Team template metadata."""
    name: str
    display_name: str
    description: str
    version: str
    roles: list[TemplateRole]


class TemplatesResponse(BaseModel):
    """Response for list_templates endpoint."""
    templates: list[TeamTemplate]


class CreateTeamRequest(BaseModel):
    """Request for creating a team from template."""
    template_name: str
    project_name: str
    prd: str  # Project Requirements Document


class CreateTeamResponse(BaseModel):
    """Response for create_team endpoint."""
    success: bool
    team_id: str
    message: str
    output_dir: str


# Load Team Button - Browse & Load Existing Teams (Story 1)
class AvailableTeam(BaseModel):
    """Available team directory for loading."""
    name: str                    # Directory name (e.g., "ai_controller_full_team")
    path: str                    # Relative path from project root (e.g., "docs/tmux/ai_controller_full_team")
    hasSetupScript: bool         # Whether setup-team.sh exists
    isActive: bool              # Whether team is running (tmux session exists)


class ListAvailableTeamsResponse(BaseModel):
    """Response for list_available_teams endpoint."""
    teams: list[AvailableTeam]
