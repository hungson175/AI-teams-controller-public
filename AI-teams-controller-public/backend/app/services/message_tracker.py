"""Message tracking for sent messages and highlight text (Sprint 2 Tech Debt).

Extracted from TmuxService to reduce complexity.
Tracks messages sent to panes and provides highlight text for UI.
"""

from datetime import datetime


class MessageTracker:
    """Tracks messages sent to tmux panes for UI highlighting.

    Features:
    - Store sent messages with timestamps
    - Generate highlight text in format: "BOSS [HH:MM]: message"
    - Per-pane message tracking
    - Latest message overwrites previous (one message per pane)
    """

    def __init__(self):
        """Initialize MessageTracker."""
        # Store sent messages: key = "team_id-role_id", value = {message, timestamp}
        self._sent_messages: dict[str, dict[str, str]] = {}

    def track_message(self, team_id: str, role_id: str, message: str):
        """Track a sent message for highlight display.

        Args:
            team_id: Team/session identifier
            role_id: Role identifier (e.g., "pane-0")
            message: Message content that was sent
        """
        key = f"{team_id}-{role_id}"
        timestamp = datetime.now().strftime("%H:%M")
        self._sent_messages[key] = {"message": message, "timestamp": timestamp}

    def get_highlight_text(self, team_id: str, role_id: str) -> str | None:
        """Get highlight text for a pane if message was sent.

        Args:
            team_id: Team/session identifier
            role_id: Role identifier (e.g., "pane-0")

        Returns:
            Formatted highlight text or None if no message tracked
        """
        key = f"{team_id}-{role_id}"
        last_message = self._sent_messages.get(key)

        if last_message:
            return f"BOSS [{last_message['timestamp']}]: {last_message['message']}"

        return None

    def clear_message(self, team_id: str, role_id: str):
        """Clear tracked message for a pane.

        Args:
            team_id: Team/session identifier
            role_id: Role identifier (e.g., "pane-0")
        """
        key = f"{team_id}-{role_id}"
        self._sent_messages.pop(key, None)
