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
    else
        log_info ".env file already exists"
    fi

    # Install Python dependencies
    if [ -f "pyproject.toml" ]; then
        log_info "Installing Python dependencies with uv..."
        if command_exists uv; then
            uv pip install -e .
        else
            log_warning "uv not found, using pip..."
            pip install -e .
        fi
        log_success "Backend dependencies installed"
    else
        log_error "pyproject.toml not found"
        exit 1
    fi

    # Initialize demo database
    log_info "Creating demo database with test user..."
    python scripts/init_sqlite_demo.py
    log_success "Demo database initialized"

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
    echo "Demo Credentials (auto-created):"
    echo "  Email: test@example.com"
    echo "  Password: test123"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Start the backend:"
    echo "   cd backend"
    echo "   uvicorn app.main:app --reload --port 17061"
    echo ""
    echo "2. In another terminal, start the frontend:"
    echo "   cd frontend"
    echo "   pnpm dev"
    echo ""
    echo "3. Open browser:"
    echo "   http://localhost:3334"
    echo ""
    echo "4. Login with demo credentials above"
    echo ""
    echo "Installed Components:"
    echo "  - Backend: FastAPI at port 17061"
    echo "  - Frontend: Next.js at port 3334"
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
