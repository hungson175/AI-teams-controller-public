#!/bin/bash
# Shared functions for all restart scripts

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "linux"
    fi
}

# Check if port is in use (handles both IPv4 and IPv6)
port_in_use() {
    local port=$1
    # Try lsof first (works for IPv4)
    if lsof -i :$port > /dev/null 2>&1; then
        return 0
    fi
    # Fall back to ss/netstat for IPv6
    if ss -tlnp 2>/dev/null | grep -q ":$port " || netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        return 0
    fi
    return 1
}

# Get PID using port
get_pid_on_port() {
    local port=$1
    lsof -t -i :$port 2>/dev/null | head -1
}

# Kill all processes on port
kill_port() {
    local port=$1
    local pids=$(lsof -t -i :$port 2>/dev/null)
    if [ -n "$pids" ]; then
        log_info "Killing processes on port $port: $pids"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Verify port is free
verify_port_free() {
    local port=$1
    local max_attempts=5
    for i in $(seq 1 $max_attempts); do
        if ! port_in_use $port; then
            return 0
        fi
        log_warn "Port $port still in use, attempt $i/$max_attempts..."
        kill_port $port
        sleep 1
    done
    log_error "Port $port still occupied after $max_attempts attempts"
    return 1
}

# Verify service running on port
verify_service_running() {
    local port=$1
    local max_attempts=10
    for i in $(seq 1 $max_attempts); do
        if port_in_use $port; then
            log_info "Service running on port $port (PID: $(get_pid_on_port $port))"
            return 0
        fi
        sleep 1
    done
    log_error "Service failed to start on port $port"
    return 1
}
