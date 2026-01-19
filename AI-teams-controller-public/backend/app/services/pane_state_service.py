"""Pane state service - handles get/send operations for tmux panes.

Sprint 6 - SRP extraction: Separated from TmuxService to follow
Single Responsibility Principle. TmuxService handles lifecycle,
PaneStateService handles pane state and messaging.
"""

import logging
import time
from datetime import datetime
from typing import Optional

from app.services.activity_detector import ActivityDetector
from app.services.message_tracker import MessageTracker
from app.services.tmux_runner import TmuxRunner

logger = logging.getLogger(__name__)


class PaneStateService:
    """Handles pane state operations (get state, send messages).

    Responsibilities:
    - Get pane output/state
    - Send messages to panes
    - Track message highlights
    - Detect pane activity

    Does NOT handle:
    - Team lifecycle (kill, restart, create) - TmuxService
    - Listing teams/roles - TmuxService
    """

    def __init__(
        self,
        capture_lines: int = 100,
        activity_detector: Optional[ActivityDetector] = None,
        message_tracker: Optional[MessageTracker] = None
    ):
        """Initialize PaneStateService.

        Args:
            capture_lines: Number of lines to capture from pane output
            activity_detector: Optional ActivityDetector instance (creates new if None)
            message_tracker: Optional MessageTracker instance (creates new if None)
        """
        self.capture_lines = capture_lines
        self._activity_detector = activity_detector or ActivityDetector()
        self._message_tracker = message_tracker or MessageTracker()

    def set_capture_lines(self, lines: int) -> None:
        """Set the number of lines to capture from pane output.

        Args:
            lines: Number of lines to capture (typically 50-500)
        """
        self.capture_lines = lines

    def _get_pane_index(self, team_id: str, role_id: str) -> Optional[str]:
        """Get the tmux pane index for a role_id.

        Args:
            team_id: tmux session name
            role_id: API role ID like "pane-0", "pane-1"

        Returns:
            pane index (like "0", "1") or None if not found
        """
        # Get basic roles without activity checks
        success, output = TmuxRunner.run(["has-session", "-t", team_id])
        if not success:
            return None

        success, output = TmuxRunner.run([
            "list-panes", "-t", team_id,
            "-F", "#{pane_index}|#{pane_id}|#{pane_title}"
        ])

        if not success or not output:
            return None

        for line in output.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|", 2)
            pane_index = parts[0]
            api_role_id = f"pane-{pane_index}"

            if api_role_id == role_id:
                return pane_index

        return None

    def get_pane_state(self, team_id: str, role_id: str) -> dict:
        """Get the current output of a pane using tmux capture-pane.

        Includes activity detection:
        - isActive: True if pane content changed since last check (role is working)
        - isActive: False if pane content is same as last check (role is idle)

        Args:
            team_id: tmux session name
            role_id: API role ID like "pane-0"

        Returns:
            dict with output, lastUpdated, highlightText, isActive
        """
        pane_index = self._get_pane_index(team_id, role_id)

        if pane_index is None:
            return {
                "output": f"Pane not found: {role_id} in {team_id}",
                "lastUpdated": datetime.now().strftime("%H:%M:%S"),
                "highlightText": None,
                "isActive": False,
            }

        # Format: session:window.pane (window defaults to 0)
        target = f"{team_id}:0.{pane_index}"

        # Capture pane content
        success, output = TmuxRunner.run([
            "capture-pane",
            "-t", target,
            "-p",  # Print to stdout
            "-e",  # Include escape sequences (ANSI colors)
            "-J",  # Join wrapped lines (preserve real newlines only)
            "-S", f"-{self.capture_lines}",  # Start from N lines back
        ])

        if not success:
            output = f"Failed to capture pane: {output}"

        # P0 Quick fix: Filter out shell noise (mermaid/syntax errors from shell init)
        filtered_lines = []
        for line in output.strip().split("\n"):
            # Skip lines with shell noise patterns
            if any(pattern in line.lower() for pattern in ["mermaid", "syntax error", "index mem"]):
                continue
            filtered_lines.append(line)
        output = "\n".join(filtered_lines)

        # Activity detection
        is_active = self._activity_detector.get_pane_activity(
            team_id=team_id,
            pane_index=pane_index,
            capture_output=output,
            success=True
        )

        # Get highlight text if we sent a message
        highlight_text = self._message_tracker.get_highlight_text(team_id, role_id)

        return {
            "output": output,
            "lastUpdated": datetime.now().strftime("%H:%M:%S"),
            "highlightText": highlight_text,
            "isActive": is_active,
        }

    def send_message(self, team_id: str, role_id: str, message: str) -> dict:
        """Send a message to a specific pane using tmux send-keys.

        Uses the Two-Enter Rule: sends message, waits, sends Enter twice.
        Special keys (Escape, etc.) are sent directly without Enter.

        Args:
            team_id: tmux session name
            role_id: API role ID like "pane-0"
            message: Message to send

        Returns:
            dict with success, message, sentAt
        """
        pane_index = self._get_pane_index(team_id, role_id)
        if pane_index is None:
            return {
                "success": False,
                "message": f"Pane not found: {role_id} in {team_id}",
                "sentAt": datetime.now().isoformat(),
            }

        # Format: session:window.pane (window defaults to 0)
        target = f"{team_id}:0.{pane_index}"

        # Handle special keys (Escape character \x1b)
        if message == "\x1b":
            success, output = TmuxRunner.run(["send-keys", "-t", target, "Escape"])
            if not success:
                return {
                    "success": False,
                    "message": f"Failed to send Escape: {output}",
                    "sentAt": datetime.now().isoformat(),
                }
            return {
                "success": True,
                "message": f"Escape key sent to {role_id} in {team_id}",
                "sentAt": datetime.now().isoformat(),
            }

        # Send the message text
        success, output = TmuxRunner.run(["send-keys", "-t", target, message])
        if not success:
            return {
                "success": False,
                "message": f"Failed to send message: {output}",
                "sentAt": datetime.now().isoformat(),
            }

        # Send first Enter
        TmuxRunner.run(["send-keys", "-t", target, "Enter"])

        # Small delay then second Enter (Two-Enter Rule)
        time.sleep(0.5)
        TmuxRunner.run(["send-keys", "-t", target, "Enter"])

        # Track sent message for highlighting
        self._message_tracker.track_message(team_id, role_id, message)

        return {
            "success": True,
            "message": f"Message sent to {role_id} in {team_id}",
            "sentAt": datetime.now().isoformat(),
        }
