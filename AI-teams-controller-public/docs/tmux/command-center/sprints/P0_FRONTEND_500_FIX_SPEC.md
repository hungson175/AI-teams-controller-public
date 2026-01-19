# P0 Technical Spec: Frontend 500 Errors Permanent Fix

**Author:** TL
**Date:** 2026-01-10
**Priority:** P0 (Boss escalation - recurring issue)
**Size:** M (script updates + verification)

---

## Problem Statement

Frontend repeatedly serves 500 errors on static chunks (`/_next/static/chunks/*.js`) after rebuilds, despite using `rm -rf .next`. Boss extremely frustrated - wants PERMANENT fix.

---

## Root Cause Analysis

### 1. Next.js Bug #78756 (CONFIRMED)

**Issue:** Webpack uses `[chunkhash]` instead of `[contenthash]` for filename hashing.

- `[chunkhash]` = hash of complete chunk (JS + CSS + WASM)
- `[contenthash]` = hash of file content only

**Effect:** When content changes, hash may NOT change, causing:
- Browsers serve cached stale files
- New HTML references same chunk hash
- Chunk content changed but filename didn't
- **500 error** when browser serves cached old version

**Status:** Fixed in Next.js canary (PR #80153), not in stable v16.0.7

**Sources:**
- [GitHub Issue #78756](https://github.com/vercel/next.js/issues/78756)
- [GitHub Discussion #82651](https://github.com/vercel/next.js/discussions/82651)

### 2. Aggressive Cache Headers

```
Cache-Control: public, max-age=31536000, immutable
```

- 31536000 seconds = **1 year**
- `immutable` = browser NEVER revalidates
- If hash doesn't change, cached version served forever

### 3. Systemd Race Condition

Current flow:
```
systemctl --user stop → (5s RestartSec) → rebuild → systemctl --user start
```

**Race:** Systemd `Restart=always` may restart old build if rebuild is slow.

### 4. Incomplete Verification

Current restart script only verifies:
- Main page returns HTTP 200

**Missing verification:**
- Specific chunk files exist
- Chunk hashes match build manifest
- BUILD_ID consistency

---

## Solution Architecture

### Phase 1: Robust Restart Script (Immediate)

Update `scripts/restart-frontend.sh`:

```bash
#!/bin/bash
# Restart Frontend (Next.js) - P0 Fix Version
set -e
source "$(dirname "$0")/lib/common.sh"

PORT=3334
SERVICE_NAME="ai-teams-frontend"
LOG_FILE="/tmp/ai-teams-frontend.log"
PROJECT_DIR="$(dirname "$0")/../frontend"

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
pnpm build >> "$LOG_FILE" 2>&1

# Step 6: Verify build artifacts exist
if [ ! -f "$PROJECT_DIR/.next/BUILD_ID" ]; then
    log_error "Build failed: BUILD_ID not found"
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
```

### Phase 2: Health Endpoint Enhancement (Short-term)

Add BUILD_ID to health check for verification:

**File:** `frontend/app/api/health/route.ts`

```typescript
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    buildId: process.env.NEXT_PUBLIC_BUILD_VERSION || 'unknown',
    timestamp: new Date().toISOString(),
  })
}
```

### Phase 3: Next.js Upgrade (Long-term)

When Next.js 16.1 stable releases (includes PR #80153):

```bash
cd frontend
pnpm update next@^16.1.0
```

---

## Verification Checklist

After restart, verify ALL:

1. [ ] Main page loads: `curl http://localhost:3334/`
2. [ ] Webpack chunk accessible: `curl http://localhost:3334/_next/static/chunks/webpack-*.js`
3. [ ] BUILD_ID matches: Compare `.next/BUILD_ID` with browser console
4. [ ] No 500 errors in log: `tail /tmp/ai-teams-frontend.log`

---

## Test Cases

1. **Clean restart**: Run script → verify all chunks accessible
2. **Rapid restart**: Run script twice quickly → no race condition
3. **Code change**: Modify file → restart → verify new content served
4. **Browser cache**: Clear cache → reload → verify correct version

---

## Acceptance Criteria

- [ ] Restart script verifies .next deletion
- [ ] Restart script verifies chunk files generated
- [ ] Restart script verifies chunks accessible via HTTP
- [ ] No more 500 errors on static chunks after restart
- [ ] BUILD_ID visible for debugging
- [ ] Systemd race condition eliminated (disable/enable pattern)

---

## Implementation Order

1. Update `scripts/restart-frontend.sh` with verification steps
2. Test on dev environment
3. Update CLAUDE.md with new verification requirements
4. Document in WHITEBOARD when complete

---

## References

- [Next.js Issue #78756](https://github.com/vercel/next.js/issues/78756) - Stale chunk hash bug
- [Next.js PR #80153](https://github.com/vercel/next.js/pull/80153) - Fix merged to canary
- [Webpack Caching Guide](https://webpack.js.org/guides/caching/) - contenthash best practices
- Memory: Frontend Production Builds Require Explicit Rebuild
- Memory: Next.js 16.0.7 Turbopack Missing Chunk Bug
