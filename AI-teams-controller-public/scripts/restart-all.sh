#!/bin/bash
# AI Teams Controller - Restart All Services
# Uses the standardized individual restart scripts

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_status() {
    echo ""
    echo "=== AI Teams Controller Service Status ==="
    echo ""

    # Check each service port
    if lsof -i :17061 > /dev/null 2>&1; then
        echo -e "Backend (17061):  ${GREEN}RUNNING${NC}"
    else
        echo -e "Backend (17061):  ${RED}STOPPED${NC}"
    fi

    if pgrep -f "celery.*worker" > /dev/null 2>&1; then
        local main_workers=$(pgrep -f "uv run celery" | wc -l)
        local total=$(pgrep -f "celery.*worker" | wc -l)
        echo -e "Celery:           ${GREEN}RUNNING${NC} ($main_workers main, $total total)"
    else
        echo -e "Celery:           ${RED}STOPPED${NC}"
    fi

    if lsof -i :3334 > /dev/null 2>&1; then
        echo -e "Frontend (3334):  ${GREEN}RUNNING${NC}"
    else
        echo -e "Frontend (3334):  ${RED}STOPPED${NC}"
    fi

    if lsof -i :17071 > /dev/null 2>&1; then
        echo -e "Terminal (17071): ${GREEN}RUNNING${NC}"
    else
        echo -e "Terminal (17071): ${RED}STOPPED${NC}"
    fi

    echo ""
}

restart_all() {
    echo ""
    echo "=========================================="
    echo "  Restarting All Services"
    echo "=========================================="
    echo ""

    log_info "Step 1/3: Restarting Backend..."
    "$SCRIPT_DIR/restart-backend.sh" || { log_error "Backend restart failed"; exit 1; }

    log_info "Step 2/3: Restarting Celery..."
    "$SCRIPT_DIR/restart-celery.sh" || { log_error "Celery restart failed"; exit 1; }

    log_info "Step 3/3: Restarting Frontend..."
    "$SCRIPT_DIR/restart-frontend.sh" || { log_warn "Frontend restart failed (optional)"; }

    echo ""
    echo "=========================================="
    echo "  All services restarted!"
    echo "=========================================="
    echo ""

    show_status
}

case "${1:-}" in
    --backend|-b)
        "$SCRIPT_DIR/restart-backend.sh"
        ;;
    --celery|-c)
        "$SCRIPT_DIR/restart-celery.sh"
        ;;
    --frontend|-f)
        "$SCRIPT_DIR/restart-frontend.sh"
        ;;
    --terminal|-t)
        "$SCRIPT_DIR/restart-terminal.sh"
        ;;
    --status|-s)
        show_status
        ;;
    --help|-h)
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Options:"
        echo "  (none)          Restart all services (backend + celery + frontend)"
        echo "  --backend, -b   Restart backend only"
        echo "  --celery, -c    Restart Celery only"
        echo "  --frontend, -f  Restart frontend only"
        echo "  --terminal, -t  Restart terminal only"
        echo "  --status, -s    Show service status"
        echo "  --help, -h      Show this help"
        echo ""
        echo "Examples:"
        echo "  $0              # Restart all services"
        echo "  $0 --celery     # Restart just Celery"
        echo "  $0 --status     # Check what's running"
        ;;
    "")
        restart_all
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
