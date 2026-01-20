#!/bin/bash
# Restart Backend (FastAPI)
set -e
source "$(dirname "$0")/lib/common.sh"

# Port 17063 - Unusual port to avoid conflicts with common services
PORT=17063
SERVICE_NAME="ai-teams-backend"
LOG_FILE="/tmp/ai-teams-backend.log"
PROJECT_DIR="$(dirname "$0")/../backend"

log_info "=== Restarting Backend (port $PORT) ==="

# Step 1: Stop old process
OS=$(detect_os)
if [ "$OS" = "linux" ]; then
    # Only use systemd if service is loaded
    if systemctl --user is-enabled $SERVICE_NAME.service &>/dev/null || systemctl --user is-active $SERVICE_NAME.service &>/dev/null; then
        systemctl --user stop $SERVICE_NAME.service 2>/dev/null || true
    fi
fi

# Step 2: Kill any remaining processes
kill_port $PORT
pkill -f "uvicorn.*$PORT" 2>/dev/null || true
sleep 1

# Step 3: Verify port free
verify_port_free $PORT || exit 1

# Step 4: Start service
log_info "Starting backend..."
cd "$PROJECT_DIR"
if [ "$OS" = "linux" ] && (systemctl --user is-enabled $SERVICE_NAME.service &>/dev/null || systemctl --user is-active $SERVICE_NAME.service &>/dev/null); then
    systemctl --user start $SERVICE_NAME.service
else
    nohup uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT >> "$LOG_FILE" 2>&1 &
fi

# Step 5: Verify running
sleep 2
verify_service_running $PORT || exit 1

# Step 6: Health check
if curl -s "http://localhost:$PORT/health" | grep -q "healthy"; then
    log_info "✅ Backend ready at http://localhost:$PORT"
else
    log_error "Backend health check failed"
    exit 1
fi
