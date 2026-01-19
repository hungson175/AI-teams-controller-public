# -*- coding: utf-8 -*-
"""Skip logic for voice feedback filtering.

This module handles the decision of which panes should NOT receive voice feedback.
It runs in the FastAPI layer (where tmux is accessible), NOT in Celery workers.

Key Design Decision: FAIL-CLOSED
When we cannot determine if a pane should be skipped (tmux fails, empty title, etc.),
we default to SKIPPING (safer) rather than PROCESSING (could cause spam).

Story 2: Skip Logic Refactor (Voice Feedback Epic)
"""

import logging
import os
import subprocess
from typing import List

logger = logging.getLogger(__name__)


def get_skip_roles() -> List[str]:
    """Get list of roles to skip voice feedback for (blocklist mode).

    Reads from SKIP_VOICE_FEEDBACK_ROLES environment variable.
    Default: 'DK' (Document Keeper - silent worker role)

    Environment variable format: comma-separated role names
    Example: SKIP_VOICE_FEEDBACK_ROLES=DK,SA,QA

    NOTE: If ALLOW_VOICE_FEEDBACK_ROLES is set, allowlist takes precedence.

    Returns:
        List of role name strings to skip
    """
    env_value = os.environ.get("SKIP_VOICE_FEEDBACK_ROLES", "DK")
    roles = [r.strip() for r in env_value.split(",") if r.strip()]
    return roles


def get_allow_roles() -> List[str]:
    """Get list of roles allowed for voice feedback (allowlist mode).

    Reads from ALLOW_VOICE_FEEDBACK_ROLES environment variable.
    When set, ONLY these roles receive voice feedback - all others are skipped.
    This takes precedence over the blocklist (SKIP_VOICE_FEEDBACK_ROLES).

    Environment variable format: comma-separated role names
    Example: ALLOW_VOICE_FEEDBACK_ROLES=PO (only PO gets voice feedback)

    Returns:
        List of role name strings to allow (empty list if not set)
    """
    env_value = os.environ.get("ALLOW_VOICE_FEEDBACK_ROLES", "")
    roles = [r.strip() for r in env_value.split(",") if r.strip()]
    return roles


def get_pane_role(team_id: str, role_id: str) -> str:
    """Get tmux pane role using @role_name option (stable, set by setup script).

    NOTE: We use @role_name option instead of pane_title because Claude Code
    overwrites pane titles with task descriptions. The @role_name option is
    set by setup-team.sh and remains stable.

    Args:
        team_id: tmux session name
        role_id: pane identifier (e.g., "pane-0", "pane-4")

    Returns:
        Role name (PM, SA, BE, FE, CR, DK) or empty string if not found/error
    """
    # Extract pane index from role_id (e.g., "pane-4" -> "4")
    pane_index = role_id.replace("pane-", "") if role_id.startswith("pane-") else role_id

    try:
        # Get @role_name option for the specific pane
        # Format: team_id:window.pane (e.g., ai_controller_full_team:0.1)
        pane_target = f"{team_id}:0.{pane_index}"
        result = subprocess.run(
            ["tmux", "show-options", "-p", "-t", pane_target, "@role_name"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            logger.warning(f"[SKIP] tmux show-options failed: {result.stderr[:100]}")
            return ""

        # Parse output: "@role_name PM" -> "PM"
        output = result.stdout.strip()
        if output.startswith("@role_name "):
            return output.split(" ", 1)[1]

        logger.warning(f"[SKIP] @role_name not set for {pane_target}")
        return ""

    except FileNotFoundError:
        logger.warning("[SKIP] tmux not found in PATH")
        return ""
    except subprocess.TimeoutExpired:
        logger.warning(f"[SKIP] tmux command timed out for {team_id}/{role_id}")
        return ""
    except Exception as e:
        logger.warning(f"[SKIP] Failed to get pane role: {e}")
        return ""


# Keep old function name for backward compatibility
def get_pane_title(team_id: str, role_id: str) -> str:
    """Deprecated: Use get_pane_role instead. Kept for backward compatibility."""
    return get_pane_role(team_id, role_id)


def should_skip_role(team_id: str, role_id: str, role_name: str | None = None) -> bool:
    """Check if voice feedback should be skipped for this role.

    CRITICAL: Uses FAIL-CLOSED pattern.
    When tmux is unavailable or role cannot be determined,
    we SKIP (return True) rather than PROCESS (safer default).

    This prevents spam/duplicate audio when the system is in an unknown state.

    Mode Selection:
    - If ALLOW_VOICE_FEEDBACK_ROLES is set (non-empty): ALLOWLIST mode
      Only roles in the allowlist get voice feedback.
    - If ALLOW_VOICE_FEEDBACK_ROLES is empty/not set: BLOCKLIST mode
      Roles in SKIP_VOICE_FEEDBACK_ROLES are skipped.

    Args:
        team_id: tmux session name
        role_id: pane identifier (e.g., "pane-0")
        role_name: role name from @role_name option (PM, SA, BE, etc.)
                   If provided, uses this directly instead of querying tmux.

    Returns:
        True if role should be SKIPPED (no voice feedback)
        False if role should be PROCESSED (generate voice feedback)
    """
    # Use provided role_name if available, otherwise query tmux
    if role_name:
        detected_role = role_name
        logger.debug(f"[SKIP] Using role_name from hook: {role_name}")
    else:
        detected_role = get_pane_role(team_id, role_id)

    # FAIL-CLOSED: Unknown role = skip (safer than processing)
    if not detected_role:
        logger.warning(
            f"[SKIP] Cannot determine role for {team_id}/{role_id}, "
            "skipping for safety (fail-closed)"
        )
        return True

    # Check if allowlist mode is enabled
    allow_roles = get_allow_roles()
    if allow_roles:
        # ALLOWLIST mode: only allow roles explicitly listed
        if detected_role in allow_roles:
            logger.info(
                f"[SKIP] ALLOWLIST: Allowing voice feedback for {detected_role}: "
                f"{team_id}/{role_id}"
            )
            return False
        else:
            logger.info(
                f"[SKIP] ALLOWLIST: Skipping voice feedback for {detected_role}: "
                f"{team_id}/{role_id} (not in allowlist: {allow_roles})"
            )
            return True

    # BLOCKLIST mode (fallback): check if role matches any skip role
    skip_roles = get_skip_roles()
    for skip_role in skip_roles:
        if skip_role == detected_role or skip_role in detected_role:
            logger.info(
                f"[SKIP] BLOCKLIST: Skipping voice feedback for {skip_role} role: "
                f"{team_id}/{role_id} (role: {detected_role})"
            )
            return True

    # Known role, not in skip list = process
    logger.debug(f"[SKIP] BLOCKLIST: Processing voice feedback: {team_id}/{role_id} (role: {detected_role})")
    return False
