#!/bin/bash
#
# AI Teams Controller Web UI Installation Script
# Installs Component 3: Next.js Frontend + FastAPI Backend + SQLite Demo
#
# Usage: ./install-web-ui.sh
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
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
PYTHON_MIN_VERSION="3.11"
NODE_MIN_VERSION="20"

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
    echo "║     AI Teams Controller Web UI Installation          ║"
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
    printf '%s\n%s' "$2" "$1" | sort -V -C
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python
    if ! command_exists python3; then
        log_error "Python 3 is not installed. Please install Python 3.11 or higher."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    log_info "Found Python $PYTHON_VERSION"

    # Check Node.js
    if ! command_exists node; then
        log_error "Node.js is not installed. Please install Node.js 20 or higher."
        exit 1
    fi

    NODE_VERSION=$(node --version | sed 's/v//')
    log_info "Found Node.js $NODE_VERSION"

    # Check pnpm
    if ! command_exists pnpm; then
        log_warning "pnpm is not installed. Installing pnpm..."
        npm install -g pnpm
        log_success "pnpm installed"
    else
        log_info "Found pnpm $(pnpm --version)"
    fi

    log_success "Prerequisites check passed"
}

# Install backend
install_backend() {
    log_info "Installing backend (FastAPI + SQLite)..."

    cd "$BACKEND_DIR"

    # Check for .env file
    if [ ! -f ".env" ]; then
        log_info "Creating .env from .env.example..."
        cp .env.example .env
        log_success ".env file created"

        # Check for demo API keys and populate .env
        local demo_keys_file="$SCRIPT_DIR/../config/demo-api-keys.txt"
        if [ -f "$demo_keys_file" ]; then
            log_info "Found demo API keys, populating .env..."

            # Extract keys from demo-api-keys.txt
            local xai_key=$(grep "^XAI_API_KEY=" "$demo_keys_file" | cut -d'=' -f2)
            local soniox_key=$(grep "^SONIOX_API_KEY=" "$demo_keys_file" | cut -d'=' -f2)

            # Update .env with demo keys
            if [ -n "$xai_key" ]; then
                sed -i "s|XAI_API_KEY=.*|XAI_API_KEY=$xai_key|" .env
                log_success "Configured xAI API key (demo)"
            fi

            if [ -n "$soniox_key" ]; then
                sed -i "s|SONIOX_API_KEY=.*|SONIOX_API_KEY=$soniox_key|" .env
                log_success "Configured Soniox API key (demo)"
            fi
        else
            log_warning "Demo API keys not found at: $demo_keys_file"
            log_warning "You'll need to add API keys to backend/.env manually"
        fi
    else
        log_info ".env file already exists"
    fi

    # Create virtual environment (PEP 668 compliance for Ubuntu 24.04+)
    if [ ! -d ".venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv .venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi

    # Activate virtual environment
    log_info "Activating virtual environment..."
    source .venv/bin/activate

    # Upgrade pip in venv
    log_info "Upgrading pip..."
    pip install --upgrade pip >/dev/null 2>&1

    # Install Python dependencies from requirements.txt
    if [ -f "requirements.txt" ]; then
        log_info "Installing Python dependencies from requirements.txt..."
        pip install -r requirements.txt
        log_success "Backend dependencies installed"
    elif [ -f "pyproject.toml" ]; then
        log_warning "requirements.txt not found, falling back to pyproject.toml..."
        if command_exists uv; then
            uv pip install -e .
        else
            pip install -e .
        fi
        log_success "Backend dependencies installed"
    else
        log_error "Neither requirements.txt nor pyproject.toml found"
        exit 1
    fi

    # Initialize demo database
    log_info "Creating demo database with test user..."
    python scripts/init_sqlite_demo.py
    log_success "Demo database initialized"

    # Deactivate venv
    deactivate

    # Display demo credentials prominently
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║                                                        ║"
    echo "║              DEMO CREDENTIALS CREATED                 ║"
    echo "║                                                        ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    log_success "Email:    test@example.com"
    log_success "Password: test123"
    echo ""
    log_warning "WARNING: Included test API keys may have been revoked already."
    log_warning "If you see auth errors, provide your own API keys."
    log_warning "These are temporary test keys for initial testing only."
    echo ""

    cd "$SCRIPT_DIR"
}

# Install frontend
install_frontend() {
    log_info "Installing frontend (Next.js)..."

    cd "$FRONTEND_DIR"

    # Install dependencies
    log_info "Installing Node.js dependencies..."
    pnpm install
    log_success "Frontend dependencies installed"

    cd "$SCRIPT_DIR"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    # Check backend database
    if [ -f "$BACKEND_DIR/aicontroller.db" ]; then
        log_success "SQLite database verified (aicontroller.db)"
    else
        log_error "Database file not found"
        return 1
    fi

    # Check backend dependencies
    if [ -d "$BACKEND_DIR/.venv" ] || python3 -c "import fastapi" 2>/dev/null; then
        log_success "Backend dependencies verified"
    else
        log_warning "Backend dependencies may not be fully installed"
    fi

    # Check frontend dependencies
    if [ -d "$FRONTEND_DIR/node_modules" ]; then
        log_success "Frontend dependencies verified"
    else
        log_error "Frontend dependencies not found"
        return 1
    fi

    log_success "Installation verification complete"
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
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║                                                        ║"
    echo "║                DEMO CREDENTIALS                        ║"
    echo "║                                                        ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    log_success "Email:    test@example.com"
    log_success "Password: test123"
    echo ""
    log_warning "WARNING: Included test API keys may have been revoked already."
    log_warning "If you see auth errors, provide your own API keys."
    log_warning "These are temporary test keys for initial testing only."
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Start the backend:"
    echo "   cd backend"
    echo "   source .venv/bin/activate"
    echo "   uvicorn app.main:app --reload --port 17063"
    echo ""
    echo "2. In another terminal, start the frontend:"
    echo "   cd frontend"
    echo "   pnpm dev"
    echo ""
    echo "3. Open browser:"
    echo "   http://localhost:3337"
    echo ""
    echo "4. Login with demo credentials above"
    echo ""
    echo "Installed Components:"
    echo "  - Backend: FastAPI at port 17063"
    echo "  - Frontend: Next.js at port 3337"
    echo "  - Database: SQLite at backend/aicontroller.db"
    echo "  - Demo user: test@example.com / test123"
    echo ""
    echo "Configuration:"
    echo "  - Backend config: backend/.env"
    echo "  - Frontend config: frontend/.env.local (if needed)"
    echo ""
}

# Main installation flow
main() {
    print_banner

    log_info "Starting Web UI installation..."
    echo ""

    # Step 1: Check prerequisites
    check_prerequisites
    echo ""

    # Step 2: Install backend
    install_backend
    echo ""

    # Step 3: Install frontend
    install_frontend
    echo ""

    # Step 4: Verify installation
    verify_installation
    echo ""

    # Success!
    print_next_steps
}

# Run main function
main
