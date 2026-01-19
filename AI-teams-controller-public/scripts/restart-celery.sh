#!/bin/bash
# Restart Celery Worker
set -e
source "$(dirname "$0")/lib/common.sh"

LOG_FILE="/tmp/ai-teams-celery.log"
PROJECT_DIR="$(dirname "$0")/../backend"

log_info "=== Restarting Celery Worker ==="

# Step 1: Stop all Celery workers (prevent duplicates)
OS=$(detect_os)
if [ "$OS" = "linux" ]; then
    systemctl --user stop ai-teams-celery.service 2>/dev/null || true
fi

# Kill ALL celery workers (including duplicates)
pkill -f "celery.*worker" 2>/dev/null || true
sleep 2

# Force kill if still running
if pgrep -f "celery.*worker" > /dev/null; then
    log_warn "Force killing remaining Celery workers..."
    pkill -9 -f "celery.*worker" 2>/dev/null || true
    sleep 1
fi

# Step 2: Verify no workers running
if pgrep -f "celery.*worker" > /dev/null; then
    log_error "Failed to stop all Celery workers"
    exit 1
fi
log_info "All Celery workers stopped"

# Step 3: Start new worker
log_info "Starting Celery worker..."
cd "$PROJECT_DIR"
if [ "$OS" = "linux" ]; then
    systemctl --user start ai-teams-celery.service
else
    nohup uv run celery -A celery_config.celery_app worker --loglevel=info >> "$LOG_FILE" 2>&1 &
fi

# Step 4: Verify running (check main worker only, not child processes)
sleep 3
# Count only main celery processes (uv run), not worker children (prefork pool)
MAIN_WORKER_COUNT=$(pgrep -f "uv run celery" | wc -l)
if [ "$MAIN_WORKER_COUNT" -eq 0 ]; then
    log_error "Celery worker failed to start"
    exit 1
elif [ "$MAIN_WORKER_COUNT" -gt 1 ]; then
    log_error "Multiple main Celery workers detected ($MAIN_WORKER_COUNT) - duplicate workers!"
    exit 1
fi

MAIN_PID=$(pgrep -f "uv run celery" | head -1)
TOTAL_PROCESSES=$(pgrep -f "celery.*worker" | wc -l)
log_info "✅ Celery worker running (main PID: $MAIN_PID, total processes: $TOTAL_PROCESSES)"
