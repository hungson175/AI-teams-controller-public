# E2E Tests - Playwright

Sprint 4 - Stabilization: Critical UI path testing

## Setup

### 1. Install Dependencies

```bash
pnpm add -D @playwright/test
npx playwright install chromium
```

### 2. Configure Test Credentials

**Required:** Create test user in backend database first.

Edit `frontend/.env.test`:

```bash
TEST_EMAIL=test@example.com
TEST_PASSWORD=testpassword123
```

**Backend Requirement:** These credentials must exist in the backend database. Coordinate with BE/PO to create test user account.

### 3. Start Services

Tests expect services running on:
- Frontend: http://localhost:3334
- Backend: http://localhost:17061

Start with: `./scripts/restart-all.sh`

## Running Tests

```bash
cd frontend

# List all tests
pnpm playwright test --list

# Run all tests
pnpm playwright test

# Run specific test file
pnpm playwright test topbar-stability

# Run with UI
pnpm playwright test --ui

# Generate HTML report
pnpm playwright show-report
```

## Test Files

| File | Tests | Purpose |
|------|-------|---------|
| `topbar-stability.spec.ts` | 3 | Verify no WS errors, no flickering |
| `websocket-connection.spec.ts` | 3 | No reconnection loops, stable WS |
| `login-flow.spec.ts` | 5 | Auth flow, error handling |
| `file-browser.spec.ts` | 5 | File tree loading, navigation |

**Total:** 16 E2E tests

## Test Status

✅ **9/16 PASS** (without auth credentials)
- Login flow tests: 5/5
- WS connection tests: 2/2
- WS error flooding: 1/1
- 1 other

⏳ **6 BLOCKED** (need auth credentials)
- File browser tests: 5
- WiFi icon stability: 1

🔄 **1 SKIP** (optional, requires env vars)

## Troubleshooting

**Tests fail with "stuck on login":**
- Verify TEST_EMAIL and TEST_PASSWORD are set in `.env.test`
- Verify test user exists in backend database
- Check backend is running on port 17061

**WebSocket errors:**
- Check backend WebSocket endpoint is accessible
- Verify no proxy/firewall blocking WS connections

**Timeout errors:**
- Increase timeout in playwright.config.ts
- Check service startup is complete before running tests
