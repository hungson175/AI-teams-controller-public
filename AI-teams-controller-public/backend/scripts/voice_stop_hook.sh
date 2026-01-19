#!/bin/bash
# -*- coding: utf-8 -*-
# Voice Stop Hook for Claude Code
#
# This hook is called when Claude Code finishes responding (Stop event).
# It notifies the backend to generate voice feedback for the user.
#
# AUTO-DETECTION: This hook automatically detects the tmux session and pane
# from the TMUX environment variable. No manual configuration needed!
#
# Installation:
#   1. Copy to ~/.claude/hooks/:
#      cp voice_stop_hook.sh ~/.claude/hooks/
#      chmod +x ~/.claude/hooks/voice_stop_hook.sh
#
#   2. Add to ~/.claude/settings.json (merge with existing Stop hooks):
#      {
#        "hooks": {
#          "Stop": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "~/.claude/hooks/voice_stop_hook.sh",
#                "timeout": 10
#              }]
#            }
#          ]
#        }
#      }
#
# Environment variables (optional overrides):
#   - VOICE_API_URL: Backend API URL (default: http://localhost:17061)
#   - VOICE_TEAM_ID: Override auto-detected team_id
#   - VOICE_ROLE_ID: Override auto-detected role_id (pane-N format)

# Don't exit on error - we want to fail silently
set +e

# Configuration
API_URL="${VOICE_API_URL:-http://localhost:17061}"

# Auto-detect tmux session and pane from environment variables
# TMUX_PANE is set by tmux to the actual pane ID (e.g., %17)
# Using display-message without -t returns the FOCUSED pane (WRONG!)
if [ -n "$TMUX" ] && [ -n "$TMUX_PANE" ]; then
    # Use $TMUX_PANE directly - it's the actual pane where this script runs
    PANE_ID="$TMUX_PANE"
    # Query tmux for this specific pane's info using -t flag
    SESSION_NAME=$(tmux display-message -t "$TMUX_PANE" -p '#{session_name}' 2>/dev/null)
    PANE_INDEX=$(tmux display-message -t "$TMUX_PANE" -p '#{pane_index}' 2>/dev/null)
fi

# Use environment overrides if set, otherwise use auto-detected values
TEAM_ID="${VOICE_TEAM_ID:-$SESSION_NAME}"
ROLE_ID="${VOICE_ROLE_ID:-pane-$PANE_INDEX}"

# Skip if not in tmux or couldn't detect
if [ -z "$TEAM_ID" ] || [ -z "$ROLE_ID" ] || [ "$ROLE_ID" = "pane-" ]; then
    exit 0
fi

# Get session info from Claude Code environment
SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"
TRANSCRIPT_PATH="${CLAUDE_TRANSCRIPT_PATH:-}"

# Call the backend task-done endpoint (fire and forget)
curl -s -X POST "${API_URL}/api/voice/task-done/${TEAM_ID}/${ROLE_ID}" \
    -H "Content-Type: application/json" \
    -d "{
        \"session_id\": \"${SESSION_ID}\",
        \"transcript_path\": \"${TRANSCRIPT_PATH}\",
        \"team_id\": \"${TEAM_ID}\",
        \"role_id\": \"${ROLE_ID}\"
    }" > /dev/null 2>&1 &

# Hook should not block, so we exit immediately
exit 0
