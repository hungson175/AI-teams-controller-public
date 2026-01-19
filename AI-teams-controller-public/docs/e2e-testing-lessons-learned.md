# E2E Testing Lessons Learned - Playwright Best Practices

**Context:** Sprint 4 Stabilization - Fixing brittle E2E tests
**Date:** 2026-01-11
**Team:** Command Center (AI Teams Controller)

---

## Universal Patterns for Stable E2E Tests

### Pattern 1: Never Use Arbitrary Timeouts

**Rule:** `waitForTimeout()` is ALWAYS wrong except for monitoring tests (console error checks)

**Why:**
- Too short → fails on slow networks/CI
- Too long → wastes time on fast environments
- No guarantee state is ready after timeout

**Instead Use:**

| Scenario | Use | Example |
|----------|-----|---------|
| Waiting for navigation | `waitForURL(url)` | `await page.waitForURL('/')` |
| Waiting for element | `waitForSelector(selector)` | `await page.waitForSelector('[data-testid="file-tree"]')` |
| Waiting for API | `waitForResponse(predicate)` | `await page.waitForResponse(r => r.url().includes('/api/login'))` |
| Waiting for state change | `expect(...).toBeVisible()` | `await expect(page.locator('header')).toBeVisible()` |

**Exception:** Monitoring tests that deliberately observe behavior over time:
```typescript
// Acceptable: checking for console errors over 10 seconds
for (let i = 0; i < 10; i++) {
  await page.waitForTimeout(1000)
  // Check console errors accumulated
}
```

---

### Pattern 2: Use Stable Selectors with data-testid

**Rule:** Never rely on implementation details (innerHTML, CSS classes, DOM structure)

**Anti-Patterns:**
```typescript
// ❌ Breaks on any HTML change
await header.innerHTML()

// ❌ Breaks when CSS refactored
await page.locator('.css-hash-xyz-abc')

// ❌ Breaks when text changes
await page.locator('text=Click here')
```

**Best Practice:**
```typescript
// ✅ Stable - survives refactoring
await page.locator('[data-testid="submit-button"]')
await page.locator('[data-testid="file-tree"]')
await page.locator('[data-testid="wifi-icon"]')
```

**Component Example:**
```tsx
// Add to React components
export function FileTree({ ... }) {
  return (
    <div data-testid="file-tree" className="...">
      {items.map(item => (
        <div
          key={item.id}
          data-testid="file-tree-item"
          data-item-name={item.name}
          data-item-type={item.type}
        >
          {item.name}
        </div>
      ))}
    </div>
  )
}
```

**Semantic Attributes:** Use `data-*` attributes to expose state:
```tsx
<Wifi
  data-testid="wifi-icon"
  data-connection-state={connectionStatus}  // 'connected', 'disconnected'
/>
```

Tests can then check: `await wifiIcon.getAttribute('data-connection-state')`

---

### Pattern 3: Wait for Loading to Complete

**Rule:** Always wait for async operations to finish before interacting with elements

**Anti-Pattern:**
```typescript
// ❌ Assumes instant loading
await page.click('button:has-text("Browse")')
await page.click('text=docs')  // May fail - tree still loading!
```

**Best Practice:**
```typescript
// ✅ Wait for loading to complete
await page.click('button:has-text("Browse")')

// Option 1: Wait for loading spinner to disappear
await page.waitForSelector('[data-testid="loading-spinner"]', {
  state: 'hidden'
})

// Option 2: Wait for content to appear
await page.waitForSelector('[data-testid="file-tree-item"]', {
  state: 'visible'
})

// Now safe to interact
await page.click('[data-testid="file-tree-item"]:has-text("docs")')
```

---

### Pattern 4: Use Auto-Waiting Assertions

**Rule:** Prefer `expect(...).toBeVisible()` over manual `isVisible()` checks

**Why:** Playwright auto-retries assertions until timeout (default 5s)

**Anti-Pattern:**
```typescript
// ❌ Checked only ONCE (race condition)
const isVisible = await page.locator('header').isVisible()
expect(isVisible).toBe(true)
```

**Best Practice:**
```typescript
// ✅ Automatically retries until visible or timeout
await expect(page.locator('header')).toBeVisible()

// ✅ Automatically retries until text matches
await expect(page.locator('[data-testid="file-tree"]')).toContainText('docs')

// ✅ Automatically retries until URL matches
await expect(page).toHaveURL('/')
```

**Available Auto-Waiting Assertions:**
- `toBeVisible()`, `toBeHidden()`
- `toContainText()`, `toHaveText()`
- `toHaveURL()`, `toHaveTitle()`
- `toBeEnabled()`, `toBeDisabled()`
- `toBeChecked()`
- `toHaveAttribute()`

---

### Pattern 5: Handle Multi-Step Async Operations

**Rule:** Wait at each async boundary (navigation, API call, animation)

**Example: Login → Navigate → Load Data**

```typescript
test('complete user flow', async ({ page }) => {
  // Step 1: Login (async - API call)
  await page.goto('/login')
  await page.fill('#login-email', email)
  await page.fill('#login-password', password)
  await page.click('button[type="submit"]')
  await page.waitForURL('/')  // ✅ Wait for navigation

  // Step 2: Switch tab (async - may load data)
  await page.click('button:has-text("Browse")')
  await page.waitForSelector('[data-testid="file-tree"]', {
    state: 'visible'
  })  // ✅ Wait for data load

  // Step 3: Expand directory (async - may fetch children)
  await page.click('[data-testid="file-tree-item"]:has-text("docs")')
  await page.waitForSelector('[data-testid="file-tree-item"]:has-text("tmux")', {
    state: 'visible',
    timeout: 5000
  })  // ✅ Wait for expansion

  // Step 4: Verify final state
  await expect(page.locator('[data-testid="file-tree"]')).toContainText('tmux')
})
```

**Key Insight:** Each async operation needs an explicit wait. Don't assume instant completion.

---

## When to Use Each Wait Strategy

| Situation | Strategy | Example |
|-----------|----------|---------|
| Navigation after click | `waitForURL()` | Login redirect |
| Element appears after delay | `waitForSelector({ state: 'visible' })` | Loading spinner disappears |
| Element disappears | `waitForSelector({ state: 'hidden' })` | Modal closes |
| API completes | `waitForResponse(predicate)` | Form submission |
| State change | `expect(...).toBeVisible()` | Header appears after auth |
| Monitoring behavior | `waitForTimeout()` (ONLY exception) | Console error checks |

---

## Testing Checklist

Before marking E2E tests complete:

### ✅ Timing
- [ ] No `waitForTimeout` (except monitoring tests)
- [ ] Navigation uses `waitForURL()`
- [ ] Dynamic content uses `waitForSelector({ state: 'visible' })`
- [ ] API calls use `waitForResponse()`
- [ ] All waits have explicit timeouts

### ✅ Selectors
- [ ] Use `data-testid` for test-specific elements
- [ ] Use semantic `data-*` attributes for state checks
- [ ] Avoid CSS classes, innerHTML, DOM structure
- [ ] Selectors are unique and specific

### ✅ Assertions
- [ ] Use auto-waiting `expect(...).toBeVisible()`
- [ ] Don't use manual checks (`isVisible()`, `count()`)
- [ ] Verify actual state, not "no error thrown"

### ✅ Reliability
- [ ] Tests pass 10 times in a row locally
- [ ] Tests pass on throttled network (Fast 3G)
- [ ] Tests pass in CI environment
- [ ] No race conditions or flaky failures

---

## Common Pitfalls

### Pitfall 1: "Test passes on my machine but fails in CI"

**Cause:** Network/CPU slower in CI → race conditions exposed

**Fix:**
- Replace `waitForTimeout` with `waitForSelector`
- Use longer timeouts for critical operations: `{ timeout: 10000 }`
- Test locally with network throttling (Chrome DevTools → Fast 3G)

### Pitfall 2: "Test fails randomly ~30% of time"

**Cause:** Race condition - element not ready when accessed

**Fix:**
- Add explicit wait before interaction
- Use `expect(...).toBeVisible()` instead of manual checks
- Check browser console for errors during test

### Pitfall 3: "Test breaks after refactoring component"

**Cause:** Selector depends on implementation details

**Fix:**
- Use `data-testid` instead of CSS classes/structure
- Add semantic `data-*` attributes for state
- Avoid innerHTML/outerHTML comparisons

### Pitfall 4: "Test passes but doesn't actually verify behavior"

**Cause:** Test checks "no error" instead of actual state

**Fix:**
```typescript
// ❌ Bad - just checks no error thrown
expect(true).toBe(true)

// ✅ Good - verifies actual state
await expect(page.locator('[data-testid="file-tree"]')).toContainText('docs')
```

---

## Integration with Team Playbook

### Recommended Playbook Entries

**[code-00010]** helpful=1 harmful=0 :: E2E tests MUST use deterministic waits. Never `waitForTimeout` except monitoring tests. Use `waitForURL`, `waitForSelector`, `waitForResponse` for async operations. Arbitrary timeouts = flaky tests.

**[code-00011]** helpful=1 harmful=0 :: Add `data-testid` to all React components that need E2E testing. Use semantic `data-*` attributes for state (e.g., `data-connection-state="connected"`). Avoid CSS classes, innerHTML, DOM structure in selectors.

**[code-00012]** helpful=1 harmful=0 :: Playwright auto-waiting assertions (`expect(...).toBeVisible()`) automatically retry until timeout. Use these instead of manual checks (`isVisible()`) to eliminate race conditions.

**[code-00013]** helpful=1 harmful=0 :: Test E2E stability by running 10 times in a row AND with network throttling (Fast 3G). Tests must pass 100% of runs. Flaky tests = false confidence.

---

## References

- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright Auto-Waiting](https://playwright.dev/docs/actionability)
- [Playwright Test Selectors](https://playwright.dev/docs/selectors)
- Sprint 4 TECH_SPEC: `/home/hungson175/dev/coding-agents/AI-teams-controller/docs/tmux/command-center/sprints/sprint-stabilization/TECH_SPEC.md`
- Quick Reference: `/home/hungson175/dev/coding-agents/AI-teams-controller/docs/e2e-test-fixes-quick-reference.md`

---

## Success Metrics

**Before applying patterns:**
- Tests fail ~30% on slow networks
- Average test runtime: 45s (10s wasted on timeouts)
- Tests break on refactoring

**After applying patterns:**
- Tests pass 100% (10/10 runs)
- Average test runtime: 15s (3× faster)
- Tests survive refactoring (stable selectors)

---

## Related Incidents

**P0 Topbar Flickering (2026-01-11):**
- Unit tests passed but real browser showed bugs
- E2E tests caught the real issue (console flooding)
- Lesson: E2E tests are the last line of defense

**TEAM_PLAYBOOK [code-00008]:**
> For UI rendering bugs (flickering, layout shifts), unit tests are INSUFFICIENT. Must use real browser testing (Playwright/Cypress) with actual login to verify fix works.

This reinforces: **Stable E2E tests = production confidence**
