# Retrospective Log - Scrum Team

## Sprint 3+4+5 Retrospective

**Date**: 2025-12-30
**Facilitator**: SM (Scrum Master)
**Participants**: PO, TL, FE, BE, QA

---

## Sprint Summary

| Sprint | Goal | Outcome |
|--------|------|---------|
| Sprint 3 | File browser improvements (scroll, width, search, stop button) | ❌ REJECTED - Scroll fix didn't work |
| Sprint 4 | Fix file browser left panel scroll | ✅ ACCEPTED |
| Sprint 5 | Fix mobile headphone button toggle | ⏳ IN PROGRESS (deprioritized) |

---

## 1. What Went Well

### Technical Excellence
- **TL Root Cause Analysis**: TL conducted 4 thorough investigations for Sprint 5 mobile headphone bug, each building on previous findings. Final root cause (#4) identified fundamental issue with Media Session API usage.
- **CSS Flexbox Pattern**: TL identified that `min-h-0 overflow-hidden` must be applied to ENTIRE flex ancestor chain for ScrollArea to work. Pattern stored in memory for future use.
- **FE TDD Correction**: After Boss flagged TDD violation, FE correctly followed TDD workflow (test first → fail → fix → pass) for fix #3. 13/13 tests passing.

### Process Improvements
- **QA Browser-Based Testing**: QA used Playwright for blackbox testing from user perspective, not code inspection. Correctly identified limitations (physical hardware buttons can't be simulated).
- **WHITEBOARD Usage**: Team actively updated WHITEBOARD with status, blockers, and root cause analyses. Single source of truth worked well.
- **tm-send Communication**: Communication via tm-send was reliable and traceable.

### Deliverables
- Sprint 4 scroll fix delivered and accepted by Boss
- Stop button feature completed
- File search (Cmd+P) feature completed
- Panel width improvements completed

---

## 2. What Didn't Go Well

### CRITICAL: PO Was Coding (Role Boundary Violation)
**Problem**: PO implemented features directly (Stop button, scroll fixes) instead of delegating through SM → TL → FE/BE workflow.

**Impact**:
- Role boundaries violated
- FE/BE team members idle while PO coded
- Sprint 3 was rejected partly due to rushed implementation

**Root Cause**: Urgency to deliver quickly led to shortcutting the process.

### CRITICAL: TDD Not Followed (Sprint 5)
**Problem**: FE fixed Sprint 5 bug (fix #2) without writing regression test first.

**Impact**:
- Boss flagged this as policy violation
- Risk of regressions during future refactoring
- Had to retrofit tests after the fact

**Root Cause**: SM did not enforce TDD requirement when assigning task initially.

### Sprint 3 Rejection
**Problem**: Sprint 3 was rejected because scroll fix didn't work. QA tested "click-to-scroll" which wasn't real scrolling functionality.

**Impact**: Rework required in Sprint 4.

**Root Cause**:
- PO implemented fix without TL spec (role violation)
- QA testing methodology was incorrect for that feature

### Sprint 5 Complexity
**Problem**: Mobile headphone toggle bug required 4 root cause investigations and 3 failed fixes before finding fundamental issue.

**Impact**: Sprint 5 extended significantly, eventually deprioritized.

**Insight**: Mobile Chrome Media Session API behavior is fundamentally different from desktop. Hard-earned lesson stored in memory system.

---

## 3. Action Items for Improvement

### FOCUS: ONE Action Item Per Sprint

**Don't fix many issues at once!** Pick ONE with most impact, monitor in next sprint.

---

### Sprint 6 Action Item (ACTIVE)

| Action Item | Owner | How to Verify |
|-------------|-------|---------------|
| **SM enforces TDD on every task** | SM | When assigning task, SM MUST say "TDD required: write test FIRST". Check test exists before accepting work. |

**Why this one?** TDD violation was flagged by Boss, caused rework, risk of regressions. Highest impact.

**How SM will enforce:**
1. Every task assignment includes: "TDD required: write test FIRST"
2. Before accepting completion, ask: "Did you write test first? Show test."
3. If not followed, log to SPRINT_LOG.md immediately

---

### Backlog (Future Sprints - ONE at a time)

| # | Action Item | Owner | Status |
|---|-------------|-------|--------|
| 1 | PO must NOT write code | PO | BACKLOG |
| 2 | TL spec required for all features | SM + TL | BACKLOG |
| 3 | Tag REAL-DEVICE-ONLY features | PO + QA | BACKLOG |
| 4 | Check official docs FIRST | TL | BACKLOG |
| 5 | Store patterns ONLY after fix confirmed | TL | BACKLOG |

---

## Key Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Sprints completed | 2 of 3 | Sprint 3 rejected, Sprint 4 accepted, Sprint 5 in progress |
| Sprint acceptance rate | 50% | Sprint 3 rejected, Sprint 4 accepted |
| Root cause investigations | 4 | Sprint 5 required deep analysis |
| TDD violations | 1 | FE fix #2 in Sprint 5 |
| Role boundary violations | 1 | PO coding in Sprint 3 |

---

## Team Feedback

*(Collected from developers during retrospective)*

### TL Feedback
**What went well:**
- Systematic root cause analysis with clear documentation
- WHITEBOARD kept updated with each hypothesis
- Used web research + memory recall to validate ideas
- Corrected wrong pattern in memory store (deleted incorrect, stored correct)

**What didn't go well:**
- 4 failed hypotheses before finding true root cause - too many iterations
- First stored pattern was WRONG (had to delete it later)
- Should have checked Google's official sample EARLIER
- Hypotheses declared as 'root cause' without mobile device verification

**Suggestions:**
- Check official docs/samples FIRST before hypothesizing
- Add console.log to verify which handlers actually fire on mobile
- Require real device test before marking 'root cause found'
- Don't store patterns to memory until fix is CONFIRMED working
- Consider: TL should have access to mobile testing (via QA or Playwright)

### FE Feedback
**What went well:**
- TDD workflow (Fixes #3 and #4): Writing failing tests first caught issues early
- Clear TL root cause specs: Each fix had precise technical guidance
- Incremental test coverage: Now have 15 comprehensive regression tests
- Audio event-based architecture (Fix #4): Cleaner separation of concerns

**What didn't go well:**
- TDD violation in Fix #2: Implemented before writing tests - had to add tests retroactively
- Multiple fix iterations (4 fixes for one bug): Root cause analysis could have been more thorough upfront
- Mobile Chrome quirks required trial-and-error discovery

**Suggestions:**
- ENFORCE TDD from sprint start: Block merges without test-first evidence
- More thorough upfront debugging: Test on target device before committing to fix approach
- Document mobile browser quirks: Create a knowledge base for Media Session API edge cases
- Consider pair debugging for P0 issues: TL + FE together on mobile device

**Overall**: Sprint 5 demonstrated strong recovery from TDD violation. Final architecture is solid.

### BE Feedback
**What went well:**
- Sprint 4 scroll fix was thorough - FE traced the full flex chain
- QA testing was comprehensive with measurable evidence (scrollHeight, clientHeight metrics)
- WHITEBOARD documentation was excellent for handoff

**What didn't go well:**
- BE was idle for Sprints 3-5 (all frontend work)
- PO coded directly instead of delegating through proper channels
- Sprint 3 was rejected - QA tested 'click-to-scroll' instead of real scroll

**Suggestions:**
- Balance sprints with FE+BE work when possible
- Enforce role boundaries - PO defines requirements, doesn't implement
- QA should verify acceptance criteria match user expectations before testing
- Consider pairing idle developers on reviews or documentation

### QA Feedback
**What went well:**
- MCP Playwright integration excellent for browser blackbox testing
- Clear acceptance criteria made test case creation straightforward
- WHITEBOARD provided good sprint visibility
- tm-send communication protocol worked reliably
- Quick retest turnaround (Fix #2, Fix #3 same day)

**What didn't go well:**
- Sprint 5: Multiple retests needed (initial → Fix #2 → Fix #3) - 3 cycles before stable
- Physical hardware button cannot be tested via Playwright - discovered during testing, not planning
- Sprint 3 scroll fix required Sprint 4 to actually fix - indicates incomplete verification

**Suggestions:**
- Tag features requiring real device testing in acceptance criteria upfront (e.g., 'REAL-DEVICE-ONLY')
- FE/BE self-test more thoroughly before QA handoff to reduce retest cycles
- Add 'Test Environment Limitations' section to sprint planning docs
- For hardware-dependent features, involve Boss earlier for real-device validation

---

## Retrospective Actions Committed

1. **Immediate**: PO stops coding, delegates all implementation
2. **Immediate**: SM adds TDD requirement to every task assignment
3. **Next Sprint**: Review QA testing methodology before sprint starts
4. **Next Sprint**: TL spec required even for "simple" fixes

---

**Next Retrospective**: After Sprint 6 completion

**Retrospective Documented By**: SM
**Date**: 2025-12-30
