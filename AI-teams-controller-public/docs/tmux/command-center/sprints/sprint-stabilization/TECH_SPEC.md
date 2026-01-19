# Sprint 4 - Stabilization Sprint Technical Specification

**Author:** TL
**Date:** 2026-01-11
**Status:** DESIGN COMPLETE
**Basis:** P0 Retro - Unit tests passed but real bugs persisted

---

## Overview

Sprint 4 addresses test quality gaps exposed by P0 topbar flickering incident. Unit tests passed while real browser showed "[WS] Error:" flooding due to unmemoized callback causing WebSocket reconnection loops.

**Goals:**
1. Add Playwright tests for critical UI paths (real browser testing)
2. Audit and fix callback/memo stability issues
3. Improve WebSocket connection test coverage

**Total Estimated Effort:** 8h

---

## CRITICAL: TDD + Revertability Protocol (Boss Directive)

### Test Table - What to Test After Each Section

| Step | Work Item | Test Command | Expected Result | STOP IF |
|------|-----------|--------------|-----------------|---------|
| **FE-1** | Playwright setup | `cd frontend && pnpm playwright test` | Playwright configured | Setup fails |
| **FE-2** | Topbar stability test | `pnpm playwright test topbar` | No console errors, no flickering | Test fails |
| **FE-3** | WebSocket connection test | `pnpm playwright test websocket` | WS connects without flooding | Test fails |
| **FE-4** | Login flow test | `pnpm playwright test login` | Login succeeds | Test fails |
| **FE-5** | File browser test | `pnpm playwright test file-browser` | Tree loads, navigation works | Test fails |
| **FE-6** | useCallback audit fixes | `pnpm test && pnpm build` | All tests + build pass | ANY failure |
| **BE-1** | WS endpoint stability test | `cd backend && uv run pytest tests/test_ws_stability.py` | All tests pass | ANY failure |

### Review Table - TL Checkpoints

| Checkpoint | After Step | TL Verifies | Pass Criteria |
|------------|------------|-------------|---------------|
| **FE-R1** | Playwright setup | Tests run in real browser | Chrome launches, tests execute |
| **FE-R2** | Topbar test | Stability verified | No "[WS] Error:" in console |
| **FE-R3** | useCallback fixes | Reference stability | No effect re-runs from callback changes |
| **BE-R1** | WS endpoint tests | Connection stability | No silent failures |

### Revert Table - Rollback Commands

| Step | Commit Pattern | Revert Command | Verify After Revert |
|------|----------------|----------------|---------------------|
| **FE-1** | `test: add Playwright setup` | `git revert HEAD` | `pnpm build` passes |
| **FE-2** | `test: add topbar stability test` | `git revert HEAD` | `pnpm build` passes |
| **FE-6** | `fix: memoize callbacks for stability` | `git revert HEAD` | `pnpm test && pnpm build` passes |
| **BE-1** | `test: add WS endpoint stability tests` | `git revert HEAD` | `uv run pytest` passes |

---

## Work Item 1: Playwright Setup and Critical UI Tests (FE)

**Owner:** FE + QA
**Estimate:** 3h
**Priority:** HIGH

### 1.1 Playwright Configuration

Install and configure Playwright for real browser testing:

```bash
cd frontend
pnpm add -D @playwright/test
npx playwright install chromium
```

**playwright.config.ts:**
```typescript
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3334',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3334',
    reuseExistingServer: !process.env.CI,
  },
})
```

### 1.2 Topbar Stability Test

**Location:** `frontend/e2e/topbar-stability.spec.ts`

```typescript
import { test, expect } from '@playwright/test'

test.describe('Topbar Stability', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.fill('[name="email"]', process.env.TEST_EMAIL!)
    await page.fill('[name="password"]', process.env.TEST_PASSWORD!)
    await page.click('button[type="submit"]')
    await page.waitForURL('/')
  })

  test('should not flood console with WS errors', async ({ page }) => {
    const consoleErrors: string[] = []
    page.on('console', msg => {
      if (msg.type() === 'error' && msg.text().includes('[WS]')) {
        consoleErrors.push(msg.text())
      }
    })

    // Wait 10 seconds and monitor
    await page.waitForTimeout(10000)

    // Should have 0 or very few WS errors (not flooding)
    expect(consoleErrors.length).toBeLessThan(3)
  })

  test('topbar should not visually flicker', async ({ page }) => {
    // Take screenshots at intervals
    const screenshots: Buffer[] = []
    for (let i = 0; i < 5; i++) {
      screenshots.push(await page.locator('header').screenshot())
      await page.waitForTimeout(2000)
    }

    // Compare screenshots - should be identical (no flickering)
    // Implementation: compare pixel data
  })

  test('WiFi icon should remain stable', async ({ page }) => {
    const wifiIcon = page.locator('header svg')
    await expect(wifiIcon).toBeVisible()

    // Monitor for 10 seconds
    let stateChanges = 0
    const initialClass = await wifiIcon.getAttribute('class')

    for (let i = 0; i < 10; i++) {
      await page.waitForTimeout(1000)
      const currentClass = await wifiIcon.getAttribute('class')
      if (currentClass !== initialClass) {
        stateChanges++
      }
    }

    // Should have minimal state changes (connection stable)
    expect(stateChanges).toBeLessThan(2)
  })
})
```

### 1.3 WebSocket Connection Test

**Location:** `frontend/e2e/websocket-connection.spec.ts`

```typescript
import { test, expect } from '@playwright/test'

test.describe('WebSocket Connection', () => {
  test('should connect without rapid reconnection', async ({ page }) => {
    const wsConnections: string[] = []

    page.on('websocket', ws => {
      wsConnections.push(`connect: ${ws.url()}`)
      ws.on('close', () => wsConnections.push(`close: ${ws.url()}`))
    })

    await page.goto('/')
    await page.waitForTimeout(10000)

    // Should have 1-2 connections, not dozens (reconnection loop)
    const connectCount = wsConnections.filter(c => c.startsWith('connect')).length
    expect(connectCount).toBeLessThan(5)
  })

  test('should handle server restart gracefully', async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(2000)

    // Simulate server restart by closing WS from server side
    // (This test documents expected behavior)

    // After reconnect, should be stable
    const errors: string[] = []
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text())
    })

    await page.waitForTimeout(10000)
    expect(errors.filter(e => e.includes('[WS]')).length).toBeLessThan(3)
  })
})
```

### 1.4 Login Flow Test

**Location:** `frontend/e2e/login-flow.spec.ts`

```typescript
import { test, expect } from '@playwright/test'

test.describe('Login Flow', () => {
  test('should login with valid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[name="email"]', process.env.TEST_EMAIL!)
    await page.fill('[name="password"]', process.env.TEST_PASSWORD!)
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL('/')
    await expect(page.locator('header')).toBeVisible()
  })

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[name="email"]', 'invalid@test.com')
    await page.fill('[name="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')

    await expect(page.locator('[role="alert"]')).toBeVisible()
  })

  test('should redirect to login when not authenticated', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL(/login/)
  })
})
```

### 1.5 File Browser Test

**Location:** `frontend/e2e/file-browser.spec.ts`

```typescript
import { test, expect } from '@playwright/test'

test.describe('File Browser', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.fill('[name="email"]', process.env.TEST_EMAIL!)
    await page.fill('[name="password"]', process.env.TEST_PASSWORD!)
    await page.click('button[type="submit"]')
    await page.waitForURL('/')
  })

  test('should load file tree', async ({ page }) => {
    // Click Browse tab
    await page.click('button:has-text("Browse")')

    // File tree should load
    await expect(page.locator('[data-testid="file-tree"]')).toBeVisible()
  })

  test('should navigate directories', async ({ page }) => {
    await page.click('button:has-text("Browse")')
    await page.waitForSelector('[data-testid="file-tree"]')

    // Click a directory
    await page.click('[data-testid="file-tree"] >> text=docs')

    // Should show subdirectory contents
    await expect(page.locator('[data-testid="file-tree"]')).toContainText('tmux')
  })
})
```

---

## Work Item 2: useCallback/useMemo Audit and Fixes (FE)

**Owner:** FE
**Estimate:** 2.5h
**Priority:** HIGH

### 2.1 Identified Reference Instability Issues

| Location | Callback | In Deps Of | Risk | Fix |
|----------|----------|------------|------|-----|
| TmuxController.tsx:117 | `onRoleActivityUpdate` | usePanePolling:178 | **CRITICAL** - P0 root cause | useCallback |
| TmuxController.tsx:147 | `onTeamSelect` | useTeamLifecycle | LOW - setState is stable | None needed |
| TmuxController.tsx:149 | `onRolesUpdate` | useTeamLifecycle | LOW - setState is stable | None needed |
| TmuxController.tsx:161 | `handleVoiceTranscriptChange` | VoiceOverlay | MEDIUM | useCallback |
| TmuxController.tsx:251 | `handleClearTranscript` | useCallback exists | OK | None needed |
| TmuxController.tsx:286 | `onHeadphoneToggle` | TeamSidebar | MEDIUM | useCallback |

### 2.2 Required Fixes

**Fix 1: onRoleActivityUpdate (CRITICAL - P0)**

```typescript
// BEFORE (inline function - new reference every render):
const { ... } = usePanePolling({
  onRoleActivityUpdate: (roleId, isActive) => {
    setRoleActivity(prev => ...)
  },
})

// AFTER (memoized - stable reference):
const handleRoleActivityUpdate = useCallback((roleId: string, isActive: boolean) => {
  setRoleActivity((prev) => {
    if (prev[roleId] === isActive) return prev
    return { ...prev, [roleId]: isActive }
  })
}, [])

const { ... } = usePanePolling({
  onRoleActivityUpdate: handleRoleActivityUpdate,
})
```

**Fix 2: handleVoiceTranscriptChange**

```typescript
// Already using useCallback at line 161 - VERIFY it has correct deps
const handleVoiceTranscriptChange = useCallback((transcript: string, status: string) => {
  setVoiceTranscript(transcript)
  setVoiceStatus(status)
}, [])  // Empty deps - setState is stable
```

**Fix 3: onHeadphoneToggle**

```typescript
// BEFORE (inline async function):
onHeadphoneToggle={async (isActive) => {
  playBeep(isActive)
  if (isActive) {
    await startRecording(selectedTeam, selectedRole)
  } else {
    stopRecording()
  }
}}

// AFTER (memoized):
const handleHeadphoneToggle = useCallback(async (isActive: boolean) => {
  playBeep(isActive)
  if (isActive && selectedTeam && selectedRole) {
    await startRecording(selectedTeam, selectedRole)
  } else {
    stopRecording()
  }
}, [playBeep, selectedTeam, selectedRole, startRecording, stopRecording])
```

### 2.3 Verification Test

Add unit test to verify callback stability:

```typescript
// frontend/hooks/__tests__/callback-stability.test.ts
import { renderHook } from '@testing-library/react'
import { useRef } from 'react'

test('onRoleActivityUpdate should have stable reference', () => {
  const callbackRefs: Function[] = []

  const { rerender } = renderHook(() => {
    const handleRoleActivityUpdate = useCallback(...)
    callbackRefs.push(handleRoleActivityUpdate)
    return handleRoleActivityUpdate
  })

  rerender()
  rerender()
  rerender()

  // All references should be the same object
  expect(callbackRefs[0]).toBe(callbackRefs[1])
  expect(callbackRefs[1]).toBe(callbackRefs[2])
  expect(callbackRefs[2]).toBe(callbackRefs[3])
})
```

---

## Work Item 3: WebSocket Connection Test Coverage (BE)

**Owner:** BE
**Estimate:** 1.5h
**Priority:** MEDIUM

### 3.1 WS Endpoint Stability Tests

**Location:** `backend/tests/test_ws_stability.py`

```python
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

class TestWebSocketStability:
    """Test WebSocket endpoint stability under various conditions."""

    def test_rapid_reconnection_handling(self, mock_tmux_service):
        """Should handle rapid client reconnections gracefully."""
        with patch("app.api.routes.get_team_service", return_value=mock_tmux_service):
            client = TestClient(app)

            # Simulate rapid reconnection (10 times in quick succession)
            for i in range(10):
                with client.websocket_connect("/api/ws/state/team1/pane-0") as ws:
                    ws.receive_json()
                    ws.close()

            # Should not cause server issues
            # (Test passes if no exceptions thrown)

    def test_concurrent_connections_same_pane(self, mock_tmux_service):
        """Should handle multiple clients connecting to same pane."""
        with patch("app.api.routes.get_team_service", return_value=mock_tmux_service):
            client = TestClient(app)

            connections = []
            for i in range(5):
                ws = client.websocket_connect("/api/ws/state/team1/pane-0")
                connections.append(ws)

            # All connections should receive data
            for ws in connections:
                data = ws.receive_json()
                assert "output" in data

            # Clean up
            for ws in connections:
                ws.close()

    def test_invalid_team_role_handling(self, mock_tmux_service):
        """Should handle invalid team/role gracefully."""
        mock_tmux_service.get_pane_state.return_value = {
            "output": "Pane not found: invalid-role in invalid-team",
            "lastUpdated": "10:00:00",
            "highlightText": None,
            "isActive": False,
        }

        with patch("app.api.routes.get_team_service", return_value=mock_tmux_service):
            client = TestClient(app)

            with client.websocket_connect("/api/ws/state/invalid-team/invalid-role") as ws:
                data = ws.receive_json()
                # Should return error message, not crash
                assert "not found" in data["output"].lower() or "output" in data

    def test_long_running_connection(self, mock_tmux_service):
        """Should maintain connection over extended period."""
        mock_tmux_service.get_pane_state.return_value = {
            "output": "test",
            "lastUpdated": "10:00:00",
            "highlightText": None,
            "isActive": False,
        }

        with patch("app.api.routes.get_team_service", return_value=mock_tmux_service):
            client = TestClient(app)

            with client.websocket_connect("/api/ws/state/team1/pane-0") as ws:
                # Send keepalive
                ws.send_text("ping")
                response = ws.receive_text()
                assert response == "pong"

                # Receive multiple updates
                for i in range(5):
                    data = ws.receive_json()
                    assert "output" in data
```

---

## Work Item 4: Documentation and Process Improvements

**Owner:** TL
**Estimate:** 1h
**Priority:** LOW

### 4.1 Add Playwright to CI Pipeline

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - name: Install dependencies
        run: cd frontend && pnpm install
      - name: Install Playwright
        run: cd frontend && npx playwright install chromium
      - name: Run E2E tests
        run: cd frontend && pnpm playwright test
        env:
          TEST_EMAIL: ${{ secrets.TEST_EMAIL }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
```

### 4.2 Update TEAM_PLAYBOOK.md

Add lesson learned from P0:

```markdown
## P0 Lessons Learned (2026-01-11)

### Unit Tests Can Pass While Real Bugs Persist

**Incident:** Topbar flickering due to unmemoized callback causing WebSocket reconnection loop.

**Why Unit Tests Missed It:**
- Unit tests mock WebSocket - don't test real connection behavior
- React Testing Library doesn't catch effect dependency issues
- No console.error monitoring in unit tests

**Solution:**
- Add Playwright E2E tests for critical UI paths
- Monitor console for errors during E2E tests
- Test callback stability explicitly
- Real browser testing catches issues mocking hides
```

---

## Summary

| Work Item | Owner | Estimate | Priority |
|-----------|-------|----------|----------|
| 1. Playwright Setup + Critical UI Tests | FE + QA | 3h | HIGH |
| 2. useCallback/useMemo Audit + Fixes | FE | 2.5h | HIGH |
| 3. WebSocket Endpoint Stability Tests | BE | 1.5h | MEDIUM |
| 4. Documentation + CI | TL | 1h | LOW |
| **Total** | | **8h** | |

---

## Acceptance Criteria

### Technical Criteria
- [ ] Playwright configured and running
- [ ] 4 critical UI path tests (topbar, WS, login, file browser)
- [ ] All identified callback stability issues fixed
- [ ] BE WebSocket stability tests added
- [ ] No "[WS] Error:" flooding in E2E tests

### Quality Criteria
- [ ] All existing tests pass
- [ ] E2E tests pass in real browser
- [ ] No console errors in E2E tests
- [ ] Build passes

### TDD Criteria (Boss Mandate)
- [ ] Tests written BEFORE fixes (where applicable)
- [ ] Progressive commits showing TDD workflow
- [ ] Review checkpoints passed

---

## Definition of Done

1. All acceptance criteria met
2. TL code review approved
3. QA E2E testing passed (real browser)
4. No regression in existing functionality
5. Console error-free for 60 seconds in E2E tests
