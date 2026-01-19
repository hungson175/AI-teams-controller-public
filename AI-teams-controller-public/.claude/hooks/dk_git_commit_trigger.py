#!/usr/bin/env python3
"""
DK Git Commit Trigger Hook (PostToolUse)

Triggers Document Keeper to sync docs when a git commit is detected.
Only triggers for successful commits (not failed ones).

Usage: PostToolUse hook on Bash tool
"""
import json
import sys
import os
import re

# State file to prevent duplicate triggers for same commit
STATE_FILE = os.path.expanduser("~/.claude/dk_last_commit.txt")

def get_last_triggered_commit():
    """Get the last commit hash that triggered DK."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return f.read().strip()
    return None

def save_triggered_commit(commit_hash):
    """Save commit hash to prevent re-triggering."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        f.write(commit_hash)

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Only process Bash tool
    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    # Get the command that was executed
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Check if it was a git commit command
    if not re.search(r'git\s+commit', command):
        sys.exit(0)

    # Get the tool response to check if commit succeeded
    tool_response = input_data.get("tool_response", {})
    stdout = tool_response.get("stdout", "")
    stderr = tool_response.get("stderr", "")
    exit_code = tool_response.get("exitCode", 0)

    # Only trigger if commit was successful
    if exit_code != 0:
        sys.exit(0)

    # Extract commit hash from output (usually in format "[branch hash] message")
    commit_match = re.search(r'\[[\w/-]+\s+([a-f0-9]{7,})\]', stdout)
    if not commit_match:
        # Try alternative format
        commit_match = re.search(r'([a-f0-9]{7,})', stdout)

    if not commit_match:
        sys.exit(0)

    commit_hash = commit_match.group(1)

    # Check if we already triggered for this commit
    last_commit = get_last_triggered_commit()
    if last_commit == commit_hash:
        sys.exit(0)

    # Save this commit to prevent re-triggering
    save_triggered_commit(commit_hash)

    # Output blocking message to trigger DK
    output = {
        "decision": "block",
        "reason": f"Git commit detected ({commit_hash}). DK should sync docs to match new code changes. Run: check git diff for changed files, update docs/generated-docs/ if code structure changed.",
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": f"New commit: {commit_hash}\nCommand: {command}\nDK trigger: Sync docs/generated-docs/ with latest code changes."
        }
    }
    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
