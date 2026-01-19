# Sprint 1 Tech Debt Remediation - Phase 1 Retrospective

**Date:** 2026-01-11 (14:03 - 15:02)
**Facilitator:** SM

---

## Sprint Summary

**Goal:** Split large route files + complete JWT migration
**Outcome:** ✅ PASSED - All acceptance criteria met

| Deliverable | Status |
|-------------|--------|
| file_routes.py → 3 modules | ✅ Complete (46+ tests) |
| voice_routes.py → 3 modules | ✅ Complete (57+ tests) |
| JWT auth migration | ✅ Complete (4 endpoints) |
| Frontend auth standardization | ✅ Complete (4 files) |

---

## Part A: Reflector Phase

### What Went WELL

1. **TDD approach effective** - BE wrote 18 failing tests first, then implemented. Resulted in 103+ passing tests with 80% coverage.

2. **Memory recall identified hidden issues** - FE used coder-memory-recall which identified `getAccessToken()` inconsistency across 4 files (not just 2 originally planned).

3. **QA blackbox testing caught runtime issue** - Code review passed but QA discovered JWT auth wasn't actually working (307 redirect instead of 401). QA testing essential.

4. **Clear TL specs** - TECH_SPEC.md provided unambiguous guidance for BE and FE.

### What Went WRONG

1. **QA blocked by frontend 500 errors** - Frontend cache stale after FE code changes. Required rebuild.
   - Root cause: FE didn't rebuild after committing auth changes
   - Resolution: FE ran restart script
   - Impact: ~3 min delay

2. **JWT auth not working despite code review approval** - Backend running old code (pre-commit e72a29ef).
   - Root cause: Backend process not restarted after JWT migration
   - Resolution: BE restarted backend
   - Impact: ~5 min delay for re-testing

### Issues Identified (3)

| # | Issue | Root Cause | Severity |
|---|-------|------------|----------|
| 1 | Frontend 500 on chunks | Stale .next cache | Medium |
| 2 | JWT returning 307 not 401 | Backend running old code | High |
| 3 | Code review didn't catch runtime issue | Code review is static, not runtime | Low |

### Selected for Action (1)

**Issue #2: Backend not restarted after JWT migration**

This is reinforcement of existing lessons [infra-00001] and [infra-00002]. No new lesson needed, but counters should be incremented.

---

## Part B: Curator Phase

### Bullets Applied This Sprint

| Bullet | Applied | Outcome |
|--------|---------|---------|
| [sprint-00002] TDD first | ✅ BE used TDD | helpful++ |
| [infra-00001] Manual restart required | ❌ Forgot restart | helpful++ (lesson reinforced) |
| [infra-00002] Verify before QA | ❌ Not followed | helpful++ (lesson reinforced) |
| [code-00001] Frontend clean rebuild | ✅ Eventually applied | helpful++ |

### Counter Updates

- [sprint-00002] helpful=8 → helpful=9 (TDD worked well)
- [infra-00001] helpful=11 → helpful=12 (restart needed)
- [infra-00002] helpful=6 → helpful=7 (should have verified before QA)
- [code-00001] helpful=14 → helpful=15 (frontend rebuild fixed 500s)

### New Bullets Added

None - issues this sprint were already documented. Existing lessons need better enforcement, not new documentation.

---

## Part C: Action Items

**0 new action items** - Existing TEAM_PLAYBOOK bullets cover these issues. Focus on following existing lessons.

**Enforcement Note:** Both blockers (frontend 500, backend stale code) are already documented in TEAM_PLAYBOOK. The team should re-read [infra-00001], [infra-00002], [code-00001] before next sprint.

---

## SM Notes

Sprint executed efficiently despite two blockers. Both blockers were resolved quickly because:
1. Root causes were immediately identified
2. Fixes were straightforward (restarts)
3. Team communicated well through SM

No Phase 2 retrospective needed unless Boss feedback reveals new issues.
