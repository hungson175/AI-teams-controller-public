"""Real tmux service - implements TeamService with actual tmux commands."""

import logging
import os
import re
import subprocess
import time
from datetime import datetime
from typing import Optional

from app.services.base import TeamService
from app.services.activity_detector import ActivityDetector
from app.services.message_tracker import MessageTracker
from app.services.team_lifecycle_manager import TeamLifecycleManager
from app.services.tmux_runner import TmuxRunner
from app.services.pane_state_service import PaneStateService

logger = logging.getLogger(__name__)


class TmuxService(TeamService):
    """Real tmux integration for production use."""

    def __init__(self, capture_lines: int = 100, poll_interval: int = 5):
        """Initialize TmuxService.

        Args:
            capture_lines: Number of lines to capture from pane output
            poll_interval: Seconds between background polls for activity detection
        """
        self.capture_lines = capture_lines
        # Activity detection (Sprint 2 refactor: extracted to ActivityDetector)
        self._activity_detector = ActivityDetector(poll_interval=poll_interval)
        # Message tracking (Sprint 2 refactor: extracted to MessageTracker)
        self._message_tracker = MessageTracker()
        # Team lifecycle (Sprint 3 refactor: extracted to TeamLifecycleManager)
        self._lifecycle_manager = TeamLifecycleManager()
        # Pane state operations (Sprint 6 refactor: extracted to PaneStateService)
        self._pane_state_service = PaneStateService(
            capture_lines=capture_lines,
            activity_detector=self._activity_detector,
            message_tracker=self._message_tracker
        )

    def start_background_polling(self):
        """Start background thread to poll all panes for activity detection.

        Sprint 29: Builds history for ALL panes so bulk endpoint returns
        correct isActive for all roles, not just previously-polled ones.
        """
        self._activity_detector.start_background_polling(self._poll_all_panes)

    def stop_background_polling(self):
        """Stop background polling thread."""
        self._activity_detector.stop_background_polling()

    def _poll_all_panes(self):
        """Poll all panes across all teams to build activity history."""
        teams = self.get_teams()
        for team in teams:
            team_id = team["id"]
            roles = self._get_roles_basic(team_id)
            for role in roles:
                pane_index = role["_pane_index"]
                # Capture and store - this builds the history
                self._get_pane_activity(team_id, pane_index)

    def _get_pane_role_name(self, team_id: str, pane_index: str) -> Optional[str]:
        """Get the @role_name user option from a tmux pane.

        This is stable - won't be overwritten by processes like Claude Code.
        Set with: tmux set-option -p -t session:window.pane @role_name "PM"
        """
        target = f"{team_id}:0.{pane_index}"
        success, output = self._run_tmux([
            "show-option", "-p", "-t", target, "-v", "@role_name"
        ])
        if success and output:
            return output.strip()
        return None

    def _run_tmux(self, args: list[str]) -> tuple[bool, str]:
        """Run a tmux command and return (success, output).

        Sprint 2 refactor: Delegates to TmuxRunner utility class.
        """
        return TmuxRunner.run(args)

    def get_teams(self) -> list[dict]:
        """Get all tmux sessions as teams.

        Includes isActive field (true if any pane in team has recent activity).
        """
        success, output = self._run_tmux(["list-sessions", "-F", "#{session_name}"])

        if not success or not output:
            return []

        sessions = output.strip().split("\n")
        teams = []

        for session in sessions:
            if not session:
                continue

            # Check if any role in this team is active
            roles = self.get_roles(session)
            is_active = any(role.get("isActive", False) for role in roles)

            teams.append({
                "id": session,
                "name": session,
                "isActive": is_active
            })

        return teams

    def _get_roles_basic(self, team_id: str) -> list[dict]:
        """Get roles without activity status (used internally to avoid circular deps)."""
        # First check if session exists
        success, _ = self._run_tmux(["has-session", "-t", team_id])
        if not success:
            return []

        # Get panes with their indices, IDs, and titles
        success, output = self._run_tmux([
            "list-panes", "-t", team_id,
            "-F", "#{pane_index}|#{pane_id}|#{pane_title}"
        ])

        if not success or not output:
            return []

        roles = []
        for line in output.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|", 2)
            pane_index = parts[0]
            pane_id = parts[1] if len(parts) > 1 else None
            pane_title = parts[2] if len(parts) > 2 and parts[2] else f"Pane {pane_index}"
            role_id = f"pane-{pane_index}"
            role_name = self._get_pane_role_name(team_id, pane_index) or pane_title

            roles.append({
                "id": role_id,
                "name": role_name,
                "order": int(pane_index) + 1,
                "_pane_index": pane_index,
                "_pane_id": pane_id,
            })

        return roles

    def get_roles(self, team_id: str) -> list[dict]:
        """Get all panes in a tmux session as roles.

        Uses stable pane index as role ID (pane-0, pane-1, etc.) since
        pane titles change dynamically when Claude Code runs tasks.

        Includes isActive for each role (Sprint 29) based on last-20-lines comparison.
        """
        roles = self._get_roles_basic(team_id)

        # Add activity status for each role (Sprint 29)
        for role in roles:
            role["isActive"] = self._get_pane_activity(team_id, role["_pane_index"])

        return roles

    def _get_pane_target(self, team_id: str, role_id: str) -> Optional[str]:
        """Get the tmux pane_id target for a role_id.

        Args:
            team_id: tmux session name
            role_id: API role ID like "pane-0", "pane-1"

        Returns:
            pane_id (like %17) which works directly as tmux target
        """
        # If role_id is already a pane_id (starts with %), use it directly
        if role_id.startswith("%"):
            return role_id

        # Look up the actual pane_id from roles (use basic to avoid activity checks)
        roles = self._get_roles_basic(team_id)
        for role in roles:
            if role["id"] == role_id:
                return role.get("_pane_id")
        return None

    def _get_pane_index(self, team_id: str, role_id: str) -> Optional[str]:
        """Get the tmux pane index for a role_id (legacy, for compatibility)."""
        roles = self._get_roles_basic(team_id)
        for role in roles:
            if role["id"] == role_id:
                return role.get("_pane_index")
        return None

    def _get_pane_activity(self, team_id: str, pane_index: str) -> bool:
        """Get activity status for a pane by comparing last 20 lines.

        Sprint 29: Used by get_roles() to avoid circular dependency.
        Compares current last-20-lines with previous snapshot.
        """
        target = f"{team_id}:0.{pane_index}"
        success, output = self._run_tmux([
            "capture-pane", "-t", target, "-p", "-e", "-J", "-S", f"-{self.capture_lines}"
        ])

        return self._activity_detector.get_pane_activity(
            team_id=team_id,
            pane_index=pane_index,
            capture_output=output,
            success=success
        )

    def send_message(self, team_id: str, role_id: str, message: str) -> dict:
        """Send a message to a specific pane using tmux send-keys.

        Sprint 6: Delegates to PaneStateService (SRP separation).
        """
        return self._pane_state_service.send_message(team_id, role_id, message)

    def set_capture_lines(self, lines: int) -> None:
        """Set the number of lines to capture from pane output.

        Sprint 6 - DIP fix: Provides method interface instead of direct attribute access.

        Args:
            lines: Number of lines to capture (typically 50-500)
        """
        self.capture_lines = lines
        self._pane_state_service.set_capture_lines(lines)

    def get_pane_state(self, team_id: str, role_id: str) -> dict:
        """Get the current output of a pane using tmux capture-pane.

        Sprint 6: Delegates to PaneStateService (SRP separation).
        """
        return self._pane_state_service.get_pane_state(team_id, role_id)

    # ========== Commander Epic: Team Lifecycle Management ==========
    # Sprint 3: Delegated to TeamLifecycleManager

    def kill_team(self, team_id: str) -> dict:
        """Kill a tmux session.

        Sprint 3: Facade - delegates to TeamLifecycleManager.
        """
        return self._lifecycle_manager.kill_team(team_id)

    def restart_team(self, team_id: str) -> dict:
        """Kill a tmux session and run its setup script if available.

        Sprint 3: Facade - delegates to TeamLifecycleManager.
        """
        return self._lifecycle_manager.restart_team(team_id)

    def restart_role(self, team_id: str, role: str) -> dict:
        """Restart a specific role within a team.

        Work Item 1: Per-role restart - delegates to TeamLifecycleManager.
        """
        return self._lifecycle_manager.restart_role(team_id, role)

    def create_terminal(self, name: Optional[str] = None, directory: Optional[str] = None) -> dict:
        """Create a new tmux session (terminal) in the specified directory.

        Sprint 3: Facade - delegates to TeamLifecycleManager.
        """
        return self._lifecycle_manager.create_terminal(name, directory)

    def list_available_teams(self) -> list[dict]:
        """List available team directories from docs/tmux/.

        Sprint 3: Facade - delegates to TeamLifecycleManager.
        """
        return self._lifecycle_manager.list_available_teams()


# Singleton instance
tmux_service = TmuxService()
