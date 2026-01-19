# Sprint 12 Retrospective Notes

## CRITICAL Issue: FE Completed Task But Didn't Report (18:24)

**What Happened:**
- SM assigned FE to debug login UI issue (18:21)
- FE completed analysis (identified browser DevTools needed, offered debug logging)
- FE DID NOT report findings to SM
- Entire sprint BLOCKED - SM waiting for report that never came
- Boss discovered FE was silently done (18:24)

**Impact:**
- Sprint stalled for ~3 minutes while team waited
- SM couldn't proceed to next step (coordinate QA debugging)
- Pattern: Silent completion breaks multi-agent coordination

**Root Cause:**
- FE didn't follow mandatory "Report Back After Every Task" rule
- FE_PROMPT.md lines 224-238 clearly states this requirement
- Agent completed work but failed to communicate completion

**Why This Matters:**
- In multi-agent systems, visibility is NOT automatic
- Each agent operates in isolation
- Without explicit reporting, SM cannot proceed
- System stalls = sprint delays

**Action Items:**
1. ✅ FE_PROMPT.md already has reporting requirement (lines 224-238)
2. Consider: Strengthen language? Add examples of what happens when agents don't report?
3. Monitor: Is this a pattern across other roles? Check other sprints.
4. Remind all agents: Completing work ≠ Reporting completion

**Lesson:**
REPORTING IS MANDATORY. Finishing a task without reporting = NOT DONE.

---

---

## SECOND Reporting Violation: QA Completed Login Test But Didn't Report (04:06)

**What Happened:**
- SM assigned QA to test login with browser console open (18:40)
- QA completed testing (~04:06)
- QA found login WORKS (HTTP 200, tokens received, navigation successful)
- QA DID NOT report findings to SM
- SM had to check QA pane to discover work was done
- Pattern: Second silent completion in same sprint (FE did same at 18:24)

**Impact:**
- SM couldn't proceed to next step (assign actual Sprint 12 testing)
- Sprint coordination delayed again
- Boss had to send directive to continue work (04:06)

**Root Cause:**
- QA completed diagnostic work but failed to communicate completion
- Same violation as FE earlier in sprint
- Both agents have "Report Back After Every Task" requirement in their prompts

**Pattern Recognition:**
- This is now a SYSTEMIC issue, not individual agent error
- 2 different agents (FE and QA) violated same rule in same sprint
- Reporting requirement exists but agents aren't following it

**Action Items for Retrospective:**
1. Why are agents completing work without reporting despite explicit requirements?
2. Is language too weak? (Already strengthened after FE violation)
3. Do agents need automated reminders?
4. Should SM check agent panes more proactively?

**Lesson:**
"Report Back" requirement exists in ALL role prompts, but enforcement is weak. Agents complete work and stop, forgetting that reporting IS part of completing the work.

---

## Login Blocker Resolution (04:06)

**Issue:**
- Login UI wasn't working (18:20)
- Sign In button didn't navigate to dashboard

**Resolution Approach:**
- FE added comprehensive debug logging (18:39)
- QA tested with browser console open (04:06)
- Console logs showed: HTTP 200 OK, tokens received, navigation successful
- **Login works after debug logging added**

**Root Cause:**
- Unknown - debug logging showed flow working correctly
- Likely: Adding logs forced frontend rebuild which cleared stale state
- Common pattern: "Heisenbug" - adding debug logging fixes the issue

**Lesson:**
- Debug logging + frontend rebuild resolved issue
- Frontend production mode requires manual rebuild after code changes
- Always try clean rebuild before complex debugging

**Timeline:**
- 18:20: Login blocker discovered
- 18:21: FE assigned to debug
- 18:36: FE reported analysis (16 min late)
- 18:39: FE added debug logging + rebuilt
- 04:06: QA tested - login WORKS
- Total blocker time: ~10 hours (but mostly overnight gap)

---

## Backend Not Restarted After Implementation (04:12)

**Issue:**
- QA testing found: PUT /api/files/{team}/{path} → 404 Not Found
- BE had implemented endpoint (commit b2f66f4, 2026-01-03 17:49)
- TL code review passed
- But endpoint didn't exist at runtime

**Root Cause:**
- Backend service was running old code from before BE's implementation
- Backend process started before Sprint 12 code was committed
- Production services don't auto-reload - require manual restart

**Impact:**
- Sprint 12 testing blocked on AC4 and AC5 (Save functionality)
- QA reported 5/7 PASS, 2/7 FAIL due to backend 404

**Resolution:**
- SM restarted backend service (04:12)
- Backend version updated: 928746b → 13d24f3 (latest)
- PUT endpoint tested via curl: SUCCESS
- QA can now retry testing

**Pattern Recognition:**
- **SAME issue as frontend earlier** (port 3334 not running latest code)
- Both frontend and backend required manual restart after code changes
- This is the THIRD infrastructure issue in Sprint 12:
  1. Frontend port not running (17:58) - resolved by restart
  2. Login UI issue (18:20) - resolved by frontend rebuild
  3. Backend 404 (04:12) - resolved by backend restart

**Lesson:**
After ANY code implementation:
1. **Frontend:** Must rebuild and restart (`rm -rf .next && pnpm build && restart`)
2. **Backend:** Must restart service to load new code

**Action Item for Process:**
- Add to completion checklist: "Restart service after implementation"
- FE/BE should restart services BEFORE reporting "DONE"
- Or: SM should proactively restart services after each phase

**Why This Matters:**
- Code exists in git but not in running service = sprint blocked
- QA tests against old code, gets false failures
- Wastes coordination time debugging non-existent issues

---
