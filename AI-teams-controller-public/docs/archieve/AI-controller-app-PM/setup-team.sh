#!/bin/bash

# AI-Controller-App Team - Automated Setup Script
# This script sets up a tmux session with 3 panes:
#   - Pane 0: PM (Claude Code) - Project Manager
#   - Pane 1: CR (Codex CLI) - Code Reviewer
#   - Pane 2: TESTER (Claude Code) - Tester
# The Boss (human) operates from a SEPARATE terminal outside tmux

set -e  # Exit on error

PROJECT_ROOT="/Users/sonph36/dev/tools/AI-teams-controller"
SESSION_NAME="AI-controller-app-PM"
PROMPTS_DIR="$PROJECT_ROOT/docs/tmux/AI-controller-app-PM/prompts"

echo "Starting AI-Controller-App Team Setup (PM + CR + TESTER)..."

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

# 3. Create 3-pane layout (PM left, CR top-right, TESTER bottom-right)
echo "Creating 3-pane layout..."
tmux split-window -h -t $SESSION_NAME        # Split horizontally: PM | right
tmux split-window -v -t $SESSION_NAME:0.1    # Split right pane vertically: CR on top, TESTER on bottom

# 4. Set pane titles (display) and @role_name (stable identifier for API)
tmux select-pane -t $SESSION_NAME:0.0 -T "PM"
tmux select-pane -t $SESSION_NAME:0.1 -T "CR"
tmux select-pane -t $SESSION_NAME:0.2 -T "TESTER"

# Set @role_name options (stable - won't be overwritten by Claude Code)
tmux set-option -p -t $SESSION_NAME:0.0 @role_name "PM"
tmux set-option -p -t $SESSION_NAME:0.1 @role_name "CR"
tmux set-option -p -t $SESSION_NAME:0.2 @role_name "TESTER"

# 5. Start Claude Code in PM pane (pane 0)
echo "Starting Claude Code in PM pane..."
tmux send-keys -t $SESSION_NAME:0.0 "cd $PROJECT_ROOT && claude" C-m

# 6. Start Codex CLI in CR pane (pane 1)
echo "Starting Codex CLI in CR pane..."
tmux send-keys -t $SESSION_NAME:0.1 "cd $PROJECT_ROOT && codex --yolo" C-m

# 7. Start Claude Code in TESTER pane (pane 2)
echo "Starting Claude Code in TESTER pane..."
tmux send-keys -t $SESSION_NAME:0.2 "cd $PROJECT_ROOT && claude" C-m

# 8. Wait for all to start
echo "Waiting 15 seconds for initialization..."
sleep 15

# 9. Initialize PM role using /init-role slash command
echo "Initializing PM role..."
tmux send-keys -t $SESSION_NAME:0.0 "/init-role PM" C-m
sleep 1
tmux send-keys -t $SESSION_NAME:0.0 C-m

# 10. Initialize CR with its prompt (codex reads directly)
echo "Initializing CR role..."
tmux send-keys -t $SESSION_NAME:0.1 "You are the Code Reviewer (CR) for the AI-controller-app project. Read your prompt at docs/tmux/AI-controller-app-PM/prompts/CR_PROMPT.md and confirm you understand your role. You only respond to BOSS messages with <<< prefix. You do NOT communicate with PM or TESTER." C-m
sleep 1
tmux send-keys -t $SESSION_NAME:0.1 C-m

# 11. Initialize TESTER role
echo "Initializing TESTER role..."
tmux send-keys -t $SESSION_NAME:0.2 "You are the TESTER for the AI-controller-app project. Read your prompt at docs/tmux/AI-controller-app-PM/prompts/TESTER_PROMPT.md and confirm you understand your role. You only respond to BOSS messages with ### prefix. You do NOT communicate with PM or CR." C-m
sleep 1
tmux send-keys -t $SESSION_NAME:0.2 C-m

# 12. Wait for roles to initialize
echo "Waiting 10 seconds for role initialization..."
sleep 10

# 13. Get pane IDs
echo "Getting pane IDs..."
PANE_IDS=$(tmux list-panes -t $SESSION_NAME -F "#{pane_id}")
PM_PANE=$(echo "$PANE_IDS" | sed -n '1p')
CR_PANE=$(echo "$PANE_IDS" | sed -n '2p')
TESTER_PANE=$(echo "$PANE_IDS" | sed -n '3p')

echo "Pane IDs:"
echo "  PM (Pane 0): $PM_PANE"
echo "  CR (Pane 1): $CR_PANE"
echo "  TESTER (Pane 2): $TESTER_PANE"

# 14. Summary
echo ""
echo "Setup Complete!"
echo ""
echo "Session: $SESSION_NAME"
echo "Project: $PROJECT_ROOT"
echo ""
echo "Pane Layout:"
echo "  +------------------+------------------+"
echo "  |                  | Pane 1           |"
echo "  | Pane 0           | CR (Codex)       |"
echo "  | PM (Claude)      | $CR_PANE              |"
echo "  | $PM_PANE              +------------------+"
echo "  |                  | Pane 2           |"
echo "  |                  | TESTER (Claude)  |"
echo "  |                  | $TESTER_PANE              |"
echo "  +------------------+------------------+"
echo ""
echo "Communication Prefixes:"
echo "  >>> message  -> Send to PM (project management)"
echo "  <<< message  -> Send to CR (code review)"
echo "  ### message  -> Send to TESTER (testing)"
echo ""
echo "Boss Terminal Commands:"
echo "  # Send to PM"
echo "  tmux send-keys -t $SESSION_NAME:0.0 'BOSS [\$(date +%H:%M)]: your message' C-m && sleep 0.5 && tmux send-keys -t $SESSION_NAME:0.0 C-m"
echo ""
echo "  # Send to CR"
echo "  tmux send-keys -t $SESSION_NAME:0.1 'BOSS [\$(date +%H:%M)]: your message' C-m && sleep 0.5 && tmux send-keys -t $SESSION_NAME:0.1 C-m"
echo ""
echo "  # Send to TESTER"
echo "  tmux send-keys -t $SESSION_NAME:0.2 'BOSS [\$(date +%H:%M)]: your message' C-m && sleep 0.5 && tmux send-keys -t $SESSION_NAME:0.2 C-m"
echo ""
echo "  # View PM output"
echo "  tmux capture-pane -t $SESSION_NAME:0.0 -p | tail -50"
echo ""
echo "  # View CR output"
echo "  tmux capture-pane -t $SESSION_NAME:0.1 -p | tail -50"
echo ""
echo "  # View TESTER output"
echo "  tmux capture-pane -t $SESSION_NAME:0.2 -p | tail -50"
echo ""
echo "  # Attach to see all (Ctrl+B, D to detach)"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "To kill session: tmux kill-session -t $SESSION_NAME"
echo ""
