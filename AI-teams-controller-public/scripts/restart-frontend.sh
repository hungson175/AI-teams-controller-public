#!/bin/bash
# Restart Frontend (Next.js) - P0 Fix Version
# Fixes recurring 500 errors on static chunks
set -e
source "$(dirname "$0")/lib/common.sh"

PORT=3334
SERVICE_NAME="ai-teams-frontend"
LOG_FILE="/tmp/ai-teams-frontend.log"
# Use absolute path to avoid issues after cd
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../frontend" && pwd)"

log_info "=== Restarting Frontend (port $PORT) ==="

# Step 1: DISABLE service (not just stop - prevents race condition)
OS=$(detect_os)
if [ "$OS" = "linux" ]; then
    systemctl --user disable --now $SERVICE_NAME.service 2>/dev/null || true
    log_info "Service disabled"
fi

# Step 2: Kill remaining processes on port (specific to this port only)
kill_port $PORT
sleep 1

# Step 3: Verify port free
verify_port_free $PORT || exit 1

# Step 4: Clean build (CRITICAL)
log_info "Cleaning .next directory..."
rm -rf "$PROJECT_DIR/.next"

# VERIFY deletion (P0 fix)
if [ -d "$PROJECT_DIR/.next" ]; then
    log_error "CRITICAL: .next directory still exists after rm -rf!"
    exit 1
fi
log_info "Verified: .next deleted"

# Step 5: Build
log_info "Building frontend..."
cd "$PROJECT_DIR"
# Set build version timestamp (for browser console logging)
export NEXT_PUBLIC_BUILD_VERSION=$(date '+%Y-%m-%d %H:%M:%S')
log_info "Build version: $NEXT_PUBLIC_BUILD_VERSION"
if ! pnpm build >> "$LOG_FILE" 2>&1; then
    log_error "Build command failed (check $LOG_FILE for details)"
    tail -20 "$LOG_FILE"
    exit 1
fi

# Step 6: Verify build artifacts exist
if [ ! -f "$PROJECT_DIR/.next/BUILD_ID" ]; then
    log_error "Build failed: BUILD_ID not found after successful build command"
    ls -la "$PROJECT_DIR/.next/" 2>&1 || log_error ".next directory doesn't exist"
    exit 1
fi

BUILD_ID=$(cat "$PROJECT_DIR/.next/BUILD_ID")
log_info "Build complete: BUILD_ID=$BUILD_ID"

# Step 7: Verify chunk files exist
CHUNK_COUNT=$(ls "$PROJECT_DIR/.next/static/chunks/"*.js 2>/dev/null | wc -l)
if [ "$CHUNK_COUNT" -lt 10 ]; then
    log_error "Build failed: Only $CHUNK_COUNT chunk files (expected 10+)"
    exit 1
fi
log_info "Verified: $CHUNK_COUNT chunk files generated"

# Step 8: Re-enable and start service
if [ "$OS" = "linux" ]; then
    systemctl --user enable $SERVICE_NAME.service
    systemctl --user start $SERVICE_NAME.service
else
    PORT=$PORT pnpm start >> "$LOG_FILE" 2>&1 &
fi

# Step 9: Wait and verify service
sleep 5
verify_service_running $PORT || exit 1

# Step 10: Verify chunks accessible (P0 fix)
WEBPACK_CHUNK=$(ls "$PROJECT_DIR/.next/static/chunks/webpack-"*.js 2>/dev/null | head -1 | xargs basename)
if [ -n "$WEBPACK_CHUNK" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/_next/static/chunks/$WEBPACK_CHUNK")
    if [ "$HTTP_CODE" != "200" ]; then
        log_error "CRITICAL: Chunk verification failed - $WEBPACK_CHUNK returned HTTP $HTTP_CODE"
        exit 1
    fi
    log_info "Verified: Chunks accessible (HTTP 200)"
fi

log_info "✅ Frontend ready at http://localhost:$PORT (BUILD_ID: $BUILD_ID)"
