# -*- coding: utf-8 -*-
"""Tests for skip_logic service.

Tests the fail-closed pattern for voice feedback filtering.
All tmux subprocess calls are mocked.

NOTE: get_pane_role() now uses `tmux show-options -p @role_name`
instead of `list-panes` with pane_title, because Claude Code
overwrites pane titles with task descriptions.
"""

import subprocess
from unittest.mock import patch, MagicMock

import pytest

from app.services.skip_logic import (
    get_allow_roles,
    get_skip_roles,
    get_pane_title,
    get_pane_role,
    should_skip_role,
)


class TestGetAllowRoles:
    """Tests for get_allow_roles() - Sprint 6."""

    def test_default_allow_roles_empty(self):
        """Should return empty list when env var not set."""
        with patch.dict("os.environ", {}, clear=True):
            roles = get_allow_roles()
            assert roles == []

    def test_single_allow_role(self):
        """Should parse single role from env."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": "PO"}):
            roles = get_allow_roles()
            assert roles == ["PO"]

    def test_multiple_allow_roles(self):
        """Should parse comma-separated roles from env."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": "PO,PM"}):
            roles = get_allow_roles()
            assert roles == ["PO", "PM"]

    def test_allow_roles_with_spaces(self):
        """Should trim whitespace from role names."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": " PO , PM "}):
            roles = get_allow_roles()
            assert roles == ["PO", "PM"]

    def test_empty_allow_roles(self):
        """Should return empty list for empty env var."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": ""}):
            roles = get_allow_roles()
            assert roles == []


class TestGetSkipRoles:
    """Tests for get_skip_roles()."""

    def test_default_skip_roles(self):
        """Should return DK as default skip role."""
        with patch.dict("os.environ", {}, clear=True):
            roles = get_skip_roles()
            assert roles == ["DK"]

    def test_custom_skip_roles(self):
        """Should parse comma-separated roles from env."""
        with patch.dict("os.environ", {"SKIP_VOICE_FEEDBACK_ROLES": "DK,SA,QA"}):
            roles = get_skip_roles()
            assert roles == ["DK", "SA", "QA"]

    def test_skip_roles_with_spaces(self):
        """Should trim whitespace from role names."""
        with patch.dict("os.environ", {"SKIP_VOICE_FEEDBACK_ROLES": " DK , SA "}):
            roles = get_skip_roles()
            assert roles == ["DK", "SA"]

    def test_empty_skip_roles(self):
        """Should return empty list for empty env var."""
        with patch.dict("os.environ", {"SKIP_VOICE_FEEDBACK_ROLES": ""}):
            roles = get_skip_roles()
            assert roles == []


class TestGetPaneRole:
    """Tests for get_pane_role() - uses @role_name tmux option."""

    def test_get_pane_role_success(self):
        """Should return role from @role_name option."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "@role_name SA"

        with patch("subprocess.run", return_value=mock_result):
            role = get_pane_role("team1", "pane-1")
            assert role == "SA"

    def test_get_pane_role_with_pane_prefix(self):
        """Should strip 'pane-' prefix from role_id."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "@role_name BE"

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            role = get_pane_role("team1", "pane-2")
            assert role == "BE"
            # Verify tmux was called with correct target
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "team1:0.2" in call_args

    def test_get_pane_role_not_set(self):
        """Should return empty string when @role_name not set."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""  # No option set

        with patch("subprocess.run", return_value=mock_result):
            role = get_pane_role("team1", "pane-5")
            assert role == ""

    def test_get_pane_role_tmux_error(self):
        """Should return empty string when tmux fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "session not found"

        with patch("subprocess.run", return_value=mock_result):
            role = get_pane_role("nonexistent", "pane-0")
            assert role == ""

    def test_get_pane_role_tmux_not_found(self):
        """Should return empty string when tmux not installed."""
        with patch("subprocess.run", side_effect=FileNotFoundError("tmux not found")):
            role = get_pane_role("team1", "pane-0")
            assert role == ""

    def test_get_pane_role_timeout(self):
        """Should return empty string on timeout."""
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("tmux", 5)):
            role = get_pane_role("team1", "pane-0")
            assert role == ""


class TestGetPaneTitle:
    """Tests for get_pane_title() - deprecated, delegates to get_pane_role."""

    def test_get_pane_title_delegates_to_get_pane_role(self):
        """Should delegate to get_pane_role for backward compatibility."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "@role_name PM"

        with patch("subprocess.run", return_value=mock_result):
            title = get_pane_title("team1", "pane-0")
            assert title == "PM"


class TestShouldSkipRole:
    """Tests for should_skip_role() - CRITICAL: fail-closed pattern."""

    def test_skip_dk_role(self):
        """Should skip DK role (in default skip list)."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "@role_name DK"

        with patch("subprocess.run", return_value=mock_result):
            with patch.dict("os.environ", {"SKIP_VOICE_FEEDBACK_ROLES": "DK"}):
                assert should_skip_role("team1", "pane-3") is True

    def test_process_pm_role(self):
        """Should process PM role (not in skip list)."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "@role_name PM"

        with patch("subprocess.run", return_value=mock_result):
            with patch.dict("os.environ", {"SKIP_VOICE_FEEDBACK_ROLES": "DK"}):
                assert should_skip_role("team1", "pane-0") is False

    def test_process_be_role(self):
        """Should process BE role (not in skip list)."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "@role_name BE"

        with patch("subprocess.run", return_value=mock_result):
            with patch.dict("os.environ", {"SKIP_VOICE_FEEDBACK_ROLES": "DK"}):
                assert should_skip_role("team1", "pane-2") is False

    # === Direct role_name parameter tests (hook provides role_name) ===

    def test_skip_with_role_name_param(self):
        """Should use role_name parameter directly without querying tmux."""
        # No subprocess mock needed - role_name is provided directly
        with patch.dict("os.environ", {"SKIP_VOICE_FEEDBACK_ROLES": "DK"}):
            assert should_skip_role("team1", "pane-5", role_name="DK") is True

    def test_process_with_role_name_param(self):
        """Should process when role_name not in skip list."""
        with patch.dict("os.environ", {"SKIP_VOICE_FEEDBACK_ROLES": "DK"}):
            assert should_skip_role("team1", "pane-0", role_name="PM") is False

    def test_role_name_param_overrides_tmux_query(self):
        """Should not query tmux when role_name is provided."""
        with patch("subprocess.run") as mock_run:
            with patch.dict("os.environ", {"SKIP_VOICE_FEEDBACK_ROLES": "DK"}):
                should_skip_role("team1", "pane-0", role_name="PM")
                # subprocess.run should NOT be called
                mock_run.assert_not_called()

    # === CRITICAL: Fail-Closed Tests ===

    def test_fail_closed_empty_role(self):
        """CRITICAL: Should SKIP when @role_name is empty (fail-closed).

        This is the core bug fix - when we can't determine the role,
        we SKIP (safer) rather than PROCESS (could cause spam).
        """
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""  # @role_name not set

        with patch("subprocess.run", return_value=mock_result):
            # Unknown role = SKIP (fail-closed)
            assert should_skip_role("team1", "pane-5") is True

    def test_fail_closed_tmux_error(self):
        """CRITICAL: Should SKIP when tmux command fails (fail-closed)."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "session not found"

        with patch("subprocess.run", return_value=mock_result):
            # tmux error = SKIP (fail-closed)
            assert should_skip_role("nonexistent", "pane-0") is True

    def test_fail_closed_tmux_not_found(self):
        """CRITICAL: Should SKIP when tmux not installed (fail-closed)."""
        with patch("subprocess.run", side_effect=FileNotFoundError("tmux")):
            # No tmux = SKIP (fail-closed)
            assert should_skip_role("team1", "pane-0") is True

    def test_fail_closed_timeout(self):
        """CRITICAL: Should SKIP on tmux timeout (fail-closed)."""
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("tmux", 5)):
            # Timeout = SKIP (fail-closed)
            assert should_skip_role("team1", "pane-0") is True

    def test_fail_closed_exception(self):
        """CRITICAL: Should SKIP on any unexpected exception (fail-closed)."""
        with patch("subprocess.run", side_effect=Exception("unexpected error")):
            # Exception = SKIP (fail-closed)
            assert should_skip_role("team1", "pane-0") is True

    # === Custom Skip Roles Tests ===

    def test_skip_multiple_roles_via_param(self):
        """Should skip all roles in SKIP_VOICE_FEEDBACK_ROLES (using role_name param)."""
        with patch.dict("os.environ", {"SKIP_VOICE_FEEDBACK_ROLES": "DK,SA"}):
            assert should_skip_role("team1", "pane-1", role_name="SA") is True
            assert should_skip_role("team1", "pane-5", role_name="DK") is True
            assert should_skip_role("team1", "pane-0", role_name="PM") is False

    def test_partial_match_in_role(self):
        """Should match role if skip_role is contained in role_name."""
        with patch.dict("os.environ", {"SKIP_VOICE_FEEDBACK_ROLES": "DK"}):
            # DK-docs contains DK
            assert should_skip_role("team1", "pane-2", role_name="DK-docs") is True


class TestAllowlistMode:
    """Tests for ALLOW_VOICE_FEEDBACK_ROLES - allowlist mode (Sprint 6).

    When ALLOW_VOICE_FEEDBACK_ROLES is set, ONLY those roles get voice feedback.
    All other roles are skipped. This takes precedence over blocklist.
    """

    def test_allow_po_role_only(self):
        """Should allow voice feedback for PO role when in allowlist."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": "PO"}, clear=False):
            assert should_skip_role("team1", "pane-0", role_name="PO") is False

    def test_block_sm_role_when_allowlist_set(self):
        """Should block SM role when only PO is in allowlist."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": "PO"}, clear=False):
            assert should_skip_role("team1", "pane-1", role_name="SM") is True

    def test_block_tl_role_when_allowlist_set(self):
        """Should block TL role when only PO is in allowlist."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": "PO"}, clear=False):
            assert should_skip_role("team1", "pane-2", role_name="TL") is True

    def test_block_fe_role_when_allowlist_set(self):
        """Should block FE role when only PO is in allowlist."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": "PO"}, clear=False):
            assert should_skip_role("team1", "pane-3", role_name="FE") is True

    def test_block_be_role_when_allowlist_set(self):
        """Should block BE role when only PO is in allowlist."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": "PO"}, clear=False):
            assert should_skip_role("team1", "pane-4", role_name="BE") is True

    def test_block_qa_role_when_allowlist_set(self):
        """Should block QA role when only PO is in allowlist."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": "PO"}, clear=False):
            assert should_skip_role("team1", "pane-5", role_name="QA") is True

    def test_fail_closed_unknown_role_with_allowlist(self):
        """CRITICAL: Should block unknown role even with allowlist (fail-closed)."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": "PO"}, clear=False):
            # Unknown/empty role should be skipped (fail-closed)
            assert should_skip_role("team1", "pane-0", role_name="") is True

    def test_allowlist_multiple_roles(self):
        """Should allow multiple roles in allowlist."""
        with patch.dict("os.environ", {"ALLOW_VOICE_FEEDBACK_ROLES": "PO,PM"}, clear=False):
            assert should_skip_role("team1", "pane-0", role_name="PO") is False
            assert should_skip_role("team1", "pane-0", role_name="PM") is False
            assert should_skip_role("team1", "pane-1", role_name="SM") is True

    def test_allowlist_takes_precedence_over_blocklist(self):
        """Allowlist should take precedence over blocklist when both set."""
        with patch.dict("os.environ", {
            "ALLOW_VOICE_FEEDBACK_ROLES": "PO",
            "SKIP_VOICE_FEEDBACK_ROLES": "DK"
        }, clear=False):
            # PO is in allowlist - should be allowed
            assert should_skip_role("team1", "pane-0", role_name="PO") is False
            # SM is NOT in allowlist - should be blocked (allowlist takes precedence)
            assert should_skip_role("team1", "pane-1", role_name="SM") is True

    def test_empty_allowlist_uses_blocklist_fallback(self):
        """Empty allowlist should fallback to blocklist behavior."""
        with patch.dict("os.environ", {
            "ALLOW_VOICE_FEEDBACK_ROLES": "",
            "SKIP_VOICE_FEEDBACK_ROLES": "DK"
        }, clear=False):
            # Empty allowlist = use blocklist mode
            assert should_skip_role("team1", "pane-0", role_name="PM") is False
            assert should_skip_role("team1", "pane-5", role_name="DK") is True
