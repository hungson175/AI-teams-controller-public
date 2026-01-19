# Technical Spec: JWT Token Lifetime Extension

## Overview
Extend login session to 48 hours per user feedback on frequent re-login.

## Current State
| Token | Current | Location |
|-------|---------|----------|
| Access | 15 min | `auth_service.py:27` |
| Refresh | 7 days | `auth_service.py:28` |

Auto-refresh mechanism: FE calls `tryRefreshTokens()` on 401 responses.

## Design Decision

**Recommended: Extend REFRESH token, keep ACCESS short.**

| Token | Before | After | Rationale |
|-------|--------|-------|-----------|
| Access | 15 min | 15 min | Keep short for security |
| Refresh | 7 days | 7 days | Already > 48h, no change needed |

**Root Cause Analysis:** If users experience frequent re-login within 48h, the issue is NOT token lifetime (7-day refresh already covers this). The issue is:
1. Not all API calls may have 401 retry logic
2. Page hard-refresh before access token renewal

**Alternative (if PO insists on simpler fix):** Extend ACCESS token to 48h.
- Trade-off: Compromised token = 48h exposure vs 15min
- Requires test update (current test expects 5-60 min)

## Recommended Fix (Option A - No Security Trade-off)

### Backend Changes
**File:** `backend/app/services/auth_service.py`

No changes needed. Current 7-day refresh > 48h requirement.

### Frontend Verification
Verify all API services have 401 retry pattern like `teamApi.ts:76-86`.

Check files:
- `lib/services/teamApi.ts` ✓ (has retry)
- `lib/api/templates.ts`
- `contexts/AuthContext.tsx`
- Other API call sites

## Alternative Fix (Option B - If PO Prefers Simplicity)

### Backend Changes
**File:** `backend/app/services/auth_service.py:27`
```python
# Before
ACCESS_TOKEN_EXPIRE_MINUTES = 15
# After
ACCESS_TOKEN_EXPIRE_MINUTES = 2880  # 48 hours
```

### Test Update Required
**File:** `backend/tests/test_auth_service.py:607`
```python
# Before
assert 5 <= ACCESS_TOKEN_EXPIRE_MINUTES <= 60
# After
assert 5 <= ACCESS_TOKEN_EXPIRE_MINUTES <= 2880
```

## Test Cases (TDD)

### If Option B Selected
1. `test_access_token_expiry` - Update constraint to allow 2880
2. `test_access_token_creation` - Verify 48h expiry in payload
3. `test_refresh_still_works` - Ensure refresh mechanism not broken

### Coverage Requirement
**Backend:** 80% minimum (security-critical code)

## Acceptance Criteria
- [ ] Users stay logged in for 48 hours without re-entering credentials
- [ ] All BE JWT tests pass
- [ ] Auto-refresh mechanism continues working
- [ ] No security regressions

## Recommendation to PO

**Ask PO:** Which option preferred?

| Option | Change | Security | Complexity |
|--------|--------|----------|------------|
| A | Verify FE 401 handling | No trade-off | Medium (audit) |
| B | Extend access to 48h | Lower (48h exposure) | Low (2 lines) |

If users are inactive for 48h+ and expect to stay logged in, Option B is simpler.
If security is priority, Option A with FE audit is better.
