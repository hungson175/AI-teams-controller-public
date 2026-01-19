#!/usr/bin/env python3
"""
SessionStart hook: Initialize agent role after session start (including auto-compact).
Outputs JSON with additionalContext containing absolute file paths.
"""
import json
import sys
import subprocess
import os

LOG_FILE = "/tmp/session_start_hook.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        from datetime import datetime
        f.write(f"{datetime.now()}: {msg}\n")

def run_cmd(cmd):
    """Run shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except Exception as e:
        log(f"Command failed: {cmd} - {e}")
        return ""

def main():
    log("SessionStart hook triggered")

    # Check if in tmux
    tmux_env = os.environ.get("TMUX", "")
    if not tmux_env:
        log("Not in tmux, exiting")
        sys.exit(0)

    # Get tmux pane ID
    tmux_pane = os.environ.get("TMUX_PANE", "")
    log(f"TMUX_PANE={tmux_pane}")

    # Get role from pane option
    role = run_cmd(f"tmux show-options -p -t {tmux_pane} @role_name 2>/dev/null | awk '{{print $2}}'")
    log(f"Role={role}")

    if not role:
        log("No role found, exiting")
        sys.exit(0)

    # Get session name
    session = run_cmd("tmux display-message -p '#S' 2>/dev/null")
    log(f"Session={session}")

    # Get project directory from CLAUDE_PROJECT_DIR or cwd
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    # Determine team directory based on session
    if session == "ai_controller_full_team":
        team_dir = "docs/tmux/ai_controller_full_team"
    elif session == "AI-controller-app-PM":
        team_dir = "docs/tmux/AI-controller-app-PM"
    else:
        log(f"Unknown session: {session}, exiting")
        sys.exit(0)

    overview_path = f"{project_dir}/{team_dir}/tmux-team-overview.md"
    prompt_path = f"{project_dir}/{team_dir}/prompts/{role}_PROMPT.md"

    log(f"Team Overview: {overview_path}")
    log(f"Prompt: {prompt_path}")

    # Build context - DIRECT AND SIMPLE
    context = f"""# MANDATORY: Initialize Agent Role

Session: **{session}** | Role: **{role}**

## READ THESE FILES NOW (use Read tool):

1. {overview_path}
2. {prompt_path}

Then announce: "[{role}] initialized. Team: {session}. Ready."
"""

    # Output JSON with additionalContext
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context
        }
    }

    print(json.dumps(output))
    log("Hook output sent successfully")
    sys.exit(0)

if __name__ == "__main__":
    main()
