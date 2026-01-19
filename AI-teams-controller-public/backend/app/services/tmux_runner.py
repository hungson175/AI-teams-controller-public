"""Tmux command execution utility (Sprint 2 Tech Debt).

Extracted from TmuxService to reduce complexity.
Provides simple, reusable interface for running tmux commands.
"""

import subprocess
from typing import Tuple


class TmuxRunner:
    """Utility class for executing tmux commands.

    Features:
    - Simple interface: run(args) -> (success, output)
    - Timeout protection (5 seconds)
    - Error handling for common failures (timeout, binary not found)
    - Stateless - can be used as a module-level utility

    This is a thin wrapper around subprocess.run for tmux commands.
    """

    @staticmethod
    def run(args: list[str], timeout: int = 5) -> Tuple[bool, str]:
        """Run a tmux command and return (success, output).

        Args:
            args: Command arguments (without 'tmux' prefix)
            timeout: Command timeout in seconds (default: 5)

        Returns:
            Tuple of (success: bool, output: str)
            - success: True if returncode == 0, False otherwise
            - output: stdout on success, error message on failure

        Examples:
            >>> TmuxRunner.run(["list-sessions"])
            (True, "session1\\nsession2")

            >>> TmuxRunner.run(["has-session", "-t", "myteam"])
            (True, "")
        """
        try:
            result = subprocess.run(
                ["tmux"] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except FileNotFoundError:
            return False, "tmux not found"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def capture_pane(target: str, lines: int = 100, include_ansi: bool = True) -> Tuple[bool, str]:
        """Convenience method for capturing pane content.

        Args:
            target: Tmux target (e.g., "session:0.1" or "%17")
            lines: Number of lines to capture from pane history
            include_ansi: Whether to include ANSI escape sequences

        Returns:
            Tuple of (success: bool, output: str)
        """
        args = [
            "capture-pane",
            "-t", target,
            "-p",  # Print to stdout
            "-J",  # Join wrapped lines
            "-S", f"-{lines}",  # Start from N lines back
        ]

        if include_ansi:
            args.append("-e")  # Include escape sequences

        return TmuxRunner.run(args)

    @staticmethod
    def send_keys(target: str, *keys: str) -> Tuple[bool, str]:
        """Convenience method for sending keys to a pane.

        Args:
            target: Tmux target (e.g., "session:0.1")
            *keys: Keys to send (can be text or special keys like "Enter")

        Returns:
            Tuple of (success: bool, output: str)
        """
        args = ["send-keys", "-t", target] + list(keys)
        return TmuxRunner.run(args)
