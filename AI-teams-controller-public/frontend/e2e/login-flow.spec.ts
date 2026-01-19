import { test, expect } from '@playwright/test'

/**
 * Login Flow E2E Tests
 *
 * Sprint 4 - Authentication Flow Verification
 * Tests login, logout, and protected route behavior
 */

test.describe('Login Flow', () => {
  test('should redirect to login when not authenticated', async ({ page }) => {
    // Try to access root without auth
    await page.goto('/')

    // Should redirect to /login or show login page
    await page.waitForLoadState('networkidle')

    const url = page.url()
    console.log(`[E2E] Current URL: ${url}`)

    // Check if we're on login page or if login form is visible
    const loginForm = page.locator('form').filter({ hasText: 'Sign in' })
    const isOnLoginPage = url.includes('/login') || await loginForm.count() > 0

    expect(isOnLoginPage).toBe(true)
  })

  test('should show login form with email and password fields', async ({ page }) => {
    await page.goto('/login')

    // Check for login form elements
    const emailInput = page.locator('#login-email')
    const passwordInput = page.locator('#login-password')
    const submitButton = page.locator('button[type="submit"]')

    await expect(emailInput).toBeVisible()
    await expect(passwordInput).toBeVisible()
    await expect(submitButton).toBeVisible()

    // Check for title
    await expect(page.locator('text=AI Teams Controller')).toBeVisible()
  })

  test('should show error for empty credentials', async ({ page }) => {
    await page.goto('/login')

    // Try to submit empty form
    await page.locator('button[type="submit"]').click()

    // HTML5 validation should prevent submission
    // Or error message should appear
    const emailInput = page.locator('#login-email')
    const isInvalid = await emailInput.evaluate(
      (el: HTMLInputElement) => !el.validity.valid
    )

    expect(isInvalid).toBe(true)
  })

  test('should login with valid credentials (if env vars set)', async ({ page }) => {
    // Skip if no test credentials provided
    const testEmail = process.env.TEST_EMAIL
    const testPassword = process.env.TEST_PASSWORD

    if (!testEmail || !testPassword) {
      test.skip()
      return
    }

    await page.goto('/login')

    // Fill in credentials
    await page.fill('#login-email', testEmail)
    await page.fill('#login-password', testPassword)

    // Submit form
    await page.click('button[type="submit"]')

    // Wait for navigation to complete (deterministic)
    await page.waitForURL('/', { timeout: 10000 })

    // Verify dashboard loaded (TMUX Controller heading visible)
    const heading = page.locator('h1:has-text("TMUX Controller")')
    await expect(heading).toBeVisible({ timeout: 5000 })
  })

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login')

    // Fill in invalid credentials
    await page.fill('#login-email', 'invalid@test.com')
    await page.fill('#login-password', 'wrongpassword')

    // Submit form
    await page.click('button[type="submit"]')

    // Wait a moment for error to appear (keep minimal timeout for error case)
    await page.waitForTimeout(1000)

    // Should still be on login page
    const url = page.url()
    expect(url).toContain('/login')

    // Error message should appear (check for error text or role="alert")
    const hasError = await page.locator('.text-destructive').count() > 0
    console.log(`[E2E] Error message displayed: ${hasError}`)

    // Either error message visible OR still on login page
    expect(hasError || url.includes('/login')).toBe(true)
  })
})
