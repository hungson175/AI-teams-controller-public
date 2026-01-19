# Sprint 2 Retrospective

**Date**: 2025-12-29
**Facilitator**: SM
**Participants**: TL, FE, BE, QA

---

## What Went Well

| Role | Feedback |
|------|----------|
| **TL** | Tech decision (microfuzz) was correct - 2KB, leveraged 80% existing code. All 4 code reviews passed first attempt. Git safety ops smooth. |
| **FE** | TDD approach - 23 tests total provided confidence for refactoring. Clean Story 2 integration with BE's API (debounce + loading states). Quick turnaround on Boss drop-UP fix request. |
| **BE** | TL specs were comprehensive with detailed test cases. Parallel work with FE was efficient. TDD yielded 10 solid tests. Reused existing FileService patterns for consistency. |
| **QA** | Playwright MCP enabled true blackbox testing - tested like real user. TL specs had clear acceptance criteria - easy to verify. All 5 browser tests passed. Drop-UP retest quick after rebuild confirmation. |

**Key Themes:**
- TL specs quality excellent (again)
- Parallel BE/FE work efficient
- Playwright MCP effective for blackbox testing

---

## What Could Improve

| Role | Feedback |
|------|----------|
| **TL** | Didn't anticipate Drop-UP UX issue - should consider input position in specs. Could parallelize BE/FE stories better (BE Story 2 didn't need to wait for FE Story 1). |
| **FE** | CRITICAL: Must rebuild frontend after EVERY code change in prod mode - caused QA failure. Now documented in FE_PROMPT.md. Async test patterns with fake timers were tricky - learned proper act() wrapping. |
| **BE** | Minor - encountered test file naming conflict (pytest module collision), resolved by adding to existing file. |
| **QA** | Initial approach was wrong (code inspection) - lesson learned. Drop-UP first test failed due to stale frontend - need "FE rebuilt" confirmation before QA retests. |

---

## Critical Lessons Learned (Boss Feedback)

### Lesson 1: QA Must Use Blackbox Testing (MCP Playwright)

**Problem:** QA initially tested by looking at code/implementation details.
**Impact:** Boss rejected testing results - Sprint 2 blocked.
**Fix:**
- QA_PROMPT.md updated with CRITICAL blackbox testing requirement
- QA must use **MCP Playwright** for browser-based testing
- If MCP Playwright unavailable, QA notifies Boss to add it (only Boss can add MCPs)
- QA never looks at code - tests from browser like real user

### Lesson 2: FE Must Restart Frontend After Code Changes

**Problem:** QA tested Drop-UP fix but saw old behavior - frontend wasn't rebuilt.
**Impact:** False negative - fix was working but not deployed.
**Fix:**
- FE_PROMPT.md updated with CRITICAL restart requirement
- Command: `cd frontend && rm -rf .next && pnpm build && pkill -f "node.*next" 2>/dev/null; PORT=3334 pnpm start &`
- FE must verify in browser before reporting "DONE"

### Lesson 3: Consider Screen Position for UI Elements

**Problem:** Autocomplete popup appeared below input (dropdown) - but input is at bottom of screen.
**Impact:** Only 1-2 rows visible - bad UX.
**Fix:**
- Changed to drop-UP (popup above input)
- TL should consider input position when specifying popup direction in specs

---

## Action Items

| # | Action | Owner | Priority | Status |
|---|--------|-------|----------|--------|
| 1 | QA uses Playwright/browser for all testing | QA | High | ✅ Done (QA_PROMPT.md updated) |
| 2 | FE restarts frontend after every code change | FE | High | ✅ Done (FE_PROMPT.md updated) |
| 3 | TL considers screen position for popup specs | TL | Medium | For Sprint 3 |
| 4 | Add "FE confirms rebuild" step before QA retests | SM | Medium | Add to workflow |
| 5 | Parallelize BE/FE work when no dependencies | SM | Low | For Sprint 3 planning |

---

## Sprint 2 Metrics

- **Stories**: 2/2 completed + 1 modification (Drop-UP)
- **Commits**: 4 (f8a4aa3, 58af5f9, a5fd73b, dd2ae08)
- **Tests**: 33 unit/integration (BE: 10, FE: 23) + 5 QA browser tests
- **Rework**: 1 (Drop-UP modification per Boss feedback)
- **Process Fixes**: 3 (QA blackbox, FE restart, popup position)

---

## Prompts Updated

| Prompt | Update |
|--------|--------|
| SM_PROMPT.md | Added "CRITICAL: QA Testing Requirements" section |
| QA_PROMPT.md | Added "CRITICAL: BROWSER-BASED BLACKBOX TESTING ONLY" section |
| FE_PROMPT.md | Added "CRITICAL: Restart Frontend After EVERY Code Change" section |

---

**Retro complete. Process significantly improved for Sprint 3.**
