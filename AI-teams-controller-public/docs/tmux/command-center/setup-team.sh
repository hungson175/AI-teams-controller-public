#!/bin/bash

# AI Controller Scrum Team - Automated Setup Script
# This script sets up a tmux session with 6 Claude Code instances (PO, SM, TL, FE, BE, QA)
# NOTE: PO is pane 0 because PO receives requirements from Boss (stakeholder)

set -e  # Exit on error

PROJECT_ROOT="/Users/sonph36/dev/coding-agents/AI-teams-controller"
SESSION_NAME="command-center"
PROMPTS_DIR="$PROJECT_ROOT/docs/tmux/command-center/prompts"

echo "Starting AI Controller Scrum Team Setup..."

# 1. Check if session already exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "Session '$SESSION_NAME' already exists!"
    read -p "Kill existing session and create new one? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        tmux kill-session -t $SESSION_NAME
        echo "Killed existing session"
    else
        echo "Aborted. Use 'tmux attach -t $SESSION_NAME' to attach to existing session"
        exit 0
    fi
fi

# 2. Start new tmux session in detached mode
echo "Creating tmux session '$SESSION_NAME'..."
cd "$PROJECT_ROOT"
tmux new-session -d -s $SESSION_NAME

# 3. Create 6-pane horizontal layout
echo "Creating 6-pane layout..."
tmux split-window -h -t $SESSION_NAME
tmux split-window -h -t $SESSION_NAME
tmux split-window -h -t $SESSION_NAME
tmux split-window -h -t $SESSION_NAME
tmux split-window -h -t $SESSION_NAME
tmux select-layout -t $SESSION_NAME even-horizontal

# 3b. Resize window to prevent tiny pane widths when detached
echo "Resizing window for proper pane widths..."
tmux resize-window -t $SESSION_NAME -x 600 -y 50

# 4. Set pane titles (visual) and @role_name (stable)
# NOTE: PO is pane 0 because PO receives requirements from Boss
tmux select-pane -t $SESSION_NAME:0.0 -T "PO"
tmux select-pane -t $SESSION_NAME:0.1 -T "SM"
tmux select-pane -t $SESSION_NAME:0.2 -T "TL"
tmux select-pane -t $SESSION_NAME:0.3 -T "FE"
tmux select-pane -t $SESSION_NAME:0.4 -T "BE"
tmux select-pane -t $SESSION_NAME:0.5 -T "QA"

# Set stable @role_name options (won't be overwritten by Claude Code)
# NOTE: To query a pane's role from within that pane, agents MUST use:
#   tmux show-options -pt $TMUX_PANE -qv @role_name
# NOT: tmux show-options -pv @role_name (returns cursor pane, not agent's pane!)
tmux set-option -p -t $SESSION_NAME:0.0 @role_name "PO"
tmux set-option -p -t $SESSION_NAME:0.1 @role_name "SM"
tmux set-option -p -t $SESSION_NAME:0.2 @role_name "TL"
tmux set-option -p -t $SESSION_NAME:0.3 @role_name "FE"
tmux set-option -p -t $SESSION_NAME:0.4 @role_name "BE"
tmux set-option -p -t $SESSION_NAME:0.5 @role_name "QA"

# 5. Get pane IDs FIRST (before starting Claude Code)
echo "Getting pane IDs..."
PANE_IDS=$(tmux list-panes -t $SESSION_NAME -F "#{pane_id}")
PO_PANE=$(echo "$PANE_IDS" | sed -n '1p')
SM_PANE=$(echo "$PANE_IDS" | sed -n '2p')
TL_PANE=$(echo "$PANE_IDS" | sed -n '3p')
FE_PANE=$(echo "$PANE_IDS" | sed -n '4p')
BE_PANE=$(echo "$PANE_IDS" | sed -n '5p')
QA_PANE=$(echo "$PANE_IDS" | sed -n '6p')

echo "Pane IDs:"
echo "  PO  (Pane 0): $PO_PANE  <- Boss talks to PO"
echo "  SM  (Pane 1): $SM_PANE"
echo "  TL  (Pane 2): $TL_PANE"
echo "  FE  (Pane 3): $FE_PANE"
echo "  BE  (Pane 4): $BE_PANE"
echo "  QA  (Pane 5): $QA_PANE"

# 6. Start Claude Code in each pane with per-agent MCP config
# QA gets Playwright MCP, others get standard (no Playwright) to save tokens
echo "Starting Claude Code in all panes..."
MCP_CONFIG_DIR="$PROJECT_ROOT/docs/tmux/command-center/configs"
STANDARD_MCP="$MCP_CONFIG_DIR/standard-mcp.json"
QA_MCP="$MCP_CONFIG_DIR/qa-mcp.json"

# Model assignment:
#   SM, TL = Opus (high-level coordination and architecture)
#   PO, FE, BE = Sonnet (standard development work)
#   QA = Sonnet (testing tasks)

# PO - Sonnet, standard config
tmux send-keys -t $SESSION_NAME:0.0 "cd $PROJECT_ROOT && claude --model sonnet --strict-mcp-config --mcp-config $STANDARD_MCP" C-m

# SM - Opus, standard config (Scrum Master needs high reasoning for coordination)
tmux send-keys -t $SESSION_NAME:0.1 "cd $PROJECT_ROOT && claude --model opus --strict-mcp-config --mcp-config $STANDARD_MCP" C-m

# TL - Opus, standard config (Tech Lead needs high reasoning for architecture decisions)
tmux send-keys -t $SESSION_NAME:0.2 "cd $PROJECT_ROOT && claude --model opus --strict-mcp-config --mcp-config $STANDARD_MCP" C-m

# FE - Sonnet, standard config
tmux send-keys -t $SESSION_NAME:0.3 "cd $PROJECT_ROOT && claude --model sonnet --strict-mcp-config --mcp-config $STANDARD_MCP" C-m

# BE - Sonnet, standard config
tmux send-keys -t $SESSION_NAME:0.4 "cd $PROJECT_ROOT && claude --model sonnet --strict-mcp-config --mcp-config $STANDARD_MCP" C-m

# QA - Sonnet, with Playwright MCP for browser-based blackbox testing
tmux send-keys -t $SESSION_NAME:0.5 "cd $PROJECT_ROOT && claude --model sonnet --strict-mcp-config --mcp-config $QA_MCP" C-m

# 9. Wait for Claude Code instances to start
echo "Waiting 20 seconds for Claude Code instances to initialize..."
sleep 20

# 10. Initialize roles using /init-role slash command
echo "Initializing agent roles..."
tmux send-keys -t $SESSION_NAME:0.0 "/init-role PO" C-m
tmux send-keys -t $SESSION_NAME:0.0 C-m
sleep 2

tmux send-keys -t $SESSION_NAME:0.1 "/init-role SM" C-m
tmux send-keys -t $SESSION_NAME:0.1 C-m
sleep 2

tmux send-keys -t $SESSION_NAME:0.2 "/init-role TL" C-m
tmux send-keys -t $SESSION_NAME:0.2 C-m
sleep 2

tmux send-keys -t $SESSION_NAME:0.3 "/init-role FE" C-m
tmux send-keys -t $SESSION_NAME:0.3 C-m
sleep 2

tmux send-keys -t $SESSION_NAME:0.4 "/init-role BE" C-m
tmux send-keys -t $SESSION_NAME:0.4 C-m
sleep 2

tmux send-keys -t $SESSION_NAME:0.5 "/init-role QA" C-m
tmux send-keys -t $SESSION_NAME:0.5 C-m

# 11. Wait for roles to initialize
echo "Waiting 15 seconds for role initialization..."
sleep 15

# 12. Verify WHITEBOARD exists
if [ ! -f "$PROJECT_ROOT/docs/tmux/command-center/WHITEBOARD.md" ]; then
    echo "WHITEBOARD.md not found! Please create it manually."
else
    echo "WHITEBOARD.md exists"
fi

# 13. Summary
echo ""
echo "Setup Complete!"
echo ""
echo "Session: $SESSION_NAME"
echo "Project: $PROJECT_ROOT"
echo ""
echo "Pane Layout:"
echo "  +--------+--------+--------+--------+--------+--------+"
echo "  | Pane 0 | Pane 1 | Pane 2 | Pane 3 | Pane 4 | Pane 5 |"
echo "  | PO     | SM     | TL     | FE     | BE     | QA     |"
echo "  | $PO_PANE | $SM_PANE | $TL_PANE | $FE_PANE | $BE_PANE | $QA_PANE |"
echo "  +--------+--------+--------+--------+--------+--------+"
echo ""
echo "Scrum Team Roles:"
echo "  PO  = Product Owner (receives requirements from Boss - PANE 0)"
echo "  SM  = Scrum Master (facilitates process)"
echo "  TL  = Tech Lead (design + code review)"
echo "  FE  = Frontend Engineer (TDD implementation)"
echo "  BE  = Backend Engineer (TDD implementation)"
echo "  QA  = Tester (blackbox testing)"
echo ""
echo "Boss Communication:"
echo "  >>> prefix sends to PO (Pane 0), not SM!"
echo "  PO receives requirements from Boss and defines sprint backlog"
echo ""
echo "Next steps:"
echo "  1. Attach to session: tmux attach -t $SESSION_NAME"
echo "  2. Switch to PO pane (Pane 0): Ctrl+B, then arrow key"
echo "  3. Provide requirements to PO using >>> prefix"
echo "  4. Watch the team work autonomously!"
echo ""
echo "To detach from session: Ctrl+B, then D"
echo "To kill session: tmux kill-session -t $SESSION_NAME"
echo ""

# 14. Move cursor to PO pane (Boss talks to PO)
tmux select-pane -t $SESSION_NAME:0.0
echo "CURSOR NOW IN PANE 0 (PO). This is where Boss sends requirements."
