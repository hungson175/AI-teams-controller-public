#!/bin/bash
# Auto-detect tmux role and output specific instructions for SessionStart

# Debug logging
LOG_FILE="/tmp/hook_debug.log"
echo "$(date): Hook triggered" >> "$LOG_FILE"
echo "  TMUX=$TMUX" >> "$LOG_FILE"
echo "  TMUX_PANE=$TMUX_PANE" >> "$LOG_FILE"
echo "  CLAUDE_PROJECT_DIR=$CLAUDE_PROJECT_DIR" >> "$LOG_FILE"

# Check if in tmux
if [ -z "$TMUX" ]; then
  echo "  -> Not in tmux, exiting" >> "$LOG_FILE"
  # Not in tmux, no action needed
  exit 0
fi

# Get role from pane option (set by setup-team.sh)
# CRITICAL: Use explicit pane ID ($TMUX_PANE) instead of -p flag
# The -p flag can fail in subprocess contexts where "current pane" is ambiguous
ROLE=$(tmux show-options -pt "$TMUX_PANE" -qv @role_name 2>/dev/null)
echo "  ROLE=$ROLE" >> "$LOG_FILE"

if [ -z "$ROLE" ]; then
  echo "  -> No role, exiting" >> "$LOG_FILE"
  # No role set, not a team pane
  exit 0
fi

# Get session name
SESSION=$(tmux display-message -p '#S' 2>/dev/null)
echo "  SESSION=$SESSION" >> "$LOG_FILE"

# Determine team directory based on session
if [ "$SESSION" = "command-center" ]; then
  TEAM_DIR="docs/tmux/command-center"
elif [ "$SESSION" = "ai_controller_full_team" ]; then
  TEAM_DIR="docs/tmux/ai_controller_full_team"
elif [ "$SESSION" = "AI-controller-app-PM" ]; then
  TEAM_DIR="docs/tmux/AI-controller-app-PM"
else
  echo "  -> Unknown session, exiting" >> "$LOG_FILE"
  # Unknown session
  exit 0
fi

echo "  TEAM_DIR=$TEAM_DIR" >> "$LOG_FILE"
echo "  -> Outputting JSON" >> "$LOG_FILE"

# Output role-specific instructions with strong language
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "CRITICAL CONTEXT RESTORATION - You are the ${ROLE} agent in tmux team '${SESSION}'.\n\n**MANDATORY FIRST ACTIONS** (do these IMMEDIATELY before anything else):\n\n1. READ your role prompt NOW: ${TEAM_DIR}/prompts/${ROLE}_PROMPT.md\n2. READ the WHITEBOARD for current status: ${TEAM_DIR}/WHITEBOARD.md\n3. CHECK your pane ID: You are in pane $(tmux display-message -p '#{pane_id}')\n\nDo NOT proceed with any other tasks until you have read these files and understand your current assignment."
  }
}
EOF
exit 0
