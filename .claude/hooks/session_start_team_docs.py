#!/usr/bin/env python3
"""
SessionStart hook for packaging-agent tmux team.

Detects the current tmux session and role, then injects:
1. workflow.md (team workflow documentation)
2. Role-specific prompt file (e.g., PO_PROMPT.md for PO role)

This ensures agents always have context after auto-compact or session restart.
"""
import json
import os
import subprocess
import sys


# Use CLAUDE_PROJECT_DIR env var for project root
PROJECT_ROOT = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

# Team configurations for packaging-agent
TEAM_CONFIGS = {
    "packaging-agent": {
        "docs_dir": os.path.join(PROJECT_ROOT, "docs/tmux/packaging-agent"),
        "roles": {"PO", "DEV", "DU"},
    },
}


def get_tmux_role():
    """Get the role from tmux @role_name option.

    CRITICAL: Use $TMUX_PANE to target the specific pane where this process runs,
    NOT the cursor pane (where user's focus is). Using -pv without target queries
    the active/cursor pane, which can be anywhere, causing wrong role detection.
    """
    # Get the pane ID where THIS process is running
    tmux_pane = os.environ.get("TMUX_PANE")
    if not tmux_pane:
        return None

    try:
        result = subprocess.run(
            ["tmux", "show-options", "-pt", tmux_pane, "-qv", "@role_name"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def get_tmux_session():
    """Get the current tmux session name."""
    try:
        result = subprocess.run(
            ["tmux", "display-message", "-p", "#S"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def read_file_content(file_path):
    """Read file content, return None if file doesn't exist."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, IOError):
        return None


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Not critical for SessionStart - just exit silently
        sys.exit(0)

    # Check if TEAM_CONFIGS is empty (not configured)
    if not TEAM_CONFIGS:
        # Hook not configured yet, exit silently
        sys.exit(0)

    # Get current session and check if it's a known team
    session = get_tmux_session()
    if session not in TEAM_CONFIGS:
        # Not a known team session, exit silently
        sys.exit(0)

    team_config = TEAM_CONFIGS[session]
    docs_dir = team_config["docs_dir"]
    valid_roles = team_config["roles"]

    # Get the role
    role = get_tmux_role()
    if not role or role not in valid_roles:
        # No valid role detected, exit silently
        sys.exit(0)

    # Build context to inject
    context_parts = []

    # 1. Read team overview
    overview_paths = [
        os.path.join(docs_dir, "workflow.md"),
    ]
    overview_content = None
    for overview_path in overview_paths:
        overview_content = read_file_content(overview_path)
        if overview_content:
            break

    if overview_content:
        context_parts.append(f"=== TEAM WORKFLOW DOCUMENTATION ===\n\n{overview_content}")

    # 2. Read role-specific prompt
    # Handle both naming conventions: ROLE_PROMPT.md or ROLE.md
    prompt_paths = [
        os.path.join(docs_dir, "prompts", f"{role}_PROMPT.md"),
        os.path.join(docs_dir, "prompts", f"{role}.md"),
    ]

    prompt_content = None
    for prompt_path in prompt_paths:
        prompt_content = read_file_content(prompt_path)
        if prompt_content:
            break

    if prompt_content:
        context_parts.append(f"=== YOUR ROLE: {role} ===\n\n{prompt_content}")

    # If we have context to inject, return it
    if context_parts:
        combined_context = "\n\n" + "\n\n".join(context_parts)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": combined_context
            }
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
