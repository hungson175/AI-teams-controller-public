#!/bin/bash
# install-tmux-skill.sh - One-command install for tmux-team-creator skill

set -e

SKILL_FILE="tmux-team-creator.skill"
SKILL_DIR="$HOME/.claude/skills"
TM_SEND_PATH="$HOME/.local/bin/tm-send"

echo "📦 Installing tmux-team-creator skill..."
echo ""

# Step 1: Install tm-send (CRITICAL)
if [ ! -f "$TM_SEND_PATH" ]; then
    echo "Installing tm-send..."
    mkdir -p $HOME/.local/bin
    cp tm-send $TM_SEND_PATH
    chmod +x $TM_SEND_PATH
    echo "✅ tm-send installed to $TM_SEND_PATH"
else
    echo "✓ tm-send already installed at $TM_SEND_PATH"
fi

# Step 1.5: Ensure ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "⚠️  Adding ~/.local/bin to PATH..."

    # Determine which profile file to use
    if [ -f "$HOME/.bashrc" ]; then
        PROFILE_FILE="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        PROFILE_FILE="$HOME/.bash_profile"
    else
        PROFILE_FILE="$HOME/.profile"
    fi

    # Add PATH export if not already present
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$PROFILE_FILE"; then
        echo '' >> "$PROFILE_FILE"
        echo '# Added by tmux-team-creator installer' >> "$PROFILE_FILE"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$PROFILE_FILE"
        echo "✅ Added ~/.local/bin to PATH in $PROFILE_FILE"
        echo ""
        echo "📌 IMPORTANT: Run this command to update your current shell:"
        echo "   source $PROFILE_FILE"
        echo ""
        echo "   Or restart your terminal."
    fi
else
    echo "✓ ~/.local/bin already in PATH"
fi

echo ""

# Step 2: Install skill
echo "Installing skill..."
mkdir -p "$SKILL_DIR"
unzip -o "$SKILL_FILE" -d "$SKILL_DIR"

echo ""
echo "✅ Successfully installed tmux-team-creator skill"
echo "   Location: $SKILL_DIR/tmux-team-creator"
echo ""
echo "📖 Usage:"
echo "   • Invoke with: /tmux-team-creator"
echo "   • Or ask Claude: 'Create a tmux team for my project'"
echo ""
echo "🔗 For more information, see the skill documentation at:"
echo "   $SKILL_DIR/tmux-team-creator/SKILL.md"
