#!/bin/bash
#
# Memory System Installation Script
# Fully automated installation with zero manual setup required
#
# Usage: ./install-memory-system.sh
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
QDRANT_PORT=16333
QDRANT_CONTAINER_NAME="memory-system-qdrant"
PYTHON_MIN_VERSION="3.10"

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
    echo "║         Memory System Installation Script             ║"
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

    # Check Python
    if ! command_exists python3; then
        log_error "Python 3 is not installed. Please install Python 3.10 or higher."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_info "Found Python $PYTHON_VERSION"

    if ! version_ge "$PYTHON_VERSION" "$PYTHON_MIN_VERSION"; then
        log_error "Python $PYTHON_MIN_VERSION or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi

    # Check pip
    if ! command_exists pip3; then
        log_error "pip3 is not installed. Please install pip."
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Check Docker availability and permissions
check_docker() {
    if ! command_exists docker; then
        log_warning "Docker is not installed"
        return 1
    fi

    # Check if Docker daemon is running and if we have permissions
    if docker info >/dev/null 2>&1; then
        log_success "Docker is available and running"
        return 0
    fi

    # Check if it's a permission error
    if docker info 2>&1 | grep -q "permission denied"; then
        log_warning "Docker permission denied - user not in docker group"

        # Attempt to fix automatically with sudo
        log_info "Attempting to add user to docker group..."

        if command_exists sudo; then
            if sudo usermod -aG docker "$USER"; then
                log_success "User added to docker group successfully"
                echo ""
                log_warning "IMPORTANT: You must log out and log back in for group changes to take effect"
                log_warning "Or run: newgrp docker"
                echo ""
                read -p "Do you want to continue with 'newgrp docker' now? (y/n) " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    log_info "Attempting to activate docker group with newgrp..."
                    # Note: newgrp spawns a new shell, so we need to re-run docker check
                    if sg docker -c "docker info >/dev/null 2>&1"; then
                        log_success "Docker access confirmed with new group"
                        return 0
                    fi
                fi

                log_error "Please log out and log back in, then run this script again"
                exit 1
            else
                log_error "Failed to add user to docker group (sudo failed)"
                log_info "Manual fix: sudo usermod -aG docker \$USER"
                log_info "Then log out and log back in"
                exit 1
            fi
        else
            log_error "sudo not available - cannot automatically fix Docker permissions"
            log_info "Manual fix: sudo usermod -aG docker \$USER"
            log_info "Then log out and log back in"
            exit 1
        fi
    else
        log_warning "Docker is installed but not running or inaccessible"
        log_info "Try: sudo systemctl start docker"
        return 1
    fi
}

# Install Qdrant using Docker
install_qdrant_docker() {
    log_info "Installing Qdrant using Docker..."

    # Check if port is already in use by ANY container
    if docker ps --format '{{.Names}}\t{{.Ports}}' | grep -q ":${QDRANT_PORT}->"; then
        local existing_container=$(docker ps --format '{{.Names}}\t{{.Ports}}' | grep ":${QDRANT_PORT}->" | cut -f1)
        log_info "Port ${QDRANT_PORT} is already in use by container: $existing_container"

        # Verify Qdrant is accessible
        if curl -s "http://localhost:${QDRANT_PORT}" >/dev/null 2>&1; then
            log_success "Qdrant is already running on http://localhost:${QDRANT_PORT}"
            return 0
        else
            log_error "Port ${QDRANT_PORT} is in use but Qdrant is not responding"
            return 1
        fi
    fi

    # Check if container already exists (but not running)
    if docker ps -a --format '{{.Names}}' | grep -q "^${QDRANT_CONTAINER_NAME}$"; then
        log_info "Qdrant container already exists. Checking status..."

        if docker ps --format '{{.Names}}' | grep -q "^${QDRANT_CONTAINER_NAME}$"; then
            log_success "Qdrant is already running on port $QDRANT_PORT"
            return 0
        else
            log_info "Starting existing Qdrant container..."
            docker start "$QDRANT_CONTAINER_NAME"
            sleep 2
            log_success "Qdrant container started"
            return 0
        fi
    fi

    # Pull latest Qdrant image
    log_info "Pulling Qdrant Docker image..."
    docker pull qdrant/qdrant:latest

    # Create and start container
    log_info "Creating Qdrant container on port $QDRANT_PORT..."
    docker run -d \
        --name "$QDRANT_CONTAINER_NAME" \
        -p "${QDRANT_PORT}:6333" \
        -v "$(pwd)/qdrant_storage:/qdrant/storage" \
        qdrant/qdrant:latest

    # Wait for Qdrant to be ready
    log_info "Waiting for Qdrant to be ready..."
    for i in {1..30}; do
        if curl -s "http://localhost:${QDRANT_PORT}" >/dev/null 2>&1; then
            log_success "Qdrant is ready on http://localhost:${QDRANT_PORT}"
            return 0
        fi
        sleep 1
    done

    log_error "Qdrant failed to start within 30 seconds"
    return 1
}

# Install Qdrant standalone (fallback)
install_qdrant_standalone() {
    log_warning "Docker not available. Qdrant standalone installation not implemented."
    log_warning "Please install Docker or set up Qdrant manually."
    log_info "Qdrant installation guide: https://qdrant.tech/documentation/quick-start/"
    return 1
}

# Setup Qdrant
setup_qdrant() {
    log_info "Setting up Qdrant vector database..."

    if check_docker; then
        if install_qdrant_docker; then
            log_success "Qdrant setup complete"
            return 0
        else
            log_error "Failed to install Qdrant with Docker"
            return 1
        fi
    else
        install_qdrant_standalone
        return $?
    fi
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."

    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv .venv
    fi

    # Activate virtual environment
    source .venv/bin/activate

    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip >/dev/null 2>&1

    # Install dependencies
    if [ -f "requirements.txt" ]; then
        log_info "Installing from requirements.txt..."
        pip install -r requirements.txt
    else
        log_info "Installing core dependencies..."
        pip install qdrant-client voyageai fastmcp pydantic python-dotenv
    fi

    log_success "Python dependencies installed"
}

# Configure environment
configure_environment() {
    log_info "Configuring environment..."

    # Create .env from .env.example if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_info "Created .env from .env.example"
        else
            log_error ".env.example not found"
            return 1
        fi
    fi

    # Check for Voyage API key
    if ! grep -q "VOYAGE_API_KEY=.*[a-zA-Z0-9]" .env; then
        log_warning "Voyage API key not found in .env"

        # Check for demo API keys first
        local demo_keys_file="$SCRIPT_DIR/../config/demo-api-keys.txt"
        if [ -f "$demo_keys_file" ]; then
            log_info "Found demo API keys, populating .env..."

            # Extract Voyage key from demo-api-keys.txt
            local voyage_key=$(grep "^VOYAGE_API_KEY=" "$demo_keys_file" | cut -d'=' -f2)

            if [ -n "$voyage_key" ]; then
                # Update .env with demo key
                sed -i "s/VOYAGE_API_KEY=.*/VOYAGE_API_KEY=$voyage_key/" .env
                log_success "Configured Voyage API key (demo)"
            else
                log_warning "Voyage API key not found in demo keys file"
            fi
        # Check if running interactively
        elif [ -t 0 ]; then
            echo ""
            read -p "Enter your Voyage AI API key (or press Enter to skip): " voyage_key

            if [ -n "$voyage_key" ]; then
                # Update .env with provided key
                sed -i "s/VOYAGE_API_KEY=.*/VOYAGE_API_KEY=$voyage_key/" .env
                log_success "Voyage API key configured"
            else
                log_warning "Skipping Voyage API key configuration"
                log_warning "You'll need to add it to .env manually before using the system"
            fi
        else
            log_warning "Non-interactive mode. You'll need to add Voyage API key to .env manually"
        fi
    else
        log_success "Voyage API key found in .env"
    fi

    # Verify Qdrant URL in .env
    if ! grep -q "QDRANT_URL=http://localhost:${QDRANT_PORT}" .env; then
        sed -i "s|QDRANT_URL=.*|QDRANT_URL=http://localhost:${QDRANT_PORT}|" .env
        log_info "Updated QDRANT_URL in .env to http://localhost:${QDRANT_PORT}"
    fi

    log_success "Environment configuration complete"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    # Activate venv for verification
    source .venv/bin/activate

    # Test Qdrant connection
    log_info "Testing Qdrant connection..."
    python3 -c "
from qdrant_client import QdrantClient
import sys

try:
    client = QdrantClient(url='http://localhost:${QDRANT_PORT}')
    collections = client.get_collections()
    print('✓ Qdrant connection successful')
    sys.exit(0)
except Exception as e:
    print(f'✗ Qdrant connection failed: {e}')
    sys.exit(1)
"

    if [ $? -eq 0 ]; then
        log_success "Qdrant connection verified"
    else
        log_error "Qdrant connection verification failed"
        return 1
    fi

    # Check if Voyage API key is configured
    source .env
    if [ -n "$VOYAGE_API_KEY" ] && [ "$VOYAGE_API_KEY" != "your-voyage-api-key-here" ]; then
        log_info "Testing Voyage API connection..."

        # Temporarily disable exit on error for Voyage API test
        set +e
        python3 -c "
import voyageai
import os
import sys

try:
    vo = voyageai.Client(api_key=os.getenv('VOYAGE_API_KEY'))
    # Simple test embedding
    result = vo.embed(texts=['test'], model='voyage-4-lite')
    if result.embeddings and len(result.embeddings[0]) == 1024:
        print('✓ Voyage API connection successful')
        sys.exit(0)
    else:
        print('✗ Voyage API returned unexpected result')
        sys.exit(1)
except Exception as e:
    print(f'✗ Voyage API connection failed: {e}')
    sys.exit(1)
" 2>/dev/null
        voyage_result=$?
        set -e
        # Re-enable exit on error

        if [ $voyage_result -eq 0 ]; then
            log_success "Voyage API connection verified"
        else
            log_warning "Voyage API verification failed (key may be invalid or missing)"
        fi
    else
        log_warning "Voyage API key not configured - skipping verification"
    fi

    # Verify skills installation
    log_info "Verifying skills installation..."
    if [ -d "$HOME/.claude/skills/memory-store" ] && [ -d "$HOME/.claude/skills/memory-recall" ]; then
        log_success "Skills verified (memory-store, memory-recall)"
    else
        log_error "Skills verification failed"
        return 1
    fi

    # Verify subagent installation
    log_info "Verifying subagent installation..."
    if [ -f "$HOME/.claude/agents/memory-only.md" ]; then
        log_success "Subagent verified (memory-only)"
    else
        log_error "Subagent verification failed"
        return 1
    fi

    # Verify hooks installation
    log_info "Verifying hooks installation..."
    if [ -x "$HOME/.claude/hooks/memory_store_reminder.py" ] && [ -x "$HOME/.claude/hooks/todowrite_memory_recall.py" ]; then
        log_success "Hooks verified (memory_store_reminder.py, todowrite_memory_recall.py)"
    else
        log_error "Hooks verification failed"
        return 1
    fi

    log_success "Installation verification complete"
}

# Install memory skills
install_skills() {
    log_info "Installing memory skills..."

    local skills_dir="$HOME/.claude/skills"
    mkdir -p "$skills_dir"

    # Install memory-store
    if [ -d "$skills_dir/memory-store" ]; then
        log_info "memory-store already installed, updating..."
        rm -rf "$skills_dir/memory-store"
    fi
    cp -r "$(pwd)/skills/memory-store" "$skills_dir/"
    log_success "Installed memory-store skill"

    # Install memory-recall
    if [ -d "$skills_dir/memory-recall" ]; then
        log_info "memory-recall already installed, updating..."
        rm -rf "$skills_dir/memory-recall"
    fi
    cp -r "$(pwd)/skills/memory-recall" "$skills_dir/"
    log_success "Installed memory-recall skill"

    log_success "Memory skills installation complete"
}

# Install memory subagent
install_subagent() {
    log_info "Installing memory subagent..."

    local agents_dir="$HOME/.claude/agents"
    mkdir -p "$agents_dir"

    # Install memory-only subagent
    if [ -f "$agents_dir/memory-only.md" ]; then
        log_info "memory-only already installed, updating..."
    fi
    cp "$(pwd)/subagents/memory-only/memory-only.md" "$agents_dir/"
    log_success "Installed memory-only subagent"

    log_success "Memory subagent installation complete"
}

# Install memory hooks
install_hooks() {
    log_info "Installing memory hooks..."

    local hooks_dir="$HOME/.claude/hooks"
    mkdir -p "$hooks_dir"

    # Install hooks
    for hook_file in hooks/*.py; do
        local hook_name=$(basename "$hook_file")
        if [ -f "$hooks_dir/$hook_name" ]; then
            log_info "$hook_name already installed, updating..."
        fi
        cp "$hook_file" "$hooks_dir/"
        chmod +x "$hooks_dir/$hook_name"
        log_success "Installed $hook_name"
    done

    log_success "Memory hooks installation complete"
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
    echo "1. Activate virtual environment:"
    echo "   source .venv/bin/activate"
    echo ""
    echo "2. Run MCP server:"
    echo "   python -m src.mcp_server.server"
    echo ""
    echo "3. Or configure Claude Code to use this MCP server"
    echo "   (see README.md for configuration instructions)"
    echo ""
    echo "Installed Components:"
    echo "  - Qdrant: http://localhost:${QDRANT_PORT}"
    echo "  - MCP Server: stdio transport"
    echo "  - Skills: memory-store, memory-recall"
    echo "  - Subagent: memory-only"
    echo "  - Hooks: memory_store_reminder.py, todowrite_memory_recall.py"
    echo ""
    echo "Memory Skills Usage:"
    echo "  - Use 'memory-store' to save coding patterns"
    echo "  - Use 'memory-recall' to retrieve relevant memories"
    echo "  - Hooks automatically trigger skills when appropriate"
    echo ""

    if ! grep -q "VOYAGE_API_KEY=.*[a-zA-Z0-9]" .env || grep -q "VOYAGE_API_KEY=your-voyage-api-key-here" .env; then
        echo "⚠️  Remember to add your Voyage API key to .env"
        echo ""
    fi
}

# Main installation flow
main() {
    print_banner

    log_info "Starting memory system installation..."
    echo ""

    # Step 1: Check prerequisites
    check_prerequisites
    echo ""

    # Step 2: Setup Qdrant
    setup_qdrant
    echo ""

    # Step 3: Install Python dependencies
    install_python_deps
    echo ""

    # Step 4: Configure environment
    configure_environment
    echo ""

    # Step 5: Install memory skills
    install_skills
    echo ""

    # Step 6: Install memory subagent
    install_subagent
    echo ""

    # Step 7: Install memory hooks
    install_hooks
    echo ""

    # Step 8: Verify installation
    verify_installation
    echo ""

    # Success!
    print_next_steps
}

# Run main function
main
