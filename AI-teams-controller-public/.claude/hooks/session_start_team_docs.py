#!/usr/bin/env python3
"""
SessionStart hook to inject role docs and workflow into agent context.

Automatically loads and injects into context:
- Role-specific prompt (docs/tmux/command-center/prompts/{ROLE}_PROMPT.md)
- Team workflow (docs/tmux/command-center/workflow.md)

Activates for command-center team at:
- startup
- resume
- clear
- compact (both auto and manual)

Uses $TMUX_PANE to avoid pane detection bugs.
Uses relative paths from cwd to work on any machine.
"""
import json
import os
import subprocess
import sys


def get_role():
    """
    Get agent role from tmux pane option using $TMUX_PANE.

    Returns: role name or empty string if not set
    """
    tmux_pane = os.environ.get("TMUX_PANE")
    if not tmux_pane:
        return ""

    try:
        result = subprocess.run(
            ["tmux", "show-options", "-pt", tmux_pane, "-qv", "@role_name"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error getting role: {e}", file=sys.stderr)
        return ""


def get_session_name():
    """
    Get tmux session name for current pane.

    Returns: session name or empty string if not in tmux
    """
    tmux_pane = os.environ.get("TMUX_PANE")
    if not tmux_pane:
        return ""

    try:
        result = subprocess.run(
            ["tmux", "display-message", "-pt", tmux_pane, "-p", "#{session_name}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error getting session name: {e}", file=sys.stderr)
        return ""


def should_activate(role, session):
    """
    Determine if hook should activate based on role and session.

    Args:
        role: Agent role (e.g., "QA", "SM", "FE")
        session: Tmux session name

    Returns: (should_activate, reason)
    """
    # No role set - setup not complete or not a multi-agent team
    if not role:
        return False, "No role assigned - skipping"

    # Not in command-center team
    if session != "command-center":
        return False, f"Not in command-center (session: {session})"

    # All checks passed - activate!
    return True, f"Role {role} in command-center team"


def load_docs(role, cwd):
    """
    Load role prompt and workflow docs from project directory.

    Args:
        role: Agent role name
        cwd: Current working directory from hook input

    Returns: Combined documentation content or None if files not found
    """
    try:
        role_prompt_path = os.path.join(cwd, f"docs/tmux/command-center/prompts/{role}_PROMPT.md")
        workflow_path = os.path.join(cwd, "docs/tmux/command-center/workflow.md")

        # Read role prompt
        with open(role_prompt_path, 'r') as f:
            role_prompt = f.read()

        # Read workflow
        with open(workflow_path, 'r') as f:
            workflow = f.read()

        # Combine with clear section headers
        combined = f"""# Role Prompt for {role}

{role_prompt}

---

# Team Workflow

{workflow}
"""
        return combined

    except FileNotFoundError as e:
        print(f"Warning: Could not find docs: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error reading docs: {e}", file=sys.stderr)
        return None


def main():
    try:
        # Load input from stdin
        input_data = json.load(sys.stdin)

        # Get role and session
        role = get_role()
        session = get_session_name()

        # Determine if we should activate
        should_act, debug_reason = should_activate(role, session)

        if not should_act:
            # Don't activate - exit cleanly
            print(f"[DEBUG] {debug_reason}", file=sys.stderr)
            sys.exit(0)

        # Get cwd from input
        cwd = input_data.get("cwd", os.getcwd())
        source = input_data.get("source", "unknown")

        print(f"[DEBUG] Activating for {debug_reason} (source: {source})", file=sys.stderr)

        # Load and inject documentation as context
        docs_content = load_docs(role, cwd)

        if docs_content:
            # Output to stdout - SessionStart automatically adds this as context
            print(docs_content)
            print(f"[DEBUG] Loaded docs for {role} from {cwd}", file=sys.stderr)
        else:
            print(f"[DEBUG] Could not load docs for {role}", file=sys.stderr)

        sys.exit(0)

    except Exception as e:
        # On any error, don't block agent from starting
        print(f"Error in session_start_team_docs hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
