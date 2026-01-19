# E2E Test Fixes - Quick Reference

**Sprint 4 Stabilization** - Replace brittle timing with deterministic waits

---

## Overview

| Test File | Issues | Fixes Needed |
|-----------|--------|--------------|
| login-flow.spec.ts | 2× `waitForTimeout(2000)` | Replace with `waitForURL` and `waitForSelector` |
| file-browser.spec.ts | 5× `waitForTimeout` | Replace with `waitForSelector('[data-testid="file-tree"]')` |
| topbar-stability.spec.ts | `innerHTML` comparison | Use `data-testid` + attribute checks |
| websocket-connection.spec.ts | ✅ Acceptable (monitoring test) | No changes needed |

---

## Part 1: Add data-testid to Components (FE)

### 1.1 FileTree Component

**File:** `/home/hungson175/dev/coding-agents/AI-teams-controller/frontend/components/file-browser/FileTree.tsx`

```tsx
// Find the root div/container and add data-testid
export function FileTree({ ... }) {
  return (
    <div data-testid="file-tree" className="...">
      {/* existing content */}
    </div>
  )
}
```

### 1.2 FileTreeItem Component

**File:** `/home/hungson175/dev/coding-agents/AI-teams-controller/frontend/components/file-browser/FileTreeItem.tsx`

```tsx
export function FileTreeItem({ name, type, ... }) {
  return (
    <div
      data-testid="file-tree-item"
      data-item-name={name}
      data-item-type={type}
      className="..."
    >
      {/* existing content */}
    </div>
  )
}
```

### 1.3 WiFi/Connection Icon Component

**Steps:**
1. Search for WiFi icon component: `grep -r "Wifi" frontend/components --include="*.tsx"`
2. Find component that renders connection status in header
3. Add `data-testid` and `data-connection-state`:

```tsx
// Example structure (adjust to actual component)
export function ConnectionStatus({ status }: { status: 'connected' | 'disconnected' | 'connecting' }) {
  return (
    <div data-testid="connection-status" data-connection-state={status}>
      {status === 'connected' && <Wifi data-testid="wifi-icon" />}
      {status === 'disconnected' && <WifiOff data-testid="wifi-off-icon" />}
    </div>
  )
}
```

---

## Part 2: Fix Test Files (QA)

### 2.1 login-flow.spec.ts

**Change 1: Line 77-91**

```typescript
// BEFORE:
await page.click('button[type="submit"]')
await page.waitForTimeout(2000)
const url = page.url()
expect(url).not.toContain('/login')

// AFTER:
await page.click('button[type="submit"]')
await page.waitForURL('/', { timeout: 10000 })
await expect(page.locator('header')).toBeVisible()
```

**Change 2: Line 102-116**

```typescript
// BEFORE:
await page.click('button[type="submit"]')
await page.waitForTimeout(2000)
const url = page.url()
expect(url).toContain('/login')

// AFTER:
await page.click('button[type="submit"]')

// Wait for error message OR verify still on login page
try {
  await page.waitForSelector('.text-destructive', {
    state: 'visible',
    timeout: 5000
  })
} catch {
  await expect(page).toHaveURL(/login/)
}
```

### 2.2 file-browser.spec.ts

**Change 1: Line 29-45 (switch to Browse tab)**

```typescript
// BEFORE:
await browseTab.click()
await page.waitForTimeout(2000)
const hasFolderIcons = await page.locator('svg').count() > 0

// AFTER:
await browseTab.click()
await page.waitForSelector('[data-testid="file-tree"]', {
  state: 'visible',
  timeout: 10000
})
const fileTree = page.locator('[data-testid="file-tree"]')
await expect(fileTree).toBeVisible()
```

**Change 2: Line 48-66 (show directory structure)**

```typescript
// BEFORE:
await page.locator('button:has-text("Browse")').click()
await page.waitForTimeout(2000)

// AFTER:
await page.locator('button:has-text("Browse")').click()
await page.waitForSelector('[data-testid="file-tree"]', { state: 'visible' })
```

**Change 3: Line 69-94 (directory navigation)**

```typescript
// BEFORE:
await docsDir.click()
await page.waitForTimeout(1000)

// AFTER:
await docsDir.click()
await page.waitForSelector('[data-testid="file-tree-item"]:has-text("tmux")', {
  state: 'visible',
  timeout: 5000
})
```

**Change 4: Line 106-107 (console errors test)**

```typescript
// BEFORE:
await page.locator('button:has-text("Browse")').click()
await page.waitForTimeout(3000)

// AFTER:
await page.locator('button:has-text("Browse")').click()
await page.waitForSelector('[data-testid="file-tree"]', {
  state: 'visible',
  timeout: 10000
})
await page.waitForTimeout(3000)  // Keep this - monitoring console errors
```

### 2.3 topbar-stability.spec.ts

**Change: Line 55-81 (WiFi icon stability)**

```typescript
// BEFORE:
await page.waitForTimeout(2000)
const header = page.locator('header').first()
let iconChangeCount = 0
const initialIconHTML = await header.innerHTML()

for (let i = 0; i < 10; i++) {
  await page.waitForTimeout(1000)
  const currentHTML = await header.innerHTML()
  if (currentHTML !== initialIconHTML && i > 1) {
    iconChangeCount++
  }
}
expect(iconChangeCount).toBeLessThan(5)

// AFTER:
const wifiIcon = page.locator('[data-testid="wifi-icon"]')
await expect(wifiIcon).toBeVisible()

const initialState = await wifiIcon.getAttribute('data-connection-state')

let stateChanges = 0
for (let i = 0; i < 10; i++) {
  await page.waitForTimeout(1000)
  const currentState = await wifiIcon.getAttribute('data-connection-state')
  if (currentState !== initialState && i > 1) {
    stateChanges++
  }
}

expect(stateChanges).toBeLessThan(3)
```

---

## Part 3: Verification (QA)

### 3.1 Test Each File Individually

```bash
cd /home/hungson175/dev/coding-agents/AI-teams-controller/frontend

# Test login flow
pnpm playwright test login-flow.spec.ts

# Test file browser
pnpm playwright test file-browser.spec.ts

# Test topbar stability
pnpm playwright test topbar-stability.spec.ts

# Test WebSocket (should still pass)
pnpm playwright test websocket-connection.spec.ts
```

### 3.2 Run All Tests 10 Times

```bash
cd frontend
for i in {1..10}; do
  echo "========== Run $i/10 =========="
  pnpm playwright test || break
done
```

### 3.3 Test on Slow Network

```bash
# In Chrome DevTools (Playwright browser):
# 1. Open DevTools (F12)
# 2. Network tab → Throttling dropdown
# 3. Select "Fast 3G" or "Slow 3G"
# 4. Run tests again

pnpm playwright test --headed  # Opens visible browser
```

---

## Part 4: Acceptance Criteria

### ✅ Before Marking Complete

- [ ] All 4 test files pass
- [ ] Tests pass 10 times in a row
- [ ] Tests pass with network throttling (Fast 3G)
- [ ] No `waitForTimeout` except in monitoring tests
- [ ] All components have `data-testid` attributes
- [ ] WiFi icon test uses semantic attributes (not innerHTML)

### ✅ Commands That Must Pass

```bash
cd frontend

# All tests pass
pnpm playwright test

# Build succeeds
pnpm build

# No TypeScript errors
pnpm typecheck
```

---

## Troubleshooting

### Issue: "data-testid not found"

**Cause:** Component not updated yet or test running before page loads

**Fix:**
1. Verify component has `data-testid` attribute
2. Add longer timeout: `{ timeout: 10000 }`
3. Check element is actually rendered (not hidden by CSS)

### Issue: "waitForSelector timeout"

**Cause:** Element never appears (bug) or selector is wrong

**Debug:**
```typescript
// Check what's actually on page
await page.screenshot({ path: 'debug.png' })
console.log(await page.content())  // Full HTML
console.log(await page.locator('[data-testid="file-tree"]').count())  // Should be > 0
```

### Issue: "Test passes sometimes, fails other times"

**Cause:** Race condition still exists (need better wait strategy)

**Fix:**
- Check if element appears AFTER an async operation (API call, animation)
- Add `waitForResponse` if triggered by network request
- Increase timeout for slow operations

---

## File Paths Reference

| Component | Path |
|-----------|------|
| FileTree | `/home/hungson175/dev/coding-agents/AI-teams-controller/frontend/components/file-browser/FileTree.tsx` |
| FileTreeItem | `/home/hungson175/dev/coding-agents/AI-teams-controller/frontend/components/file-browser/FileTreeItem.tsx` |
| login-flow test | `/home/hungson175/dev/coding-agents/AI-teams-controller/frontend/e2e/login-flow.spec.ts` |
| file-browser test | `/home/hungson175/dev/coding-agents/AI-teams-controller/frontend/e2e/file-browser.spec.ts` |
| topbar-stability test | `/home/hungson175/dev/coding-agents/AI-teams-controller/frontend/e2e/topbar-stability.spec.ts` |

---

## Estimated Time

| Task | Owner | Time |
|------|-------|------|
| Add data-testid to 3 components | FE | 15 min |
| Fix login-flow.spec.ts | QA | 10 min |
| Fix file-browser.spec.ts | QA | 15 min |
| Fix topbar-stability.spec.ts | QA | 10 min |
| Run verification tests | QA | 20 min |
| **Total** | | **70 min** |

---

## Success Metrics

**Before fixes:**
- Tests fail ~30% of the time on slow network
- `waitForTimeout` wastes 10+ seconds per test run
- innerHTML comparison breaks on whitespace changes

**After fixes:**
- Tests pass 100% of the time (10/10 runs)
- Tests complete 2-3× faster (no arbitrary waits)
- Stable selectors survive refactoring
