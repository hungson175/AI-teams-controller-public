import { defineConfig, devices } from '@playwright/test'
import dotenv from 'dotenv'

// Load test environment variables from .env.test
// Must be done before config evaluation to make env vars available
dotenv.config({ path: '.env.test' })

/**
 * Playwright Configuration for AI Teams Controller
 *
 * Sprint 4 - Stabilization: E2E tests for critical UI paths
 * - Topbar stability (no WS errors, no flickering)
 * - WebSocket connection (no reconnection loops)
 * - Login flow
 * - File browser
 *
 * Environment Variables Required (set in .env.test):
 * - TEST_EMAIL: Valid user email in backend database
 * - TEST_PASSWORD: Password for test user
 *
 * See e2e/README.md for setup instructions.
 */

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
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3334',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
})
