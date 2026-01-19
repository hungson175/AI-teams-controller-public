#!/usr/bin/env python3
"""
Unit tests for session_start_team_docs.py hook.

Tests all acceptance criteria from SPEC_session_start_team_docs.md
"""
import json
import os
import sys
import subprocess
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from io import StringIO

# Add parent directory to path to import the hook
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the hook module
import session_start_team_docs


class TestSessionStartTeamDocs(unittest.TestCase):
    """Test suite for session_start_team_docs hook."""

    def setUp(self):
        """Set up test fixtures."""
        self.hook_path = Path(__file__).parent.parent / "session_start_team_docs.py"
        self.sample_input = {
            "session_id": "test-session-123",
            "transcript_path": "/tmp/test_transcript.txt"
        }

    def run_hook(self, stdin_data, env=None):
        """
        Run the hook script with given stdin data and environment.

        Returns: (stdout, stderr, returncode)
        """
        if not self.hook_path.exists():
            # Hook not implemented yet - this is TDD, so test should fail initially
            raise FileNotFoundError(f"Hook not found: {self.hook_path}")

        env_vars = os.environ.copy()
        if env:
            env_vars.update(env)

        result = subprocess.run(
            [sys.executable, str(self.hook_path)],
            input=json.dumps(stdin_data),
            capture_output=True,
            text=True,
            env=env_vars
        )
        return result.stdout, result.stderr, result.returncode

    # ========================================================================
    # AC1: Detect Role Correctly
    # ========================================================================

    @patch.dict(os.environ, {"TMUX_PANE": "%42"})
    @patch("session_start_team_docs.subprocess.run")
    def test_ac1_reads_role_from_tmux_pane_env(self, mock_run):
        """AC1: Hook reads $TMUX_PANE environment variable."""
        # Setup mock to return role
        mock_run.return_value = MagicMock(
            stdout="QA",
            stderr="",
            returncode=0
        )

        # Call get_role directly
        role = session_start_team_docs.get_role()

        # Verify role was retrieved
        self.assertEqual(role, "QA")

        # Verify tmux command was called with correct arguments
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], "tmux")
        self.assertEqual(call_args[1], "show-options")
        self.assertIn("-pt", call_args)
        self.assertIn("%42", call_args)
        self.assertIn("@role_name", call_args)

    @patch.dict(os.environ, {"TMUX_PANE": "%42"})
    @patch("session_start_team_docs.subprocess.run")
    def test_ac1_uses_correct_tmux_command(self, mock_run):
        """AC1: Hook uses 'tmux show-options -pt $TMUX_PANE -qv @role_name'."""
        mock_run.return_value = MagicMock(stdout="QA", returncode=0)

        session_start_team_docs.get_role()

        # Verify exact command structure
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args, ["tmux", "show-options", "-pt", "%42", "-qv", "@role_name"])

    @patch.dict(os.environ, {"TMUX_PANE": "%42"})
    @patch("session_start_team_docs.subprocess.run")
    def test_ac1_exits_without_blocking_when_no_role(self, mock_run):
        """AC1: If role is empty, hook exits without blocking."""
        # Mock tmux to return empty role
        mock_run.return_value = MagicMock(
            stdout="",  # Empty role
            stderr="",
            returncode=0
        )

        role = session_start_team_docs.get_role()
        should_act, reason = session_start_team_docs.should_activate(role, "command-center")

        # Should not activate when role is empty
        self.assertFalse(should_act)
        self.assertIn("No role", reason)

    # ========================================================================
    # AC2: Detect Team Context
    # ========================================================================

    @patch.dict(os.environ, {"TMUX_PANE": "%42"})
    def test_ac2_exits_when_not_command_center(self):
        """AC2: Hook exits without blocking if not in command-center."""
        with patch("subprocess.run") as mock_run:
            def mock_subprocess(cmd, *args, **kwargs):
                if "@role_name" in cmd:
                    return MagicMock(stdout="QA", returncode=0)
                elif "session_name" in str(cmd):
                    return MagicMock(stdout="other-session", returncode=0)
                return MagicMock(stdout="", returncode=0)

            mock_run.side_effect = mock_subprocess

            try:
                stdout, stderr, returncode = self.run_hook(
                    self.sample_input,
                    env={"TMUX_PANE": "%42"}
                )

                # Should exit cleanly without blocking
                self.assertEqual(returncode, 0, "Should exit with code 0 for other sessions")
                output_data = json.loads(stdout) if stdout.strip() else {}
                self.assertNotEqual(
                    output_data.get("decision"),
                    "block",
                    "Should NOT block when not in command-center"
                )
            except FileNotFoundError:
                self.skipTest("Hook not implemented yet (TDD)")

    @patch.dict(os.environ, {"TMUX_PANE": "%42"})
    def test_ac2_activates_only_for_command_center(self):
        """AC2: Hook only activates for command-center team."""
        with patch("subprocess.run") as mock_run:
            def mock_subprocess(cmd, *args, **kwargs):
                if "@role_name" in cmd:
                    return MagicMock(stdout="QA", returncode=0)
                elif "session_name" in str(cmd):
                    return MagicMock(stdout="command-center", returncode=0)
                return MagicMock(stdout="", returncode=0)

            mock_run.side_effect = mock_subprocess

            try:
                stdout, stderr, returncode = self.run_hook(
                    self.sample_input,
                    env={"TMUX_PANE": "%42"}
                )

                # Should block for command-center with role
                output_data = json.loads(stdout) if stdout.strip() else {}
                self.assertEqual(
                    output_data.get("decision"),
                    "block",
                    "Should block for command-center team"
                )
            except FileNotFoundError:
                self.skipTest("Hook not implemented yet (TDD)")

    # ========================================================================
    # AC3: Block with Mandatory Instructions
    # ========================================================================

    @patch.dict(os.environ, {"TMUX_PANE": "%42"})
    def test_ac3_blocks_with_correct_json_format(self):
        """AC3: Hook outputs JSON with {"decision": "block", "reason": "..."}."""
        with patch("subprocess.run") as mock_run:
            def mock_subprocess(cmd, *args, **kwargs):
                if "@role_name" in cmd:
                    return MagicMock(stdout="QA", returncode=0)
                elif "session_name" in str(cmd):
                    return MagicMock(stdout="command-center", returncode=0)
                return MagicMock(stdout="", returncode=0)

            mock_run.side_effect = mock_subprocess

            try:
                stdout, stderr, returncode = self.run_hook(
                    self.sample_input,
                    env={"TMUX_PANE": "%42"}
                )

                # Parse JSON output
                output_data = json.loads(stdout)

                # Verify JSON structure
                self.assertEqual(output_data.get("decision"), "block")
                self.assertIn("reason", output_data)
                self.assertIsInstance(output_data["reason"], str)
                self.assertTrue(len(output_data["reason"]) > 0)
            except FileNotFoundError:
                self.skipTest("Hook not implemented yet (TDD)")

    @patch.dict(os.environ, {"TMUX_PANE": "%42"})
    def test_ac3_reason_includes_exact_file_paths(self):
        """AC3: Reason includes exact file paths to read."""
        with patch("subprocess.run") as mock_run:
            def mock_subprocess(cmd, *args, **kwargs):
                if "@role_name" in cmd:
                    return MagicMock(stdout="SM", returncode=0)
                elif "session_name" in str(cmd):
                    return MagicMock(stdout="command-center", returncode=0)
                return MagicMock(stdout="", returncode=0)

            mock_run.side_effect = mock_subprocess

            try:
                stdout, stderr, returncode = self.run_hook(
                    self.sample_input,
                    env={"TMUX_PANE": "%42"}
                )

                output_data = json.loads(stdout)
                reason = output_data.get("reason", "")

                # Verify file paths are included
                self.assertIn("docs/tmux/command-center/prompts/SM_PROMPT.md", reason)
                self.assertIn("docs/tmux/command-center/workflow.md", reason)
            except FileNotFoundError:
                self.skipTest("Hook not implemented yet (TDD)")

    @patch.dict(os.environ, {"TMUX_PANE": "%42"})
    def test_ac3_reason_is_clear_and_actionable(self):
        """AC3: Reason is clear and actionable."""
        with patch("subprocess.run") as mock_run:
            def mock_subprocess(cmd, *args, **kwargs):
                if "@role_name" in cmd:
                    return MagicMock(stdout="FE", returncode=0)
                elif "session_name" in str(cmd):
                    return MagicMock(stdout="command-center", returncode=0)
                return MagicMock(stdout="", returncode=0)

            mock_run.side_effect = mock_subprocess

            try:
                stdout, stderr, returncode = self.run_hook(
                    self.sample_input,
                    env={"TMUX_PANE": "%42"}
                )

                output_data = json.loads(stdout)
                reason = output_data.get("reason", "")

                # Verify reason has clear instructions
                self.assertIn("Read", reason.lower())
                self.assertIn("before", reason.lower())
                # Should contain numbered steps or clear structure
                self.assertTrue("1." in reason or "2." in reason)
            except FileNotFoundError:
                self.skipTest("Hook not implemented yet (TDD)")

    # ========================================================================
    # AC4: Handle Race Conditions
    # ========================================================================

    @patch.dict(os.environ, {"TMUX_PANE": "%42"})
    def test_ac4_exits_gracefully_when_role_not_set(self):
        """AC4: If @role_name not set yet, hook exits gracefully."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="",  # Empty - role not set yet
                returncode=0
            )

            try:
                stdout, stderr, returncode = self.run_hook(
                    self.sample_input,
                    env={"TMUX_PANE": "%42"}
                )

                # Should exit cleanly
                self.assertEqual(returncode, 0)
                output_data = json.loads(stdout) if stdout.strip() else {}
                self.assertNotEqual(output_data.get("decision"), "block")
            except FileNotFoundError:
                self.skipTest("Hook not implemented yet (TDD)")

    # ========================================================================
    # AC5: Error Handling
    # ========================================================================

    @patch.dict(os.environ, {})  # No TMUX_PANE
    def test_ac5_handles_missing_tmux_pane_env(self):
        """AC5: On any error, hook exits without blocking."""
        try:
            stdout, stderr, returncode = self.run_hook(self.sample_input)

            # Should exit with error code but not block
            # (either 0 for graceful skip or 1 for error)
            self.assertIn(returncode, [0, 1], "Should exit cleanly on error")
            output_data = json.loads(stdout) if stdout.strip() else {}
            self.assertNotEqual(
                output_data.get("decision"),
                "block",
                "Should NOT block on error"
            )
        except FileNotFoundError:
            self.skipTest("Hook not implemented yet (TDD)")

    @patch.dict(os.environ, {"TMUX_PANE": "%42"})
    def test_ac5_handles_tmux_command_failure(self):
        """AC5: Handle tmux command failure gracefully."""
        with patch("subprocess.run") as mock_run:
            # Simulate tmux command failure
            mock_run.side_effect = subprocess.SubprocessError("tmux not found")

            try:
                stdout, stderr, returncode = self.run_hook(
                    self.sample_input,
                    env={"TMUX_PANE": "%42"}
                )

                # Should exit with error code but not block
                self.assertEqual(returncode, 1, "Should exit with error code on exception")
                output_data = json.loads(stdout) if stdout.strip() else {}
                self.assertNotEqual(
                    output_data.get("decision"),
                    "block",
                    "Should NOT block on error"
                )
            except FileNotFoundError:
                self.skipTest("Hook not implemented yet (TDD)")

    @patch.dict(os.environ, {"TMUX_PANE": "%42"})
    def test_ac5_logs_errors_to_stderr(self):
        """AC5: Errors logged to stderr."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Test error")

            try:
                stdout, stderr, returncode = self.run_hook(
                    self.sample_input,
                    env={"TMUX_PANE": "%42"}
                )

                # Error should be logged to stderr
                self.assertTrue(len(stderr) > 0, "Error should be logged to stderr")
                self.assertIn("error", stderr.lower(), "stderr should contain 'error'")
            except FileNotFoundError:
                self.skipTest("Hook not implemented yet (TDD)")


if __name__ == "__main__":
    unittest.main()
