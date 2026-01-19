# Sprint 5 - Tech Debt Cleanup Technical Specification

**Author:** TL | **Date:** 2026-01-11 | **Status:** READY FOR REVIEW

---

## Overview

Sprint 5 addresses deferred Playwright test fixes from Sprint 4 (3 of 16 tests had issues) and original tech debt items. Focus: test reliability, repository cleanup.

**Total Estimated Effort:** 6h

---

## Work Item 1: Playwright Test Fixes (FE)

**Owner:** FE | **Estimate:** 2h | **Priority:** HIGH

### 1.1 Login Test Timing (login-flow.spec.ts:79-80)

**Issue:** `waitForTimeout(2000)` is brittle timing.

**Fix:** Replace with proper wait strategies:
- Use `waitForURL('/', { timeout: 5000 })` after login submit
- Use `waitForSelector('header')` to confirm dashboard loaded
- Remove arbitrary `waitForTimeout` calls

### 1.2 File Browser Test Prerequisite (file-browser.spec.ts)

**Issue:** Tests assume file tree loads immediately, may fail on slow networks.

**Fix:**
- Add `waitForSelector('[data-testid="file-tree"]', { timeout: 10000 })`
- Use `waitForResponse` to wait for API call completion
- Add retry logic for directory content checks

### 1.3 WiFi Icon Selector (topbar-stability.spec.ts:55-80)

**Issue:** `header.innerHTML()` comparison is fragile (any header change triggers).

**Fix:**
- Add `data-testid="wifi-status-icon"` to WiFi icon component
- Use `locator('[data-testid="wifi-status-icon"]')` instead of `header.innerHTML()`
- Track icon class changes specifically (connected/disconnected state)

---

## Work Item 2: Repository Cleanup (TL + FE/BE)

**Owner:** TL coord | **Estimate:** 2h | **Priority:** MEDIUM

### 2.1 experiments/ Folder

**Current state:** 668K (7 subdirs: Codex, GLM, TTS, google-tts, hand-free-js-talk, soniox, audio.wav)

**Decision:** Keep or remove based on Boss input. If removing:
```bash
rm -rf experiments/
git add -A && git commit -m "chore: remove experiments folder"
```

### 2.2 Test File Audit

**Current counts:** 39 BE test files, 57 FE test files

**Tasks:**
- Identify duplicate test coverage (same API tested multiple ways)
- Consolidate VoiceFeedbackContext tests (2 files: .test.tsx, .wave2.test.tsx)
- Remove obsolete tests for deleted features

---

## Work Item 3: Context Provider Review (FE)

**Owner:** FE | **Estimate:** 2h | **Priority:** LOW

### 3.1 Current Context Structure (Clean)

```
frontend/contexts/
├── AuthContext.tsx          # Auth state
├── SettingsContext.tsx      # App settings
└── VoiceFeedbackContext.tsx # Voice notifications
```

Wrapped in: `frontend/components/providers/Providers.tsx`

**Assessment:** Structure is clean. No redundancy detected.

**Optional cleanup:**
- Verify each context is used (no dead code)
- Ensure proper memoization in context values
- Add missing `useCallback` for context methods if needed

---

## Summary

| Work Item | Owner | Estimate | Priority |
|-----------|-------|----------|----------|
| 1. Playwright Test Fixes | FE | 2h | HIGH |
| 2. Repository Cleanup | TL coord | 2h | MEDIUM |
| 3. Context Provider Review | FE | 2h | LOW |
| **Total** | | **6h** | |

---

## Acceptance Criteria

- [ ] All 16 E2E tests pass (currently 13/16)
- [ ] No brittle `waitForTimeout` in E2E tests
- [ ] experiments/ folder decision made and executed
- [ ] VoiceFeedbackContext test files consolidated
- [ ] All existing unit tests pass
- [ ] Build passes

---

## Code Coverage Requirements

**Frontend:** 70% minimum | **Backend:** 80% minimum
(Per CODE_COVERAGE_STANDARDS.md)
