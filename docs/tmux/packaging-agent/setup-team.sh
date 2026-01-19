#!/bin/bash

# Packaging Agent Team - Automated Setup Script
# Creates a tmux session with 3 Claude Code instances (PO, DEV, DU)

set -e  # Exit on error

PROJECT_ROOT="${PROJECT_ROOT:-/home/hungson175/dev/coding-agents/packaging-agent}"
SESSION_NAME="${SESSION_NAME:-packaging-agent}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"

# Auto-scale window width based on number of panes
NUM_PANES=3
MIN_WIDTH_PER_PANE=80
WINDOW_WIDTH=$((NUM_PANES * MIN_WIDTH_PER_PANE))
WINDOW_HEIGHT=50

echo "Starting Packaging Agent Team Setup..."
echo "Project Root: $PROJECT_ROOT"
echo "Session Name: $SESSION_NAME"

# 1. Check if session already exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "Session '$SESSION_NAME' already exists!"
    read -p "Kill existing session and create new one? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        tmux kill-session -t $SESSION_NAME
        echo "Killed existing session"
    else
        echo "Aborted. Use 'tmux attach -t $SESSION_NAME' to attach"
        exit 0
    fi
fi

# 2. Start new tmux session
echo "Creating tmux session '$SESSION_NAME'..."
cd "$PROJECT_ROOT"
tmux new-session -d -s $SESSION_NAME

# 3. Create 3-pane layout
echo "Creating 3-pane layout..."
tmux split-window -h -t $SESSION_NAME
tmux split-window -h -t $SESSION_NAME
tmux select-layout -t $SESSION_NAME even-horizontal

# 4. Resize for proper pane widths (auto-scaled)
echo "Resizing window to ${WINDOW_WIDTH}x${WINDOW_HEIGHT} (${NUM_PANES} panes x ${MIN_WIDTH_PER_PANE} chars)..."
tmux resize-window -t $SESSION_NAME -x $WINDOW_WIDTH -y $WINDOW_HEIGHT

# 5. Set pane titles and role names
tmux select-pane -t $SESSION_NAME:0.0 -T "PO"
tmux select-pane -t $SESSION_NAME:0.1 -T "DEV"
tmux select-pane -t $SESSION_NAME:0.2 -T "DU"

tmux set-option -p -t $SESSION_NAME:0.0 @role_name "PO"
tmux set-option -p -t $SESSION_NAME:0.1 @role_name "DEV"
tmux set-option -p -t $SESSION_NAME:0.2 @role_name "DU"

# 6. Get pane IDs
echo "Getting pane IDs..."
PANE_IDS=$(tmux list-panes -t $SESSION_NAME -F "#{pane_id}")
PO_PANE=$(echo "$PANE_IDS" | sed -n '1p')
DEV_PANE=$(echo "$PANE_IDS" | sed -n '2p')
DU_PANE=$(echo "$PANE_IDS" | sed -n '3p')

echo "Pane IDs:"
echo "  PO (Pane 0): $PO_PANE"
echo "  DEV (Pane 1): $DEV_PANE"
echo "  DU (Pane 2): $DU_PANE"

# 7. Verify tm-send is installed globally
echo "Verifying tm-send installation..."

if command -v tm-send > /dev/null 2>&1; then
    echo "tm-send is installed at: $(which tm-send)"
else
    echo ""
    echo "ERROR: tm-send is not installed!"
    echo ""
    echo "tm-send is a GLOBAL tool that must be installed to ~/.local/bin/tm-send"
    echo "It is NOT project-specific - one installation serves all projects."
    echo ""
    echo "Please install tm-send first before running this script."
    echo ""
    tmux kill-session -t $SESSION_NAME
    exit 1
fi

# 8. Start Claude Code in each pane
echo "Starting Claude Code instances..."
tmux send-keys -t $SESSION_NAME:0.0 "cd $PROJECT_ROOT && claude --dangerously-skip-permissions" C-m
tmux send-keys -t $SESSION_NAME:0.1 "cd $PROJECT_ROOT && claude --dangerously-skip-permissions" C-m
tmux send-keys -t $SESSION_NAME:0.2 "cd $PROJECT_ROOT && claude --dangerously-skip-permissions" C-m

# 9. Wait for Claude Code to start
echo "Waiting for Claude Code to start (15 seconds)..."
sleep 15

# 10. Initialize roles
echo "Initializing roles..."
tmux send-keys -t $SESSION_NAME:0.0 "/init-role PO" C-m
tmux send-keys -t $SESSION_NAME:0.0 C-m

tmux send-keys -t $SESSION_NAME:0.1 "/init-role DEV" C-m
tmux send-keys -t $SESSION_NAME:0.1 C-m

tmux send-keys -t $SESSION_NAME:0.2 "/init-role DU" C-m
tmux send-keys -t $SESSION_NAME:0.2 C-m

# 11. Wait for initialization
echo "Waiting for role initialization (10 seconds)..."
sleep 10

# 12. Update prompt files with actual pane IDs and project root
echo "Updating prompt files with pane IDs..."

# Update PO_PROMPT.md
sed -i "s|\${PROJECT_ROOT}|$PROJECT_ROOT|g" "$PROMPTS_DIR/PO_PROMPT.md" 2>/dev/null || true

# Update DEV_PROMPT.md
sed -i "s|\${PROJECT_ROOT}|$PROJECT_ROOT|g" "$PROMPTS_DIR/DEV_PROMPT.md" 2>/dev/null || true

# Update DU_PROMPT.md
sed -i "s|\${PROJECT_ROOT}|$PROJECT_ROOT|g" "$PROMPTS_DIR/DU_PROMPT.md" 2>/dev/null || true

echo ""
echo "=========================================="
echo "Packaging Agent Team Setup Complete!"
echo "=========================================="
echo ""
echo "Session: $SESSION_NAME"
echo "Project: $PROJECT_ROOT"
echo ""
echo "Roles:"
echo "  PO (Pane 0): $PO_PANE"
echo "  DEV (Pane 1): $DEV_PANE"
echo "  DU (Pane 2): $DU_PANE"
echo ""
echo "To attach to the session:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "To send messages (from outside tmux):"
echo "  tm-send -s $SESSION_NAME PO \"BOSS: Your message here\""
echo ""
echo "To list roles in session:"
echo "  tm-send -s $SESSION_NAME --list"
echo ""
echo "Next steps:"
echo "1. Attach to the session"
echo "2. Verify all agents have initialized properly"
echo "3. Send initial goal to PO (from Boss terminal)"
echo ""
echo "=========================================="
