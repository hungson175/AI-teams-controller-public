"""Abstract base class for team services - Strategy Pattern."""

from abc import ABC, abstractmethod
from typing import Optional


class TeamService(ABC):
    """Abstract interface for team services.

    Implementations:
    - MockDataService: Returns mock data for testing/development
    - TmuxService: Real tmux integration for production
    """

    @abstractmethod
    def get_teams(self) -> list[dict]:
        """Get all teams (tmux sessions)."""
        pass

    @abstractmethod
    def get_roles(self, team_id: str) -> list[dict]:
        """Get all roles (tmux panes) for a team."""
        pass

    @abstractmethod
    def send_message(self, team_id: str, role_id: str, message: str) -> dict:
        """Send a message to a specific pane."""
        pass

    @abstractmethod
    def get_pane_state(self, team_id: str, role_id: str) -> dict:
        """Get the current state/output of a pane."""
        pass

    @abstractmethod
    def set_capture_lines(self, lines: int) -> None:
        """Set the number of lines to capture from pane output.

        Args:
            lines: Number of lines to capture (typically 50-500)
        """
        pass

    # ========== Commander Epic: Team Lifecycle Management ==========

    @abstractmethod
    def kill_team(self, team_id: str) -> dict:
        """Kill a tmux session.

        Returns dict with success, message fields.
        """
        pass

    @abstractmethod
    def restart_team(self, team_id: str) -> dict:
        """Kill and restart a tmux session.

        Returns dict with success, message, setupScriptRun fields.
        """
        pass

    @abstractmethod
    def create_terminal(self, name: Optional[str] = None, directory: Optional[str] = None) -> dict:
        """Create a new terminal session.

        Args:
            name: Optional session name. Auto-generated if not provided.
            directory: Optional starting directory. Defaults to home directory.

        Returns dict with success, teamId, message fields.
        """
        pass

    # ========== Load Team Button: Browse & Load Existing Teams ==========

    @abstractmethod
    def list_available_teams(self) -> list[dict]:
        """List available team directories that can be loaded.

        Scans docs/tmux/ for team directories with setup-team.sh scripts.

        Returns list of dicts with: name, path, hasSetupScript, isActive
        """
        pass
