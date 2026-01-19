# Technical Spec: Service Restart Standardization

**Author:** TL
**Date:** 2026-01-09
**Priority:** P0 (Boss directive)
**Size:** M (4 scripts + documentation)

---

## Overview

Standardize service restart process to eliminate port conflicts and duplicate workers.

**Current Problems:**
- Mix of systemd, bash, manual commands
- Duplicate Celery workers (2+ groups)
- Multiple frontend instances on port 3334
- 30+ minutes debugging port issues

---

## Architecture

### Scripts Location

```
scripts/
├── restart-frontend.sh   # Next.js (port 3334)
├── restart-backend.sh    # FastAPI (port 17061)
├── restart-terminal.sh   # Node.js (port 17071)
├── restart-celery.sh     # Celery worker (no port)
└── lib/
    └── common.sh         # Shared functions
```

### Common Library (`lib/common.sh`)

```bash
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

# Check if port is in use
port_in_use() {
    local port=$1
    lsof -i :$port > /dev/null 2>&1
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
```

---

## Script Specifications

### 1. restart-frontend.sh

**Port:** 3334
**Process:** Next.js (`node.*next`)
**Log:** `/tmp/ai-teams-frontend.log`

```bash
#!/bin/bash
# Restart Frontend (Next.js)
set -e
source "$(dirname "$0")/lib/common.sh"

PORT=3334
SERVICE_NAME="ai-teams-frontend"
LOG_FILE="/tmp/ai-teams-frontend.log"
PROJECT_DIR="$(dirname "$0")/../frontend"

log_info "=== Restarting Frontend (port $PORT) ==="

# Step 1: Stop old process
OS=$(detect_os)
if [ "$OS" = "linux" ]; then
    # Stop systemd service if exists
    systemctl --user stop $SERVICE_NAME.service 2>/dev/null || true
fi

# Step 2: Kill any remaining processes on port
kill_port $PORT
pkill -f "node.*next" 2>/dev/null || true
sleep 1

# Step 3: Verify port free
verify_port_free $PORT || exit 1

# Step 4: Clean build (CRITICAL for Next.js)
log_info "Cleaning .next directory..."
rm -rf "$PROJECT_DIR/.next"

# Step 5: Build
log_info "Building frontend..."
cd "$PROJECT_DIR"
pnpm build >> "$LOG_FILE" 2>&1

# Step 6: Start service
log_info "Starting frontend..."
if [ "$OS" = "linux" ]; then
    systemctl --user start $SERVICE_NAME.service
else
    PORT=$PORT pnpm start >> "$LOG_FILE" 2>&1 &
fi

# Step 7: Verify running
sleep 3
verify_service_running $PORT || exit 1

# Step 8: Health check
if curl -s "http://localhost:$PORT/" > /dev/null; then
    log_info "✅ Frontend ready at http://localhost:$PORT"
else
    log_error "Frontend not responding to health check"
    exit 1
fi
```

### 2. restart-backend.sh

**Port:** 17061
**Process:** FastAPI (`uvicorn.*17061`)
**Log:** `/tmp/ai-teams-backend.log`

```bash
#!/bin/bash
# Restart Backend (FastAPI)
set -e
source "$(dirname "$0")/lib/common.sh"

PORT=17061
SERVICE_NAME="ai-teams-backend"
LOG_FILE="/tmp/ai-teams-backend.log"
PROJECT_DIR="$(dirname "$0")/../backend"

log_info "=== Restarting Backend (port $PORT) ==="

# Step 1: Stop old process
OS=$(detect_os)
if [ "$OS" = "linux" ]; then
    systemctl --user stop $SERVICE_NAME.service 2>/dev/null || true
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
if [ "$OS" = "linux" ]; then
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
```

### 3. restart-terminal.sh

**Port:** 17071
**Process:** Node.js terminal service (`node.*terminal`)
**Log:** `/tmp/ai-teams-terminal.log`

```bash
#!/bin/bash
# Restart Terminal Service (Node.js)
set -e
source "$(dirname "$0")/lib/common.sh"

PORT=17071
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
```

### 4. restart-celery.sh (UPDATE EXISTING)

**Port:** None (worker process)
**Process:** Celery (`celery.*worker`)
**Log:** `/tmp/ai-teams-celery.log`

```bash
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

# Step 4: Verify running (single worker)
sleep 3
WORKER_COUNT=$(pgrep -f "celery.*worker" | wc -l)
if [ "$WORKER_COUNT" -eq 0 ]; then
    log_error "Celery worker failed to start"
    exit 1
elif [ "$WORKER_COUNT" -gt 1 ]; then
    log_warn "Multiple Celery workers detected ($WORKER_COUNT) - this may indicate a problem"
fi

log_info "✅ Celery worker running (PID: $(pgrep -f 'celery.*worker' | head -1))"
```

---

## CLAUDE.md Update

Replace "Running Services" section with:

```markdown
## Running Services

**ALWAYS use the standardized restart scripts:**

```bash
# Restart individual services
./scripts/restart-frontend.sh   # Next.js (port 3334)
./scripts/restart-backend.sh    # FastAPI (port 17061)
./scripts/restart-terminal.sh   # Terminal (port 17071)
./scripts/restart-celery.sh     # Celery worker

# Check logs
tail -f /tmp/ai-teams-frontend.log
tail -f /tmp/ai-teams-backend.log
tail -f /tmp/ai-teams-terminal.log
tail -f /tmp/ai-teams-celery.log
```

**NEVER use manual commands like:**
- ❌ `pkill -f "next"`
- ❌ `systemctl --user restart ai-teams-frontend`
- ❌ `kill $(lsof -t -i:3334)`

Scripts handle: kill old → verify port free → start new → verify running
```

---

## Test Cases

1. **Port conflict resolution**: Start frontend twice → second start kills first
2. **Clean restart**: `restart-frontend.sh` removes .next before build
3. **Duplicate prevention**: Run `restart-celery.sh` twice → only 1 worker
4. **Cross-OS**: Scripts work on both Linux (systemctl) and macOS (launchctl)
5. **Error handling**: Script exits with error if port stays occupied

---

## Acceptance Criteria

- [ ] ONE script per service in `/scripts/`
- [ ] Scripts auto-kill old processes before starting
- [ ] Scripts verify port is free before starting
- [ ] Scripts verify service running after start
- [ ] No duplicate workers/instances possible
- [ ] Works on both Linux and macOS
- [ ] CLAUDE.md updated with correct commands
- [ ] Boss can restart without debugging port conflicts

---

## Implementation Order

1. Create `scripts/lib/common.sh` (shared functions)
2. Create `restart-frontend.sh`
3. Create `restart-backend.sh`
4. Create `restart-terminal.sh`
5. Update `restart-celery.sh`
6. Update CLAUDE.md
7. Test on Linux environment
