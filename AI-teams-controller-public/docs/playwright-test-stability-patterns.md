# Playwright Test Stability Patterns - E2E Test Best Practices

**Date:** 2026-01-11
**Context:** Sprint 4 Stabilization - Fixing brittle E2E tests with timing issues
**Reference:** TECH_SPEC Section 1.2-1.5, TEAM_PLAYBOOK code-00008

---

## Executive Summary

The current Playwright E2E tests have **brittle timing issues** that cause flaky test failures:

1. **Arbitrary timeouts** (`waitForTimeout(2000)`) instead of deterministic waits
2. **No waits for async operations** (file tree loading, API responses)
3. **Fragile selectors** using `innerHTML` comparison instead of stable data attributes
4. **Assumption-based testing** without verifying actual state changes

This document provides actionable patterns to fix these issues based on Playwright best practices and lessons learned from the P0 incident (2026-01-11).

---

## Problem Analysis

### Current Issues in Tests

| File | Line | Issue | Impact |
|------|------|-------|--------|
| `login-flow.spec.ts` | 80 | `waitForTimeout(2000)` after login | Fails on slow networks, wastes time on fast ones |
| `login-flow.spec.ts` | 105 | `waitForTimeout(2000)` after error | Same as above |
| `file-browser.spec.ts` | 35 | `waitForTimeout(2000)` for tree load | Flaky - tree may not be loaded yet |
| `file-browser.spec.ts` | 51,72,107 | Multiple `waitForTimeout` | Multiple race conditions |
| `topbar-stability.spec.ts` | 66 | `innerHTML` comparison | Brittle - any whitespace/comment change breaks test |
| `websocket-connection.spec.ts` | 36 | `waitForTimeout(15000)` | Extremely long, blocks CI pipeline |

### Why This Matters (from TEAM_PLAYBOOK)

> **[code-00008]** For UI rendering bugs (flickering, layout shifts), unit tests are INSUFFICIENT. Must use real browser testing (Playwright/Cypress) with actual login to verify fix works. Mocked tests can't catch render cycle issues.

Playwright tests are our **last line of defense** against production bugs. Brittle tests = false confidence.

---

## Pattern 1: Replace `waitForTimeout` with Deterministic Waits

### Anti-Pattern: Arbitrary Timeouts

```typescript
// ❌ BAD - Brittle, slow, race-prone
await page.click('button[type="submit"]')
await page.waitForTimeout(2000)  // Hope 2s is enough!
const url = page.url()
expect(url).not.toContain('/login')
```

**Problems:**
- Too short → test fails on slow networks/CI
- Too long → wastes 2 seconds even when ready in 100ms
- No guarantee state is actually ready after timeout

### Pattern 1A: Wait for URL Changes

```typescript
// ✅ GOOD - Deterministic, fast, reliable
await page.click('button[type="submit"]')
await page.waitForURL('/') // Waits until navigation completes
const url = page.url()
expect(url).toBe('/')
```

**Why it works:**
- Returns immediately when navigation completes
- Fails fast if navigation doesn't happen (default 30s timeout)
- Works consistently across slow/fast environments

### Pattern 1B: Wait for Specific Elements

```typescript
// ❌ BAD
await page.click('button:has-text("Browse")')
await page.waitForTimeout(2000)
const hasFolderIcons = await page.locator('svg').count() > 0

// ✅ GOOD - Wait for specific element that indicates "ready"
await page.click('button:has-text("Browse")')
await page.waitForSelector('[data-testid="file-tree"]', { state: 'visible' })
await expect(page.locator('[data-testid="file-tree"]')).toBeVisible()
```

### Pattern 1C: Wait for Network Responses

```typescript
// ❌ BAD
await page.click('button[type="submit"]')
await page.waitForTimeout(2000)  // Hope login API finished

// ✅ GOOD - Wait for actual API response
await Promise.all([
  page.waitForResponse(resp =>
    resp.url().includes('/api/auth/login') && resp.status() === 200
  ),
  page.click('button[type="submit"]')
])
await page.waitForURL('/')
```

---

## Pattern 2: Use Stable Selectors with `data-testid`

### Anti-Pattern: Fragile Selectors

```typescript
// ❌ BAD - Breaks on any HTML structure change
const initialIconHTML = await header.innerHTML()
for (let i = 0; i < 10; i++) {
  const currentHTML = await header.innerHTML()
  if (currentHTML !== initialIconHTML) {
    iconChangeCount++
  }
}
```

**Problems:**
- `innerHTML` includes whitespace, comments, all child elements
- Legitimate changes (add tooltip, change class) break test
- Doesn't test what we care about (WiFi icon stability)

### Pattern 2A: Test Specific Element with data-testid

```typescript
// ✅ GOOD - Stable, semantic, focused
// In component: <Wifi className="..." data-testid="wifi-icon" />

const wifiIcon = page.locator('[data-testid="wifi-icon"]')
await expect(wifiIcon).toBeVisible()

// Monitor state changes via CSS class (semantic indicator)
const initialState = await wifiIcon.getAttribute('data-connection-state')
await page.waitForTimeout(10000)  // Acceptable for monitoring test
const finalState = await wifiIcon.getAttribute('data-connection-state')

expect(finalState).toBe(initialState)  // Should remain stable
```

### Pattern 2B: Add data-testid to Components

Update React components to include test IDs:

```tsx
// frontend/components/file-browser/FileTree.tsx
export function FileTree({ ... }) {
  return (
    <div data-testid="file-tree" className="...">
      {/* tree content */}
    </div>
  )
}

// frontend/components/ConnectionStatus.tsx (hypothetical)
export function ConnectionStatus({ status }: { status: WSStatus }) {
  return (
    <div data-testid="connection-status" data-status={status}>
      {status === 'connected' && <Wifi data-testid="wifi-icon" />}
      {status === 'disconnected' && <WifiOff data-testid="wifi-off-icon" />}
    </div>
  )
}
```

**Benefits:**
- Test IDs are stable across refactors
- Semantic meaning clear to future maintainers
- Easy to query in tests: `page.locator('[data-testid="wifi-icon"]')`

---

## Pattern 3: Wait for Loading States to Complete

### Anti-Pattern: Assume Instant Loading

```typescript
// ❌ BAD - Assumes tree loads instantly
await page.click('button:has-text("Browse")')
const docsDir = page.locator('text=docs').first()
await docsDir.click()  // May fail if tree still loading!
```

### Pattern 3A: Wait for Loading Indicator to Disappear

```typescript
// ✅ GOOD - Wait for loading to finish
await page.click('button:has-text("Browse")')

// Wait for loading spinner to disappear
await page.waitForSelector('[data-testid="file-tree-loading"]', {
  state: 'hidden',
  timeout: 10000
})

// OR wait for tree content to appear
await page.waitForSelector('[data-testid="file-tree-item"]', {
  state: 'visible'
})

// Now safe to interact
const docsDir = page.locator('[data-testid="file-tree-item"]:has-text("docs")')
await docsDir.click()
```

### Pattern 3B: Chain Waits for Multi-Step Operations

```typescript
// ✅ GOOD - Explicit wait at each async boundary
test('should navigate directories', async ({ page }) => {
  // 1. Login (async)
  await page.goto('/login')
  await page.fill('#login-email', process.env.TEST_EMAIL!)
  await page.fill('#login-password', process.env.TEST_PASSWORD!)
  await page.click('button[type="submit"]')
  await page.waitForURL('/')  // Wait for navigation

  // 2. Switch to Browse tab (may trigger API call)
  await page.click('button:has-text("Browse")')
  await page.waitForSelector('[data-testid="file-tree"]', { state: 'visible' })

  // 3. Expand directory (async operation)
  const docsDir = page.locator('[data-testid="file-tree-item"]:has-text("docs")')
  await docsDir.click()

  // Wait for subdirectory to appear (not instant!)
  await page.waitForSelector('[data-testid="file-tree-item"]:has-text("tmux")', {
    state: 'visible',
    timeout: 5000
  })

  // 4. Now verify
  await expect(page.locator('[data-testid="file-tree"]')).toContainText('tmux')
})
```

---

## Pattern 4: Use Auto-Waiting Assertions

### Playwright Built-in Auto-Retry

Most `expect` assertions **automatically retry** until timeout:

```typescript
// ✅ These automatically retry for up to 5 seconds (default)
await expect(page.locator('header')).toBeVisible()
await expect(page.locator('[data-testid="file-tree"]')).toContainText('docs')
await expect(page).toHaveURL('/')

// ❌ These do NOT auto-retry (manual checks)
const isVisible = await page.locator('header').isVisible()
expect(isVisible).toBe(true)  // Checked only once!
```

**Use auto-waiting assertions whenever possible** - they eliminate race conditions.

---

## Pattern 5: Handle Login in beforeEach Correctly

### Current Implementation (Acceptable but Improvable)

```typescript
test.beforeEach(async ({ page }) => {
  await page.goto('/login')
  await page.fill('#login-email', process.env.TEST_EMAIL!)
  await page.fill('#login-password', process.env.TEST_PASSWORD!)
  await page.click('button[type="submit"]')
  await page.waitForURL('/')  // ✅ GOOD - Deterministic wait
})
```

### Best Practice: Verify Login Success

```typescript
test.beforeEach(async ({ page }) => {
  await page.goto('/login')

  // Fill credentials
  await page.fill('#login-email', process.env.TEST_EMAIL!)
  await page.fill('#login-password', process.env.TEST_PASSWORD!)

  // Submit and wait for navigation
  await Promise.all([
    page.waitForURL('/'),
    page.click('button[type="submit"]')
  ])

  // Verify login success (header visible = authenticated)
  await expect(page.locator('header')).toBeVisible()
})
```

---

## Actionable Fixes for Current Tests

### Fix 1: login-flow.spec.ts

```typescript
// Line 77-91: Replace waitForTimeout with waitForURL
test('should login with valid credentials', async ({ page }) => {
  await page.goto('/login')
  await page.fill('#login-email', testEmail)
  await page.fill('#login-password', testPassword)

  // ❌ OLD
  // await page.click('button[type="submit"]')
  // await page.waitForTimeout(2000)

  // ✅ NEW
  await page.click('button[type="submit"]')
  await page.waitForURL('/', { timeout: 10000 })  // Wait for redirect

  // Verify login success
  await expect(page.locator('header')).toBeVisible()
})

// Line 102-116: Replace waitForTimeout with error message selector
test('should show error for invalid credentials', async ({ page }) => {
  await page.goto('/login')
  await page.fill('#login-email', 'invalid@test.com')
  await page.fill('#login-password', 'wrongpassword')

  // ❌ OLD
  // await page.click('button[type="submit"]')
  // await page.waitForTimeout(2000)

  // ✅ NEW
  await page.click('button[type="submit"]')

  // Wait for error message to appear OR verify still on login page
  try {
    await page.waitForSelector('.text-destructive', {
      state: 'visible',
      timeout: 5000
    })
  } catch {
    // If no error message, verify we're still on login page
    await expect(page).toHaveURL(/login/)
  }
})
```

### Fix 2: file-browser.spec.ts

```typescript
// Line 29-45: Replace waitForTimeout with selector wait
test('should switch to Browse tab and load file tree', async ({ page }) => {
  // Add data-testid="file-tree" to FileTree.tsx first!

  await page.locator('button:has-text("Browse")').click()

  // ❌ OLD
  // await page.waitForTimeout(2000)

  // ✅ NEW - Wait for tree to be visible
  await page.waitForSelector('[data-testid="file-tree"]', {
    state: 'visible',
    timeout: 10000
  })

  // Verify content loaded
  const fileTree = page.locator('[data-testid="file-tree"]')
  await expect(fileTree).toBeVisible()

  // Check for expected directories
  await expect(fileTree).toContainText('backend')
})

// Line 69-94: Wait for directory expansion
test('should allow directory navigation', async ({ page }) => {
  await page.locator('button:has-text("Browse")').click()
  await page.waitForSelector('[data-testid="file-tree"]', { state: 'visible' })

  const docsDir = page.locator('[data-testid="file-tree-item"]:has-text("docs")').first()

  if (await docsDir.count() > 0) {
    await docsDir.click()

    // ❌ OLD
    // await page.waitForTimeout(1000)

    // ✅ NEW - Wait for subdirectory to appear
    await page.waitForSelector('[data-testid="file-tree-item"]:has-text("tmux")', {
      state: 'visible',
      timeout: 5000
    })

    await expect(page.locator('[data-testid="file-tree"]')).toContainText('tmux')
  }
})
```

### Fix 3: topbar-stability.spec.ts

```typescript
// Line 55-81: Replace innerHTML comparison with data attribute check
test('WiFi icon should remain stable', async ({ page }) => {
  // Add data-testid="wifi-icon" and data-connection-state to component first!

  // ❌ OLD
  // const initialIconHTML = await header.innerHTML()
  // for (let i = 0; i < 10; i++) {
  //   const currentHTML = await header.innerHTML()
  //   if (currentHTML !== initialIconHTML) iconChangeCount++
  // }

  // ✅ NEW
  const wifiIcon = page.locator('[data-testid="wifi-icon"]')
  await expect(wifiIcon).toBeVisible()

  // Get initial connection state
  const initialState = await wifiIcon.getAttribute('data-connection-state')

  // Monitor for 10 seconds
  let stateChanges = 0
  for (let i = 0; i < 10; i++) {
    await page.waitForTimeout(1000)  // Acceptable for monitoring test
    const currentState = await wifiIcon.getAttribute('data-connection-state')
    if (currentState !== initialState && i > 1) {  // Allow initial stabilization
      stateChanges++
    }
  }

  // Should remain stable (allow 1-2 legitimate state changes)
  expect(stateChanges).toBeLessThan(3)
})
```

### Fix 4: Add data-testid to Components

**Files to update:**

1. **frontend/components/file-browser/FileTree.tsx**
```tsx
export function FileTree({ ... }) {
  return (
    <div data-testid="file-tree" className="...">
      {/* tree content */}
    </div>
  )
}
```

2. **frontend/components/file-browser/FileTreeItem.tsx**
```tsx
export function FileTreeItem({ name, type, ... }) {
  return (
    <div
      data-testid="file-tree-item"
      data-item-name={name}
      data-item-type={type}
      className="..."
    >
      {name}
    </div>
  )
}
```

3. **Header/Topbar Component (find the one with WiFi icon)**
```tsx
// Find component that renders connection status
export function ConnectionStatus({ status }: { status: WSStatus }) {
  return (
    <div data-testid="connection-status">
      {status === 'connected' && (
        <Wifi
          data-testid="wifi-icon"
          data-connection-state={status}
          className="..."
        />
      )}
    </div>
  )
}
```

---

## Summary: Test Quality Checklist

Before marking E2E tests as "done", verify:

### ✅ Timing
- [ ] No `waitForTimeout` except for monitoring tests (console error checks)
- [ ] Use `waitForURL` for navigation
- [ ] Use `waitForSelector` for dynamic content
- [ ] Use `waitForResponse` for API calls
- [ ] All waits have explicit timeout (e.g., `{ timeout: 10000 }`)

### ✅ Selectors
- [ ] Use `data-testid` for test-specific queries
- [ ] Avoid `innerHTML` or `outerHTML` comparisons
- [ ] Use semantic attributes (`data-connection-state`, `data-status`)
- [ ] Selectors are specific enough to be unique

### ✅ Assertions
- [ ] Use auto-waiting `expect(...).toBeVisible()` instead of manual checks
- [ ] Verify actual state, not just "no error thrown"
- [ ] Test user-visible behavior, not implementation details

### ✅ Reliability
- [ ] Tests pass 10 times in a row locally
- [ ] Tests pass on slow network (throttle in Chrome DevTools)
- [ ] Tests pass in CI environment
- [ ] No flaky failures due to race conditions

---

## References

- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright Auto-Waiting](https://playwright.dev/docs/actionability)
- TECH_SPEC Section 1.2-1.5 (Sprint 4 Stabilization)
- TEAM_PLAYBOOK [code-00008]: Real browser testing required for UI bugs
- P0 Incident (2026-01-11): Unit tests passed but browser showed bugs

---

## Next Steps

1. **FE**: Add `data-testid` attributes to components:
   - FileTree, FileTreeItem
   - WiFi/connection status icon
   - File tree loading spinner (if exists)

2. **QA**: Update test files with deterministic waits:
   - login-flow.spec.ts (lines 80, 105)
   - file-browser.spec.ts (lines 35, 51, 72, 79, 107)
   - topbar-stability.spec.ts (lines 66-77)

3. **QA**: Run tests 10 times to verify stability:
   ```bash
   cd frontend
   for i in {1..10}; do echo "Run $i"; pnpm playwright test || break; done
   ```

4. **TL**: Review test quality before accepting sprint
