# -*- coding: utf-8 -*-
"""Team lifecycle management - kill, restart, create, list teams.

Sprint 3 Tech Debt - Extracted from TmuxService to satisfy SRP.
Handles tmux session lifecycle operations.
"""

import logging
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.services.tmux_runner import TmuxRunner

logger = logging.getLogger(__name__)


class TeamLifecycleManager:
    """Manages team (tmux session) lifecycle operations.

    Extracted from TmuxService (Sprint 3) to satisfy Single Responsibility Principle.
    Handles: kill, restart, create, list available teams.

    Dependencies injected via constructor for testability.
    """

    def __init__(self):
        """Initialize TeamLifecycleManager."""
        pass  # Uses TmuxRunner static methods

    def _validate_team_exists(self, team_id: str) -> bool:
        """Validate that a team (tmux session) exists.

        Security: Prevents command injection by verifying team_id is valid.

        Args:
            team_id: Team/session name to validate

        Returns:
            True if session exists, False otherwise
        """
        success, _ = TmuxRunner.run(["has-session", "-t", team_id])
        return success

    def kill_team(self, team_id: str) -> dict:
        """Kill a tmux session.

        Args:
            team_id: The tmux session name to kill

        Returns:
            dict with success, message fields
        """
        # Security: Validate team exists first
        if not self._validate_team_exists(team_id):
            return {
                "success": False,
                "message": f"Team not found: {team_id}",
            }

        success, output = TmuxRunner.run(["kill-session", "-t", team_id])

        if success:
            logger.info(f"[TeamLifecycle] Killed session: {team_id}")
            return {
                "success": True,
                "message": f"Team '{team_id}' terminated",
            }
        else:
            logger.error(f"[TeamLifecycle] Failed to kill session {team_id}: {output}")
            return {
                "success": False,
                "message": f"Failed to kill team: {output}",
            }

    def restart_team(self, team_id: str) -> dict:
        """Kill a tmux session and run its setup script if available.

        Args:
            team_id: The tmux session name to restart

        Returns:
            dict with success, message, setupScriptRun fields
        """
        # Security: Validate team exists first
        if not self._validate_team_exists(team_id):
            return {
                "success": False,
                "message": f"Team not found: {team_id}",
                "setupScriptRun": False,
            }

        # Step 1: Kill the session
        kill_success, kill_output = TmuxRunner.run(["kill-session", "-t", team_id])
        if not kill_success:
            return {
                "success": False,
                "message": f"Failed to kill team: {kill_output}",
                "setupScriptRun": False,
            }

        logger.info(f"[TeamLifecycle] Killed session for restart: {team_id}")

        # Step 2: Find README for this team
        # Check both locations (matching project structure: docs/tmux/{team_id}/):
        # 1. ~/dev/tmux-teams/{team_id}/docs/tmux/{team_id}/ (teams created via Create Team UI)
        # 2. {project_root}/docs/tmux/{team_id}/ (manually created teams in this project)
        home_teams_path = os.path.join(
            os.path.expanduser("~"), "dev", "tmux-teams", team_id, "docs", "tmux", team_id, "README.md"
        )
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        project_teams_path = os.path.join(project_root, "docs", "tmux", team_id, "README.md")

        # Prefer ~/dev/tmux-teams/ location first
        if os.path.exists(home_teams_path):
            readme_path = home_teams_path
        else:
            readme_path = project_teams_path

        if not os.path.exists(readme_path):
            return {
                "success": True,
                "message": f"Team '{team_id}' killed (no README found)",
                "setupScriptRun": False,
            }

        # Step 3: Parse README for setup script
        setup_script = self._find_setup_script(readme_path)
        if not setup_script:
            return {
                "success": True,
                "message": f"Team '{team_id}' killed (no setup script in README)",
                "setupScriptRun": False,
            }

        # Step 4: Run setup script
        try:
            logger.info(f"[TeamLifecycle] Running setup script: {setup_script}")
            result = subprocess.run(
                ["bash", setup_script],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout for setup scripts
                cwd=os.path.dirname(setup_script),  # Run in script's directory
            )

            if result.returncode == 0:
                logger.info(f"[TeamLifecycle] Setup script completed successfully")
                return {
                    "success": True,
                    "message": f"Team '{team_id}' restarted successfully",
                    "setupScriptRun": True,
                }
            else:
                logger.error(f"[TeamLifecycle] Setup script failed: {result.stderr}")
                return {
                    "success": False,
                    "message": f"Setup script failed: {result.stderr[:200]}",
                    "setupScriptRun": True,
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Setup script timed out (60s)",
                "setupScriptRun": True,
            }
        except Exception as e:
            logger.error(f"[TeamLifecycle] Error running setup script: {e}")
            return {
                "success": False,
                "message": f"Error running setup script: {str(e)}",
                "setupScriptRun": True,
            }

    def restart_role(self, team_id: str, role: str) -> dict:
        """Restart a specific role within a team.

        Args:
            team_id: The tmux session name
            role: The role name (SM, PO, TL, FE, BE, QA)

        Returns:
            dict with success, role, pane_id, and message fields
        """
        # Step 1: Validate team exists
        if not self._validate_team_exists(team_id):
            return {
                "success": False,
                "message": f"Team '{team_id}' not found",
            }

        # Step 2: Find pane by @role_name
        success, output = TmuxRunner.run([
            "list-panes",
            "-t", team_id,
            "-F", "#{pane_id} #{@role_name}"
        ])

        if not success:
            return {
                "success": False,
                "message": f"Failed to list panes: {output}",
            }

        # Parse output to find matching role
        pane_id = None
        for line in output.strip().split('\n'):
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[1] == role:
                pane_id = parts[0]
                break

        if not pane_id:
            return {
                "success": False,
                "message": f"Role '{role}' not found in team '{team_id}'",
            }

        # Step 3: Model mapping (per TECH_SPEC)
        model_map = {
            "SM": "opus",
            "TL": "opus",
            "PO": "sonnet",
            "FE": "sonnet",
            "BE": "sonnet",
            "QA": "haiku",
        }
        model = model_map.get(role, "sonnet")  # Default to sonnet

        # Step 4: Send Ctrl+C to stop current process
        TmuxRunner.run(["send-keys", "-t", pane_id, "C-c"])

        # Step 5: Re-run claude command with appropriate model
        claude_cmd = f"claude --model {model}"
        TmuxRunner.run(["send-keys", "-t", pane_id, claude_cmd, "C-m"])

        # Step 6: Send /init-role command
        init_cmd = f"/init-role {role}"
        TmuxRunner.run(["send-keys", "-t", pane_id, init_cmd, "C-m"])

        logger.info(f"[TeamLifecycle] Restarted role '{role}' in team '{team_id}' (pane {pane_id})")

        return {
            "success": True,
            "role": role,
            "pane_id": pane_id,
            "message": f"Role '{role}' restarted successfully",
        }

    def create_terminal(self, name: Optional[str] = None, directory: Optional[str] = None) -> dict:
        """Create a new tmux session (terminal) in the specified directory.

        Args:
            name: Optional session name. Auto-generated if not provided.
            directory: Optional starting directory. Defaults to home directory.

        Returns:
            dict with success, teamId, message fields
        """
        # Auto-generate name if not provided
        if not name:
            name = f"terminal-{datetime.now().strftime('%H%M%S')}"

        # Sanitize name: only allow alphanumeric, hyphens, underscores
        sanitized_name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
        if not sanitized_name:
            return {
                "success": False,
                "teamId": "",
                "message": "Invalid terminal name (must contain alphanumeric characters)",
            }

        # Check if session already exists
        if self._validate_team_exists(sanitized_name):
            return {
                "success": False,
                "teamId": sanitized_name,
                "message": f"Session '{sanitized_name}' already exists",
            }

        # Use provided directory or default to home
        start_dir = directory if directory else os.path.expanduser("~")
        # Expand ~ if present in directory path
        start_dir = os.path.expanduser(start_dir)

        # Validate directory exists
        if not os.path.isdir(start_dir):
            return {
                "success": False,
                "teamId": "",
                "message": f"Directory does not exist: {start_dir}",
            }

        # Create new detached session in specified directory
        success, output = TmuxRunner.run([
            "new-session", "-d", "-s", sanitized_name, "-c", start_dir
        ])

        if success:
            logger.info(f"[TeamLifecycle] Created terminal session: {sanitized_name}")
            return {
                "success": True,
                "teamId": sanitized_name,
                "message": f"Terminal '{sanitized_name}' created",
            }
        else:
            logger.error(f"[TeamLifecycle] Failed to create terminal: {output}")
            return {
                "success": False,
                "teamId": "",
                "message": f"Failed to create terminal: {output}",
            }

    def list_available_teams(self) -> list[dict]:
        """List available team directories from docs/tmux/.

        Returns list of team directories, checking if they have setup-team.sh
        and if the team is currently active (tmux session exists).

        Return format:
        [
            {
                "name": "ai_controller_full_team",
                "path": "docs/tmux/ai_controller_full_team",
                "hasSetupScript": True,
                "isActive": True
            }
        ]
        """
        teams = []
        teams_dir = Path("docs/tmux")

        # Handle case where docs/tmux doesn't exist
        if not teams_dir.exists():
            logger.warning("[TeamLifecycle] docs/tmux directory not found")
            return []

        # Scan for team directories
        for entry in sorted(teams_dir.iterdir()):
            if not entry.is_dir():
                continue

            team_name = entry.name
            team_path = str(entry.relative_to(Path.cwd()))

            # Check if setup-team.sh exists
            setup_script = entry / "setup-team.sh"
            has_setup_script = setup_script.exists()

            # Check if team is active (tmux session exists)
            is_active = self._check_team_active(team_name)

            teams.append({
                "name": team_name,
                "path": team_path,
                "hasSetupScript": has_setup_script,
                "isActive": is_active,
            })

        # Sort: active teams first, then by name
        teams.sort(key=lambda t: (-t["isActive"], t["name"]))

        logger.info(f"[TeamLifecycle] Found {len(teams)} available teams")
        return teams

    def _check_team_active(self, team_name: str) -> bool:
        """Check if a team (tmux session) is currently active.

        Args:
            team_name: Team/session name to check

        Returns:
            True if session is running, False otherwise
        """
        success, output = TmuxRunner.run(["list-sessions", "-F", "#{session_name}"])
        if not success:
            return False

        active_sessions = output.strip().split("\n") if output else []
        return team_name in active_sessions

    def _find_setup_script(self, readme_path: str) -> Optional[str]:
        """Parse README to find setup script path.

        Looks for patterns like:
        - setup-team.sh
        - ./setup-team.sh
        - bash setup-team.sh

        Args:
            readme_path: Path to the README.md file

        Returns:
            Absolute path to setup script if found, None otherwise
        """
        if not os.path.exists(readme_path):
            return None

        try:
            with open(readme_path, "r") as f:
                content = f.read()

            # Look for setup script patterns in README
            # Pattern: setup-team.sh or ./setup-team.sh in code blocks or text
            patterns = [
                r"(?:bash\s+|\./)?(setup-team\.sh)",
                r"(?:bash\s+|\./)?(setup[_-]team\.sh)",
            ]

            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    script_name = match.group(1)
                    # Build absolute path relative to README location
                    readme_dir = os.path.dirname(readme_path)
                    script_path = os.path.join(readme_dir, script_name)
                    if os.path.exists(script_path):
                        return os.path.abspath(script_path)

            return None
        except Exception as e:
            logger.error(f"[TeamLifecycle] Error parsing README: {e}")
            return None
