# Sprint 13 Retrospective Notes

**Sprint**: Mini IDE Sprint 2 - Syntax Highlighting + Terminal Quick View
**Date**: 2026-01-04
**Status**: IN PROGRESS

---

## CRITICAL Issue #1: TDD Process Violation (05:29)

**What Happened:**
- FE reported "Work Item #1 COMPLETE" (05:28)
- Detailed implementation tasks in report (CodeMirror installed, component created, etc.)
- SM accepted completion and assigned Work Item #2
- Boss asked: "Did FE bypass TDD?" (05:29)
- Investigation: CodeEditor.test.tsx does NOT exist
- TDD was explicit backlog requirement (Task #7 + AC)

**Impact:**
- Work Item #1 actually INCOMPLETE (no tests)
- Had to stop Work Item #2 and backtrack
- Process integrity broken
- TDD discipline lost

**Root Causes:**

1. **FE Prompt Weakening:**
   - Earlier use of `/prompting` skill may have weakened TDD enforcement
   - FE_PROMPT.md TDD section not emphatic enough
   - No "CRITICAL" or "MANDATORY" language
   - FE implemented code-first instead of tests-first

2. **SM Verification Failure:**
   - SM accepted completion report without verification
   - Did NOT check for test files before accepting
   - Did NOT validate all backlog requirements met
   - Moved to next work item without verification

**Why This Matters:**
- TDD has been core practice since Sprint 1 (both FE and BE)
- Losing TDD = losing quality gates
- Boss caught violation, not SM (process guardian failure)
- Demonstrates prompting skill can remove critical constraints

**Action Items for Retrospective:**

1. ✅ **DONE DURING SPRINT**: Strengthened FE_PROMPT.md and BE_PROMPT.md
   - Added "CRITICAL: TESTS FIRST, CODE SECOND - NO EXCEPTIONS"
   - Made TDD enforcement explicit and mandatory
   - Added "Writing code before tests is a process violation"

2. **FOR RETROSPECTIVE**: Add SM verification checklist
   - When accepting work completion, SM must verify:
     - All backlog tasks complete?
     - Test files exist?
     - All acceptance criteria met?
   - Update SM_PROMPT.md with verification workflow

3. **FOR RETROSPECTIVE**: Document "fix/instruct" protocol
   - When Boss says "fix" or "instruct" → edit markdown files
   - Add to SM_PROMPT.md
   - Ensures SM takes direct action on process issues

**Lesson:**
Prompt optimization can remove critical constraints. TDD must be EMPHATIC in prompts, not just mentioned. SM must VERIFY completion, not just accept reports.

**Boss Directives:**
1. "Fix the prompt to ensure TDD practices are followed when developers work, including both frontend and backend."
2. "Establish code coverage standards - research what's reasonable, not arbitrary 100%."
3. "TL must specify coverage percentage in specs going forward."

**Actions Taken:**
- ✅ Strengthened FE_PROMPT.md and BE_PROMPT.md with emphatic TDD requirements
- ✅ Added SM verification checklist before accepting work
- ✅ Added "fix/instruct" = edit markdown protocol to SM_PROMPT.md
- ✅ Assigned TL to research code coverage standards (/quick-research)
- ✅ FE wrote CodeEditor.test.tsx (12/12 tests passing, verified)

Status: Work Item #1 COMPLETE with tests. FE on Work Item #2 (TDD approach). TL researching coverage standards.

---

## CRITICAL Issue #2: Passive Communication Pattern (05:02-05:08)

**What Happened:**
- SM sent tm-send to TL requesting backlog review (05:03)
- SM "stood by" passively waiting for response
- TL didn't respond immediately (AI agents don't auto-respond)
- Sprint 13 planning BLOCKED
- Boss intervened: "Why don't you send tm-send to make others work?"

**Impact:**
- Sprint planning stalled
- Boss had to force action
- Demonstrated passive coordination = broken system

**Root Cause:**
- Earlier prompt optimization may have removed active communication emphasis
- SM reverted to passive "wait and see" instead of active "verify and engage"
- AI agents need explicit reminders to communicate

**Action Taken:**
- ✅ Updated SM_PROMPT.md with "CRITICAL: Active Coordination in AI Teams"
- ✅ Updated TL_PROMPT.md with acknowledgment requirements
- ✅ Updated workflow.md with active communication section
- ✅ All roles re-read updated documentation
- ✅ Stored failure pattern in coder-memory (doc ID: 515bc593)

**Fix Demonstrated:**
- TL acknowledged immediately after update
- FE acknowledged work assignments
- Active coordination working

**Lesson:**
AI multi-agent teams require EXPLICIT active communication instructions. Shortened prompts can remove critical behavioral requirements.

---

## Issues for Retrospective Discussion

1. **Prompt Optimization Risk:**
   - Using `/prompting` skill to "optimize" can remove critical constraints
   - Need guidelines: What can be shortened vs. what must stay emphatic
   - TDD, reporting, active communication are NON-NEGOTIABLE

2. **SM Verification Workflow:**
   - Add formal verification checklist to SM_PROMPT.md
   - Before accepting completion: verify tests, verify requirements, verify deliverables

3. **"Fix/Instruct" Protocol:**
   - When Boss says "fix/instruct" → SM edits markdown files
   - Document this in SM_PROMPT.md

---

## Boss Demo Feedback (Issue #3) - Post-Sprint Discovery (06:46)

**What Happened:**
- Boss demoed Sprint 13 after PO acceptance (9/10 AC)
- Discovered two issues not caught by QA testing:

**CRITICAL - Popup Not Scrollable:**
- Boss quote: "making it scrollable is an easy fix—do that right away"
- Current behavior: Popup shows only 1 page of content
- Impact: "pretty meaningless" for files longer than viewport
- Most real files are longer than 1 page
- Classification: P0 blocker (breaks core usability)

**COMPLEX - File Path Parsing Bugs:**
- Long paths: only end part clickable (line wrap issue)
- Inconsistent clickability for identical-looking links
- Naive parsing: doesn't handle relative vs absolute paths
- Claude Code outputs paths relative to different dirs
- Boss: "Try to fix them if you can; if not, leave it"
- Classification: P1 technical debt (gradual improvement)

**Why QA Missed These:**
1. **Scrollable Popup:**
   - QA tested with short files (sprint_backlog.md might fit in viewport)
   - Didn't test with long files (workflow.md, large code files)
   - AC6 "Clicking opens file popup" was too vague
   - AC needed: "Popup shows FULL file content with scroll"

2. **Path Parsing:**
   - QA tested only basic cases (short paths, consistent format)
   - Didn't test edge cases: long paths, relative paths, different formats
   - AC5 "File paths in terminal clickable" didn't specify ALL paths
   - Real usage revealed edge cases

**Action Items:**

1. ✅ **DONE**: SM decided hotfix approach for scrollable popup
   - Not Sprint 14 (too critical to wait)
   - Boss said "easy fix, do right away"
   - FE will fix immediately after retro

2. **FOR SPRINT 14**: Path parsing improvements
   - Document in Sprint 14 backlog as P1 technical debt
   - TL to design robust path parsing (relative/absolute, line wrap)
   - Not sprint-blocker (Boss: "if you can")

3. **QA IMPROVEMENT**: Test with realistic data
   - Short files ≠ real usage
   - Test edge cases, not just happy path
   - Add to QA_PROMPT.md: "Test with production-like data"

**Lesson:**
QA testing with ideal/short data misses real-world issues. Boss demo with real usage reveals gaps. Acceptance criteria must be specific about edge cases (scroll, long paths, etc.).

---

## Sprint 13 Final Metrics

**Acceptance Criteria:** 9/10 PASS (90% success rate)
- AC8 (click-outside) deferred to Sprint 14
- AC1-7, AC9-10 all PASS

**Test Coverage:**
- Total tests: 76 (progressive: 12→16→21→27)
- Coverage: 86-96% (exceeds 70% minimum)
- TDD Compliance: 100% (after WI#1 correction)

**Code Quality:**
- TL code review: PASS (all 4 work items approved)
- Progressive implementation: 4 work items, small commits
- All Sprint 12 features preserved

**Value Delivered:**
- Professional code editor with syntax highlighting (11 languages)
- Terminal file path quick view with popup
- 70% of Mini IDE Epic complete (up from 40%)

**Process Adherence:**
- Sprint planning: Complete with TL specs
- TDD enforcement: Fixed mid-sprint, then 100% compliance
- Code review: Thorough (TL approved all work items)
- QA testing: Systematic (10 AC tested)

**Issues Discovered:**
- 2 critical issues caught and fixed during sprint (TDD, passive comms)
- 2 issues discovered in Boss demo (scrollable popup, path parsing)

---

## Retrospective Summary

**What Went Well:**
1. ✅ Quick recovery from TDD violation - FE wrote tests immediately
2. ✅ Active communication fixed and working - all roles acknowledged
3. ✅ Progressive implementation - 4 work items, incremental value
4. ✅ High test coverage - 76 tests, 86-96% coverage
5. ✅ Code coverage standards established - TL research, Boss-approved
6. ✅ Professional feature delivery - syntax highlighting working

**What Didn't Go Well:**
1. ❌ TDD violation on WI#1 - FE bypassed tests initially
2. ❌ Passive communication - SM didn't actively engage TL
3. ❌ QA testing gaps - missed scrollable popup and path parsing issues
4. ❌ Vague acceptance criteria - "opens popup" vs "shows full content with scroll"

**Action Items Applied During Sprint:**
1. ✅ Strengthened TDD enforcement in FE/BE prompts
2. ✅ Added SM verification checklist before accepting work
3. ✅ Updated all role prompts with active communication
4. ✅ Established code coverage standards (Frontend 70%, Backend 80%)

**Action Items for After Sprint:**
1. 🔧 **IMMEDIATE**: FE hotfix for scrollable popup (P0 blocker)
2. 📋 **SPRINT 14**: Path parsing improvements (P1 technical debt)
3. 📝 **QA IMPROVEMENT**: Update QA_PROMPT.md with realistic data testing

**Prompt Changes Made:**
- `FE_PROMPT.md` - Emphatic TDD requirements
- `BE_PROMPT.md` - Emphatic TDD requirements
- `SM_PROMPT.md` - Verification checklist, active coordination
- `TL_PROMPT.md` - Acknowledgment requirements, coverage standards
- `workflow.md` - Active communication section, coverage standards

**Overall Assessment:**
Sprint 13 delivered professional code editing with syntax highlighting. Two critical process issues (TDD, communication) were caught and fixed mid-sprint. Boss demo revealed two usability gaps (scrollable popup, path parsing).

**90% success rate is excellent** given the complexity. The scrollable popup is a straightforward fix (Boss: "easy fix"). Path parsing is gradual improvement work.

**Key Lesson:** Prompt optimization can remove critical constraints. TDD, reporting, and active communication are NON-NEGOTIABLE and must stay emphatic in prompts.

---

**Retrospective Status:** ✅ COMPLETE
**Completed By:** SM (Scrum Master)
**Date:** 2026-01-04 06:48
