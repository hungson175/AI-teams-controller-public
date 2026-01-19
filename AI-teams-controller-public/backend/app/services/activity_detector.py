"""Activity detection for tmux panes (Sprint 2 Tech Debt).

Extracted from TmuxService to reduce complexity.
Handles background polling and activity detection based on pane output changes.
"""

import logging
import threading
import time
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class ActivityDetector:
    """Detects activity in tmux panes by comparing output snapshots.

    Features:
    - Background polling thread that monitors all panes
    - Last-20-lines comparison for efficient activity detection
    - Per-pane activity tracking with separate state
    - Error resilience in background loop

    Sprint 29: This enables bulk endpoint to return correct isActive status
    for all roles by building history through background polling.
    """

    def __init__(self, poll_interval: int = 5):
        """Initialize ActivityDetector.

        Args:
            poll_interval: Seconds between background polls
        """
        self.poll_interval = poll_interval
        # Store previous pane output for activity detection (Sprint 29)
        self._previous_pane_output: dict[str, str] = {}
        # Background polling thread
        self._polling_thread: Optional[threading.Thread] = None
        self._stop_polling = threading.Event()

    def start_background_polling(self, poll_callback: Callable[[], None]):
        """Start background thread to poll all panes for activity detection.

        Sprint 29: Builds history for ALL panes so bulk endpoint returns
        correct isActive for all roles, not just previously-polled ones.

        Args:
            poll_callback: Function to call on each poll cycle (should call poll_all_panes)
        """
        if self._polling_thread is not None and self._polling_thread.is_alive():
            logger.warning("[ActivityDetector] Background polling already running")
            return

        self._stop_polling.clear()
        self._polling_thread = threading.Thread(
            target=self._poll_loop,
            args=(poll_callback,),
            daemon=True,
            name="tmux-activity-poller"
        )
        self._polling_thread.start()
        logger.info(f"[ActivityDetector] Background polling started (interval={self.poll_interval}s)")

    def stop_background_polling(self):
        """Stop background polling thread."""
        self._stop_polling.set()
        if self._polling_thread is not None:
            self._polling_thread.join(timeout=2)
            logger.info("[ActivityDetector] Background polling stopped")

    def _poll_loop(self, poll_callback: Callable[[], None]):
        """Background loop that polls all panes every poll_interval seconds.

        Args:
            poll_callback: Function to call on each poll cycle
        """
        while not self._stop_polling.is_set():
            try:
                poll_callback()
            except Exception as e:
                # Log but don't crash - background task must be resilient
                logger.error(f"[ActivityDetector] Background poll error: {e}")

            # Wait for next poll interval (check stop event frequently)
            for _ in range(self.poll_interval * 10):
                if self._stop_polling.is_set():
                    return
                time.sleep(0.1)

    def get_pane_activity(
        self,
        team_id: str,
        pane_index: str,
        capture_output: str,
        success: bool
    ) -> bool:
        """Get activity status for a pane by comparing last 20 lines.

        Sprint 29: Used by get_roles() to avoid circular dependency.
        Compares current last-20-lines with previous snapshot.

        Args:
            team_id: Team/session identifier
            pane_index: Pane index within team
            capture_output: Current pane output from tmux capture-pane
            success: Whether the capture was successful

        Returns:
            True if pane content changed since last check, False otherwise
        """
        if not success:
            return False

        # Extract last 20 lines for comparison
        key = f"{team_id}-pane-{pane_index}"
        lines = capture_output.strip().split("\n")
        last_20_lines = "\n".join(lines[-20:]) if len(lines) > 20 else capture_output
        previous_last_20 = self._previous_pane_output.get(key)
        is_active = previous_last_20 is not None and last_20_lines != previous_last_20
        self._previous_pane_output[key] = last_20_lines

        return is_active

    def get_last_output(self, team_id: str, role_id: str) -> Optional[str]:
        """Get the last captured output for a pane.

        Args:
            team_id: Team/session identifier
            role_id: Role identifier (e.g., "pane-0")

        Returns:
            Last captured output or None if not found
        """
        key = f"{team_id}-{role_id}"
        return self._previous_pane_output.get(key)

    def clear_history(self, team_id: str, role_id: str):
        """Clear activity history for a pane.

        Args:
            team_id: Team/session identifier
            role_id: Role identifier (e.g., "pane-0")
        """
        key = f"{team_id}-{role_id}"
        self._previous_pane_output.pop(key, None)
