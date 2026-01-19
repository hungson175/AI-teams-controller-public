import { test, expect } from '@playwright/test'

/**
 * Topbar Stability E2E Tests
 *
 * Sprint 4 - Critical UI Path Testing
 * Verifies P0 fix: No WebSocket errors flooding, no topbar flickering
 */

test.describe('Topbar Stability', () => {
  test.beforeEach(async ({ page }) => {
    // Login first (per TECH_SPEC Section 1.2)
    await page.goto('/login')
    await page.fill('#login-email', process.env.TEST_EMAIL!)
    await page.fill('#login-password', process.env.TEST_PASSWORD!)
    await page.click('button[type="submit"]')
    await page.waitForURL('/')
  })

  test('should not flood console with WS errors', async ({ page }) => {
    const consoleErrors: string[] = []
    const wsErrors: string[] = []

    // Capture all console messages
    page.on('console', msg => {
      const text = msg.text()
      if (msg.type() === 'error') {
        consoleErrors.push(text)
        if (text.includes('[WS]')) {
          wsErrors.push(text)
        }
      }
    })

    // Already logged in via beforeEach
    // Wait for initial WebSocket connection
    await page.waitForTimeout(3000)

    // Monitor for 10 seconds (should be stable, no flooding)
    await page.waitForTimeout(10000)

    // CRITICAL: Should have 0 or very few WS errors (not flooding)
    // P0 bug caused dozens of errors - this verifies the fix
    console.log(`[E2E] Total console errors: ${consoleErrors.length}`)
    console.log(`[E2E] WebSocket errors: ${wsErrors.length}`)

    if (wsErrors.length > 0) {
      console.log('[E2E] WS Errors found:')
      wsErrors.forEach((err, idx) => console.log(`  ${idx + 1}. ${err}`))
    }

    expect(wsErrors.length).toBeLessThan(3)
  })

  test('WiFi icon should remain stable', async ({ page }) => {
    // Already logged in via beforeEach
    // Wait for WiFi icon to appear
    const wifiIcon = page.locator('[data-testid="wifi-icon"]')
    await expect(wifiIcon).toBeVisible({ timeout: 5000 })

    // Get initial connection state
    const initialState = await wifiIcon.getAttribute('data-connection-state')
    console.log(`[E2E] Initial WiFi state: ${initialState}`)

    // Monitor for 10 seconds - state should not change excessively
    let stateChangeCount = 0
    let previousState = initialState

    for (let i = 0; i < 10; i++) {
      await page.waitForTimeout(1000)
      const currentState = await wifiIcon.getAttribute('data-connection-state')

      // Track state changes (connected <-> disconnected)
      if (currentState !== previousState && i > 1) {
        stateChangeCount++
        console.log(`[E2E] State changed at ${i}s: ${previousState} -> ${currentState}`)
        previousState = currentState
      }
    }

    // Allow some changes (legitimate reconnection), but not constant flickering
    // P0 bug caused rapid reconnections - this verifies the fix
    expect(stateChangeCount).toBeLessThan(3)
  })

  test('should maintain stable WebSocket connection', async ({ page }) => {
    const wsConnections: string[] = []
    const wsCloseEvents: string[] = []

    // Track WebSocket connections
    page.on('websocket', ws => {
      const url = ws.url()
      wsConnections.push(`connect: ${url}`)
      console.log(`[E2E] WebSocket connected: ${url}`)

      ws.on('close', () => {
        wsCloseEvents.push(`close: ${url}`)
        console.log(`[E2E] WebSocket closed: ${url}`)
      })
    })

    // Already logged in via beforeEach
    // Wait for initial connection
    await page.waitForTimeout(3000)

    // Monitor for 10 seconds
    await page.waitForTimeout(10000)

    console.log(`[E2E] Total WS connections: ${wsConnections.length}`)
    console.log(`[E2E] Total WS closes: ${wsCloseEvents.length}`)

    // Should have 1-2 connections max (voice feedback + pane state)
    // NOT dozens (reconnection loop)
    expect(wsConnections.length).toBeLessThan(5)

    // Close events should be minimal (stable connection)
    expect(wsCloseEvents.length).toBeLessThan(3)
  })
})
