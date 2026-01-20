#!/bin/bash
#
# tmux Team Creator Skill Installation Script
# Professional installation with verification and error handling
#
# Usage: ./install-tmux-skill.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuration
SKILL_FILE="tmux-team-creator.skill"
SKILL_DIR="$HOME/.claude/skills"
TM_SEND_PATH="$HOME/.local/bin/tm-send"
BASH_MIN_VERSION="4.0"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║                                                        ║"
    echo "║     tmux Team Creator Skill Installation              ║"
    echo "║                                                        ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Compare version numbers
version_ge() {
    # Returns 0 if $1 >= $2
    printf '%s\n%s' "$2" "$1" | sort -V -C
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check unzip
    if ! command_exists unzip; then
        log_error "unzip is not installed. Please install unzip."
        log_info "On Ubuntu/Debian: sudo apt-get install unzip"
        log_info "On macOS: brew install unzip"
        exit 1
    fi
    log_info "Found unzip"

    # Check bash version
    BASH_VERSION_NUM="${BASH_VERSION%%.*}"
    if [ "$BASH_VERSION_NUM" -lt 4 ]; then
        log_error "Bash 4.0 or higher is required. Found: $BASH_VERSION"
        exit 1
    fi
    log_info "Found Bash $BASH_VERSION"

    # Check tmux
    if ! command_exists tmux; then
        log_warning "tmux is not installed. Skill requires tmux for team creation."
        log_info "On Ubuntu/Debian: sudo apt-get install tmux"
        log_info "On macOS: brew install tmux"
        log_info "Installation will continue, but skill won't work without tmux."
        echo ""
    else
        log_info "Found tmux $(tmux -V | cut -d' ' -f2)"
    fi

    log_success "Prerequisites check passed"
}

# Install tm-send
install_tm_send() {
    log_info "Installing tm-send tool..."

    if [ ! -f "tm-send" ]; then
        log_error "tm-send file not found in current directory"
        exit 1
    fi

    mkdir -p "$HOME/.local/bin"

    if [ -f "$TM_SEND_PATH" ]; then
        log_info "tm-send already installed, updating..."
    fi

    cp tm-send "$TM_SEND_PATH"
    chmod +x "$TM_SEND_PATH"
    log_success "Installed tm-send to $TM_SEND_PATH"
}

# Ensure ~/.local/bin is in PATH
ensure_path() {
    log_info "Checking PATH configuration..."

    if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
        log_success "~/.local/bin already in PATH"
        return 0
    fi

    log_warning "~/.local/bin not in PATH, adding..."

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
        log_success "Added ~/.local/bin to PATH in $PROFILE_FILE"
        echo ""
        log_warning "IMPORTANT: Run this command to update your current shell:"
        echo "   source $PROFILE_FILE"
        echo ""
        log_info "Or restart your terminal"
        echo ""
    else
        log_success "PATH configuration already present in $PROFILE_FILE"
    fi
}

# Install skill
install_skill() {
    log_info "Installing tmux-team-creator skill..."

    if [ ! -f "$SKILL_FILE" ]; then
        log_error "Skill file not found: $SKILL_FILE"
        exit 1
    fi

    mkdir -p "$SKILL_DIR"

    if [ -d "$SKILL_DIR/tmux-team-creator" ]; then
        log_info "Skill already installed, updating..."
        rm -rf "$SKILL_DIR/tmux-team-creator"
    fi

    unzip -o -q "$SKILL_FILE" -d "$SKILL_DIR"
    log_success "Installed skill to $SKILL_DIR/tmux-team-creator"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    # Check skill directory exists
    if [ -d "$SKILL_DIR/tmux-team-creator" ]; then
        log_success "Skill verified (tmux-team-creator)"
    else
        log_error "Skill verification failed - directory not found"
        return 1
    fi

    # Check SKILL.md exists
    if [ -f "$SKILL_DIR/tmux-team-creator/SKILL.md" ]; then
        log_success "Skill documentation verified"
    else
        log_error "Skill documentation not found"
        return 1
    fi

    # Check tm-send executable
    if [ -x "$TM_SEND_PATH" ]; then
        log_success "tm-send verified (executable)"
    else
        log_error "tm-send verification failed - not executable"
        return 1
    fi

    log_success "Installation verification complete"
}

# Install slash command
install_command() {
    log_info "Installing /create-tmux-team command..."

    local COMMAND_DIR="$HOME/.claude/commands"
    local COMMAND_FILE="$SCRIPT_DIR/commands/create-tmux-team.md"

    if [ ! -f "$COMMAND_FILE" ]; then
        log_warning "Command file not found: $COMMAND_FILE (skipping)"
        return 0
    fi

    mkdir -p "$COMMAND_DIR"

    # Check if command already exists
    if [ -f "$COMMAND_DIR/create-tmux-team.md" ]; then
        log_info "Command already installed, updating..."
    fi

    # Copy command file
    cp "$COMMAND_FILE" "$COMMAND_DIR/"

    if [ -f "$COMMAND_DIR/create-tmux-team.md" ]; then
        log_success "Command installed: /create-tmux-team"
    else
        log_warning "Command installation may have failed (file not found after copy)"
        return 1
    fi
}

# Print next steps
print_next_steps() {
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║                                                        ║"
    echo "║           Installation Complete! ✓                    ║"
    echo "║                                                        ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Quick start - ONE COMMAND creates and starts team:"
    echo "   /create-tmux-team"
    echo ""
    echo "2. Or use skill directly:"
    echo "   /tmux-team-creator"
    echo ""
    echo "3. Or ask Claude Code:"
    echo "   'Create a Scrum team for my project'"
    echo ""
    echo "Installed Components:"
    echo "  - Skill: tmux-team-creator"
    echo "  - Command: /create-tmux-team (one-command setup)"
    echo "  - Tool: tm-send (for agent communication)"
    echo "  - Templates: 3 team templates"
    echo ""
    echo "Documentation:"
    echo "  $SKILL_DIR/tmux-team-creator/SKILL.md"
    echo ""
    echo "Templates Included:"
    echo "  • Scrum Team (PO, SM, TL, BE, FE, QA)"
    echo "  • Lite Team (PO, Worker - minimal)"
    echo "  • McKinsey Research Team (EM, RL, PR, SR, DA, QR)"
    echo ""
}

# Main installation flow
main() {
    print_banner

    log_info "Starting tmux-team-creator skill installation..."
    echo ""

    # Step 1: Check prerequisites
    check_prerequisites
    echo ""

    # Step 2: Install tm-send
    install_tm_send
    echo ""

    # Step 3: Ensure PATH
    ensure_path
    echo ""

    # Step 4: Install skill
    install_skill
    echo ""

    # Step 5: Install slash command
    install_command
    echo ""

    # Step 6: Verify installation
    verify_installation
    echo ""

    # Success!
    print_next_steps
}

# Run main function
main
