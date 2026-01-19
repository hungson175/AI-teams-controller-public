#!/bin/bash
# Test Suite for Service Restart Scripts
# Validates restart scripts for backend, frontend, celery services
# Based on proven patterns from production debugging

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# Test configuration
BACKEND_PORT=17061
FRONTEND_PORT=3334
TEST_RESULTS=()
FAILED_TESTS=0
TOTAL_TESTS=0

# Helper functions
run_test() {
    local test_name="$1"
    local test_cmd="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    log_info "Running test: $test_name"
    if eval "$test_cmd"; then
        TEST_RESULTS+=("✅ PASS: $test_name")
        return 0
    else
        TEST_RESULTS+=("❌ FAIL: $test_name")
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Test 1: Backend - Single Instance Check
test_backend_single_instance() {
    log_info "Test 1: Backend - Verify single instance running"

    # Count actual Python uvicorn processes (not uv wrapper)
    # uv creates: parent "uv run" + child "python uvicorn"
    local backend_count=$(pgrep -f "python.*uvicorn.*17061" | wc -l)

    if [ "$backend_count" -eq 0 ]; then
        log_error "No backend process found"
        return 1
    elif [ "$backend_count" -gt 1 ]; then
        log_error "Multiple backend processes detected ($backend_count)"
        log_error "PIDs: $(pgrep -f 'python.*uvicorn.*17061')"
        return 1
    fi

    log_info "Backend: Single instance verified (PID: $(pgrep -f 'python.*uvicorn.*17061'))"
    return 0
}

# Test 2: Backend - Port Binding Check (EADDRINUSE prevention)
test_backend_port_binding() {
    log_info "Test 2: Backend - Verify port $BACKEND_PORT is properly bound"

    # Check if port is listening
    if ! lsof -i :$BACKEND_PORT > /dev/null 2>&1; then
        log_error "Port $BACKEND_PORT is not listening"
        return 1
    fi

    # Get PID on port (filter out SSH tunnels)
    local port_pid=$(lsof -i :$BACKEND_PORT -sTCP:LISTEN | grep -v ssh | awk 'NR==2 {print $2}')
    local process_pid=$(pgrep -f "python.*uvicorn.*$BACKEND_PORT" | head -1)

    if [ -z "$port_pid" ]; then
        log_error "No service process found on port $BACKEND_PORT (only SSH tunnel)"
        return 1
    fi

    if [ "$port_pid" != "$process_pid" ]; then
        log_error "Port PID ($port_pid) != Process PID ($process_pid)"
        return 1
    fi

    log_info "Backend: Port $BACKEND_PORT correctly bound to PID $port_pid"
    return 0
}

# Test 3: Backend - Health Check
test_backend_health() {
    log_info "Test 3: Backend - Health endpoint check"

    # Wait up to 10 seconds for backend to be ready
    for i in {1..10}; do
        if curl -sf "http://localhost:$BACKEND_PORT/health" | grep -q "healthy"; then
            log_info "Backend: Health check PASSED"
            return 0
        fi
        sleep 1
    done

    log_error "Backend health check failed after 10 seconds"
    return 1
}

# Test 4: Celery - Single Main Worker Check
test_celery_single_worker() {
    log_info "Test 4: Celery - Verify single main worker (no duplicates)"

    # Count main celery processes (uv run celery)
    local main_worker_count=$(pgrep -f "uv run celery" | wc -l)

    if [ "$main_worker_count" -eq 0 ]; then
        log_error "No Celery main worker found"
        return 1
    elif [ "$main_worker_count" -gt 1 ]; then
        log_error "Multiple Celery main workers detected ($main_worker_count) - DUPLICATE WORKERS!"
        log_error "PIDs: $(pgrep -f 'uv run celery')"
        return 1
    fi

    # Also count total celery processes (should be > 1 due to prefork pool)
    local total_worker_count=$(pgrep -f "celery.*worker" | wc -l)
    log_info "Celery: Single main worker verified (PID: $(pgrep -f 'uv run celery'))"
    log_info "Celery: Total worker processes: $total_worker_count (includes worker pool)"

    return 0
}

# Test 5: Frontend - Single Instance Check
test_frontend_single_instance() {
    log_info "Test 5: Frontend - Verify single instance running"

    # Count frontend processes (next-server for this project on port 3334)
    local frontend_count=0
    if lsof -i :$FRONTEND_PORT > /dev/null 2>&1; then
        # Get PIDs listening on frontend port (exclude SSH tunnels)
        frontend_count=$(lsof -i :$FRONTEND_PORT -sTCP:LISTEN | grep -v ssh | grep -c "next-server" || echo 0)
    fi

    if [ "$frontend_count" -eq 0 ]; then
        log_warn "No frontend process found - this is OK if frontend is not currently running"
        return 0  # Don't fail - frontend is optional
    elif [ "$frontend_count" -gt 1 ]; then
        log_error "Multiple frontend processes detected ($frontend_count)"
        lsof -i :$FRONTEND_PORT -sTCP:LISTEN | grep -v ssh | grep "next-server"
        return 1
    fi

    local frontend_pid=$(lsof -t -i :$FRONTEND_PORT -sTCP:LISTEN | grep -v "$(pgrep ssh)" | head -1)
    log_info "Frontend: Single instance verified (PID: $frontend_pid)"
    return 0
}

# Test 6: Frontend - Port Binding Check
test_frontend_port_binding() {
    log_info "Test 6: Frontend - Verify port $FRONTEND_PORT is properly bound"

    # Check if port is listening
    if ! lsof -i :$FRONTEND_PORT > /dev/null 2>&1; then
        log_warn "Port $FRONTEND_PORT is not listening - frontend not running"
        return 0  # Don't fail - frontend is optional
    fi

    # Get PID on port (filter out SSH tunnels)
    local port_pid=$(lsof -i :$FRONTEND_PORT -sTCP:LISTEN | grep -v ssh | awk 'NR==2 {print $2}')

    if [ -z "$port_pid" ]; then
        log_warn "No frontend process on port $FRONTEND_PORT (only SSH tunnel or not running)"
        return 0  # Don't fail
    fi

    log_info "Frontend: Port $FRONTEND_PORT correctly bound to PID $port_pid"
    return 0
}

# Test 7: Frontend - Static Chunks Check (500 Error Prevention)
test_frontend_static_chunks() {
    log_info "Test 7: Frontend - Verify static chunks are accessible (no 500 errors)"

    # Skip if frontend not running
    if ! lsof -i :$FRONTEND_PORT > /dev/null 2>&1; then
        log_warn "Frontend not running - skipping static chunks test"
        return 0
    fi

    # Check main page
    local main_page_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$FRONTEND_PORT/")
    if [ "$main_page_code" != "200" ]; then
        log_error "Main page returned HTTP $main_page_code (expected 200)"
        return 1
    fi

    # Check webpack chunk (common static file)
    local webpack_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$FRONTEND_PORT/_next/static/chunks/webpack.js")
    if [ "$webpack_code" = "404" ] || [ "$webpack_code" = "500" ]; then
        log_error "Static webpack chunk returned HTTP $webpack_code (expected 200)"
        log_error "This indicates stale .next build - rebuild required"
        return 1
    fi

    log_info "Frontend: Main page (HTTP $main_page_code) and static chunks OK"
    return 0
}

# Test 8: Port Conflict Detection
test_port_conflicts() {
    log_info "Test 8: Port Conflict Detection - Verify no unexpected processes on ports"

    local conflicts_found=0

    # Check backend port
    local backend_proc=$(lsof -i :$BACKEND_PORT -sTCP:LISTEN -t 2>/dev/null)
    if [ -n "$backend_proc" ]; then
        local backend_cmd=$(ps -p "$backend_proc" -o comm=)
        if [[ ! "$backend_cmd" =~ (uvicorn|python) ]]; then
            log_error "Unexpected process on backend port $BACKEND_PORT: $backend_cmd (PID: $backend_proc)"
            conflicts_found=1
        fi
    fi

    # Check frontend port
    local frontend_proc=$(lsof -i :$FRONTEND_PORT -sTCP:LISTEN -t 2>/dev/null)
    if [ -n "$frontend_proc" ]; then
        local frontend_cmd=$(ps -p "$frontend_proc" -o comm=)
        if [[ ! "$frontend_cmd" =~ (node) ]]; then
            log_error "Unexpected process on frontend port $FRONTEND_PORT: $frontend_cmd (PID: $frontend_proc)"
            conflicts_found=1
        fi
    fi

    if [ "$conflicts_found" -eq 0 ]; then
        log_info "Port conflicts: None detected"
        return 0
    else
        return 1
    fi
}

# Test 9: Service Restart Idempotency
test_restart_idempotency() {
    log_info "Test 9: Restart Idempotency - Verify restart scripts can run multiple times safely"

    # Record initial PIDs
    local initial_backend_pid=$(pgrep -f "python.*uvicorn.*$BACKEND_PORT" | head -1)
    local initial_celery_pid=$(pgrep -f "uv run celery" | head -1)

    log_info "Initial PIDs - Backend: $initial_backend_pid, Celery: $initial_celery_pid"

    # Restart backend
    log_info "Running restart-backend.sh..."
    if ! "$SCRIPT_DIR/restart-backend.sh" > /dev/null 2>&1; then
        log_error "Backend restart failed"
        return 1
    fi

    # Verify new backend is running (different PID)
    local new_backend_pid=$(pgrep -f "python.*uvicorn.*$BACKEND_PORT" | head -1)
    if [ -z "$new_backend_pid" ]; then
        log_error "Backend not running after restart"
        return 1
    fi

    if [ "$new_backend_pid" = "$initial_backend_pid" ]; then
        log_error "Backend PID unchanged after restart (old process still running)"
        return 1
    fi

    # Verify only 1 backend process
    local backend_count=$(pgrep -f "python.*uvicorn.*$BACKEND_PORT" | wc -l)
    if [ "$backend_count" -ne 1 ]; then
        log_error "Expected 1 backend process, found $backend_count"
        return 1
    fi

    log_info "Backend restart: Success (old PID: $initial_backend_pid -> new PID: $new_backend_pid)"

    # Restart celery
    log_info "Running restart-celery.sh..."
    if ! "$SCRIPT_DIR/restart-celery.sh" > /dev/null 2>&1; then
        log_error "Celery restart failed"
        return 1
    fi

    # Verify new celery is running (different PID)
    local new_celery_pid=$(pgrep -f "uv run celery" | head -1)
    if [ -z "$new_celery_pid" ]; then
        log_error "Celery not running after restart"
        return 1
    fi

    if [ "$new_celery_pid" = "$initial_celery_pid" ]; then
        log_error "Celery PID unchanged after restart (old process still running)"
        return 1
    fi

    # Verify only 1 main celery worker
    local celery_count=$(pgrep -f "uv run celery" | wc -l)
    if [ "$celery_count" -ne 1 ]; then
        log_error "Expected 1 main Celery worker, found $celery_count"
        return 1
    fi

    log_info "Celery restart: Success (old PID: $initial_celery_pid -> new PID: $new_celery_pid)"
    log_info "Idempotency test: PASSED - Restarts produce clean single instances"

    return 0
}

# Test 10: Process Cleanup Verification
test_process_cleanup() {
    log_info "Test 10: Process Cleanup - Verify no orphaned/zombie processes"

    # Check for zombie processes related to our services
    local zombies=$(ps aux | grep -E "(uvicorn|celery|next)" | grep "<defunct>" | wc -l)
    if [ "$zombies" -gt 0 ]; then
        log_error "Found $zombies zombie processes"
        ps aux | grep -E "(uvicorn|celery|next)" | grep "<defunct>"
        return 1
    fi

    log_info "Process cleanup: No zombie processes detected"
    return 0
}

# Main test execution
main() {
    echo ""
    echo "=========================================="
    echo "  Service Restart Scripts Test Suite"
    echo "=========================================="
    echo ""

    log_info "Starting tests..."
    echo ""

    # Run all tests
    run_test "Backend Single Instance" "test_backend_single_instance"
    run_test "Backend Port Binding" "test_backend_port_binding"
    run_test "Backend Health Check" "test_backend_health"
    run_test "Celery Single Worker" "test_celery_single_worker"
    run_test "Frontend Single Instance" "test_frontend_single_instance"
    run_test "Frontend Port Binding" "test_frontend_port_binding"
    run_test "Frontend Static Chunks" "test_frontend_static_chunks"
    run_test "Port Conflicts" "test_port_conflicts"
    run_test "Restart Idempotency" "test_restart_idempotency"
    run_test "Process Cleanup" "test_process_cleanup"

    # Print results
    echo ""
    echo "=========================================="
    echo "  Test Results"
    echo "=========================================="
    echo ""

    for result in "${TEST_RESULTS[@]}"; do
        echo "$result"
    done

    echo ""
    echo "=========================================="
    echo "  Summary: $((TOTAL_TESTS - FAILED_TESTS))/$TOTAL_TESTS tests passed"
    echo "=========================================="
    echo ""

    if [ "$FAILED_TESTS" -gt 0 ]; then
        log_error "$FAILED_TESTS tests failed"
        exit 1
    else
        log_info "All tests passed!"
        exit 0
    fi
}

# Run tests
main "$@"
