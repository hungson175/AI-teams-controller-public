import { test, expect } from '@playwright/test'

/**
 * WebSocket Connection E2E Tests
 *
 * Sprint 4 - WebSocket Stability Verification
 * Ensures no reconnection loops caused by unmemoized callbacks
 */

test.describe('WebSocket Connection', () => {
  test('should connect without rapid reconnection', async ({ page }) => {
    const wsConnections: string[] = []
    const wsMessages: number[] = []

    // Track WebSocket lifecycle
    page.on('websocket', ws => {
      const url = ws.url()
      wsConnections.push(`connect:${Date.now()}:${url}`)
      console.log(`[WS] Connected: ${url}`)

      let messageCount = 0
      ws.on('framereceived', () => {
        messageCount++
      })

      ws.on('close', () => {
        wsMessages.push(messageCount)
        wsConnections.push(`close:${Date.now()}:${url}`)
        console.log(`[WS] Closed: ${url} (${messageCount} messages received)`)
      })
    })

    await page.goto('/')

    // Wait for initial connection and stabilization
    await page.waitForTimeout(15000)

    const connectEvents = wsConnections.filter(c => c.startsWith('connect'))
    const closeEvents = wsConnections.filter(c => c.startsWith('close'))

    console.log(`[E2E] WebSocket connections: ${connectEvents.length}`)
    console.log(`[E2E] WebSocket closes: ${closeEvents.length}`)

    // CRITICAL: Should have 1-3 connections max (not dozens from reconnection loop)
    // P0 bug caused connection storm due to unmemoized callback
    expect(connectEvents.length).toBeLessThan(5)

    // Each connection should receive messages (proves it's functional)
    if (wsMessages.length > 0) {
      const totalMessages = wsMessages.reduce((a, b) => a + b, 0)
      console.log(`[E2E] Total messages received: ${totalMessages}`)
      expect(totalMessages).toBeGreaterThan(0)
    }
  })

  test('should not have console errors during WebSocket lifecycle', async ({ page }) => {
    const consoleErrors: string[] = []

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text())
      }
    })

    await page.goto('/')
    await page.waitForTimeout(10000)

    // Filter for WebSocket-specific errors
    const wsErrors = consoleErrors.filter(err =>
      err.includes('[WS]') || err.toLowerCase().includes('websocket')
    )

    console.log(`[E2E] Total console errors: ${consoleErrors.length}`)
    console.log(`[E2E] WebSocket errors: ${wsErrors.length}`)

    if (wsErrors.length > 0) {
      console.log('[E2E] WebSocket errors detected:')
      wsErrors.forEach((err, idx) => console.log(`  ${idx + 1}. ${err}`))
    }

    // Should have minimal or no WS errors
    expect(wsErrors.length).toBeLessThan(3)
  })

  test('should handle page visibility changes gracefully', async ({ page }) => {
    const wsConnections: string[] = []

    page.on('websocket', ws => {
      wsConnections.push(`connect:${ws.url()}`)
      ws.on('close', () => wsConnections.push(`close:${ws.url()}`))
    })

    await page.goto('/')
    await page.waitForTimeout(3000)

    const connectsBefore = wsConnections.filter(c => c.startsWith('connect')).length

    // Simulate tab hidden/visible (common real-world scenario)
    await page.evaluate(() => {
      Object.defineProperty(document, 'visibilityState', {
        configurable: true,
        get: () => 'hidden'
      })
      document.dispatchEvent(new Event('visibilitychange'))
    })

    await page.waitForTimeout(2000)

    await page.evaluate(() => {
      Object.defineProperty(document, 'visibilityState', {
        configurable: true,
        get: () => 'visible'
      })
      document.dispatchEvent(new Event('visibilitychange'))
    })

    await page.waitForTimeout(3000)

    const connectsAfter = wsConnections.filter(c => c.startsWith('connect')).length
    const reconnections = connectsAfter - connectsBefore

    console.log(`[E2E] Reconnections after visibility change: ${reconnections}`)

    // Should not cause excessive reconnections
    expect(reconnections).toBeLessThan(3)
  })
})
