#!/bin/bash
# Restart Terminal Service (Node.js)
set -e
source "$(dirname "$0")/lib/common.sh"

# Port 17073 - Unusual port to avoid conflicts with common services
PORT=17073
LOG_FILE="/tmp/ai-teams-terminal.log"
PROJECT_DIR="$(dirname "$0")/../terminal-service"

log_info "=== Restarting Terminal Service (port $PORT) ==="

# Step 1: Kill old process
kill_port $PORT
pkill -f "node.*terminal" 2>/dev/null || true
sleep 1

# Step 2: Verify port free
verify_port_free $PORT || exit 1

# Step 3: Start service
log_info "Starting terminal service..."
cd "$PROJECT_DIR"
nohup node server.js >> "$LOG_FILE" 2>&1 &

# Step 4: Verify running
sleep 2
verify_service_running $PORT || exit 1

log_info "✅ Terminal service ready at http://localhost:$PORT"
