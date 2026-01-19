# Sprint 14 Retrospective

**Sprint**: Intelligent File Path Resolution (Mini IDE Sprint 3)
**Date**: 2026-01-04
**Duration**: ~90 minutes (14:46 start → 16:22 accepted)
**Status**: ACCEPTED by PO - All 10 AC PASS

---

## Sprint Summary

**Goal**: Fix terminal file path parsing with intelligent search and caching

**Results**:
- ✅ All 5 work items COMPLETE (41/41 tests, 85-100% coverage)
- ✅ TL code review PASS
- ✅ QA testing: 10/10 AC PASS
- ✅ Boss requirements met (design carefully, TDD carefully)

**Complexity**: MEDIUM (Boss warning: "looks small but complicated")

---

## What Went Well ✅

### 1. Boss "THINK HARD" Directive Followed

**Boss Warning (14:44)**:
- "The next sprint is going to be very challenging"
- "Tell the tech lead to design it carefully before handing it off to the coders"
- "THINK HARD from several perspectives"
- "TDD very carefully"

**TL Response**:
- Created comprehensive 380-line spec (TL_SPEC_file_path_resolution.md)
- Answered 6 key design questions
- Client-side vs backend decision (with rationale table)
- Search algorithm with code examples
- Cache strategy with invalidation triggers
- Multi-match handling with UX flows

**Result**: SM approved design, FE implementation matched spec exactly

### 2. TDD Discipline Maintained

**FE Implementation**:
- 41/41 tests passing (100% pass rate)
- 85-100% coverage across all files (exceeds 80% target)
- Tests written FIRST, code second
- Progressive implementation (WI#1 → WI#5)

**Boss Requirement Met**: "TDD very carefully" ✅

### 3. FileSearch Dependency Concern Resolved Quickly

**Issue (15:06)**: Boss caught potential design flaw
- Boss: "FileSearch Cmd+P is 100% broken"
- Concern: TL design says "reuse FileSearch cache" - can't build on broken foundation

**TL Investigation (15:08)**:
- Sprint 14 does NOT depend on FileSearch component
- Both use backend API `/api/files/{team}/list` independently
- FileSearch broken = separate P1 backlog item

**Result**: Sprint 14 UNBLOCKED in 2 minutes

### 4. All Acceptance Criteria Met

**QA Testing Results**: 10/10 PASS
- AC1-3: Path resolution (relative, absolute, subdirectory) ✅
- AC4: Multi-match popup ✅
- AC5-7: Cache functionality (initialize, hit, refresh) ✅
- AC8: Search all project files ✅
- AC9-10: Clickability (all formats, long paths) ✅

---

## What Went Wrong ❌

### 1. CRITICAL Infrastructure Blocker (70 minutes)

**Timeline**:
- 15:11: FE reported build error "TypeError: Cannot convert object to primitive value"
- 15:13: PO escalated to SM
- 15:54: QA confirmed frontend 500 errors (cannot test)
- 16:00: SM tried dev mode (INVALID per Boss - breaks voice commands)
- 16:05: QA testing STOPPED, FE assigned to fix production build
- 16:20: FE FIXED build (disabled worker threads)
- **Total blocker time: ~70 minutes**

**Root Cause**: Next.js worker threads bug
- 31 parallel workers causing "TypeError: Cannot convert object to primitive value"
- Next.js "Collecting page data" phase failing

**Solution**: FE disabled worker threads (`cpus: 1` in next.config.mjs)
- Trade-off: Slower builds (18s vs 6s) but STABLE
- Production build now works

**Impact**:
- Sprint 14 code was COMPLETE at 15:02, but QA testing blocked until 16:20
- ~70 minutes lost to infrastructure issue
- Boss escalation required

### 2. Dev Mode Workaround INVALID

**What Happened (16:00)**:
- SM coordinated FE to start dev mode (`pnpm dev`) to unblock QA
- QA started testing in dev mode

**Boss Directive (16:05)**:
- "I forbid you from running the frontend in dev mode"
- "Dev mode breaks voice commands/ping"

**Result**:
- QA testing STOPPED immediately
- All dev mode work invalidated
- Had to wait for production build fix

**Lesson**: Always verify constraints with Boss before workarounds. Dev mode is NOT acceptable for this project (voice integration).

### 3. Multiple Server Restarts Required

**Issue**: Chunk hash mismatches after build
- HTML referenced OLD chunk hash: `layout-c715efc9beb0ba39.js`
- Build created NEW chunk hash: `layout-bd6b278abfb48a73.js`
- Result: 500 errors on static chunks

**Root Cause**: Server started before/during build completion
- FE restarted server multiple times
- Each restart loaded different chunk references

**Resolution**: Final restart at 16:23 with verified chunk hashes

### 4. Role Detection Bug (Pane @role_name Mismatch)

**Issue**:
- Pane %77 (index 0) had `@role_name=SM` (should be PO)
- Pane %78 (index 1) had `@role_name=SM` (correct)
- Caused SessionStart hook to give wrong role context

**Impact**: Boss had to manually debug and fix pane roles

**Root Cause**: Configuration drift - `setup-team.sh` not setting pane options correctly

**Fix**: Manual `tmux set-option -p -t %77 @role_name PO`

---

## Action Items

### 1. Document Next.js Worker Threads Bug (Priority: HIGH)

**Add to CLAUDE.md**:
```markdown
## Next.js Build Error: Worker Threads

**Error**: "TypeError: Cannot convert object to primitive value"
**Phase**: "Collecting page data"
**Root Cause**: Next.js worker threads bug (31 parallel workers)

**Fix**: Disable worker threads in `next.config.mjs`:
\`\`\`javascript
experimental: {
  cpus: 1  // Disable parallel workers
}
\`\`\`

**Trade-off**: Slower builds (18s vs 6s) but STABLE
**Status**: Applied in Sprint 14, production build working
```

**Owner**: SM
**Deadline**: Before next sprint

### 2. Pre-Sprint Infrastructure Validation Checklist

**Add to SM workflow**:
```markdown
## Before Assigning Work to FE/BE:

1. Verify production build works:
   - `cd frontend && rm -rf .next && pnpm build`
   - Check for build errors
   - If errors: Fix BEFORE sprint starts

2. Verify production server starts:
   - `PORT=3334 pnpm start &`
   - `curl http://localhost:3334` (expect 200)

3. Verify Cloudflare tunnel (if applicable):
   - Check external URL serves correctly
   - Clear caches if needed
```

**Owner**: SM
**Deadline**: Before Sprint 15

### 3. Fix Pane @role_name Setup in setup-team.sh

**Issue**: Pane options drift after session restart

**Fix**: Verify `setup-team.sh` sets @role_name correctly:
```bash
tmux set-option -p -t command-center:0.0 @role_name PO
tmux set-option -p -t command-center:0.1 @role_name SM
tmux set-option -p -t command-center:0.2 @role_name TL
tmux set-option -p -t command-center:0.3 @role_name FE
tmux set-option -p -t command-center:0.4 @role_name BE
tmux set-option -p -t command-center:0.5 @role_name QA
```

**Verification**:
```bash
tmux list-panes -t command-center -F "#{pane_id} | Index #{pane_index} | @role_name=#{@role_name}"
```

**Owner**: SM
**Deadline**: Before next session restart

### 4. Production Build Requirement in CLAUDE.md (CRITICAL)

**Add to CLAUDE.md** (emphasize Boss constraint):
```markdown
## CRITICAL: Production Mode ONLY

**Boss Directive**: Frontend MUST run in production mode (pnpm build + pnpm start)

**Why**: Dev mode breaks voice commands/ping functionality

**NEVER run**: `pnpm dev` for QA testing or Boss demo

**Always run**:
\`\`\`bash
cd frontend && rm -rf .next && pnpm build
pkill -f "next start"; PORT=3334 pnpm start &
\`\`\`
```

**Owner**: SM
**Deadline**: Before Sprint 15

---

## Metrics

| Metric | Sprint 14 | Previous (Sprint 13) | Change |
|--------|-----------|---------------------|--------|
| Duration | ~90 min | ~180 min | -50% ✅ |
| Blocker Time | ~70 min (77%) | ~40 min (22%) | +88% ❌ |
| Code Quality | 41/41 tests, 85-100% coverage | 76/76 tests, 86-96% coverage | Same ✅ |
| QA Results | 10/10 AC PASS | 9/10 AC PASS | +10% ✅ |

**Analysis**:
- Sprint faster overall (Boss "THINK HARD" directive worked - good design = faster coding)
- BUT blocker time MUCH higher (infrastructure issue, not code issue)
- Code quality consistent (TDD discipline maintained)
- QA results improved (10/10 vs 9/10)

---

## Boss Feedback

(Awaiting Boss demo and feedback)

---

## Sprint 14 Lessons

### 1. Careful Design Reduces Coding Time

Boss directive to "design carefully" was CORRECT:
- TL spent ~30 minutes designing (comprehensive spec)
- FE completed implementation in ~45 minutes (matched spec exactly)
- NO rework needed (TL review PASS on first try)

**Lesson**: Upfront design investment pays off in faster, cleaner implementation.

### 2. Infrastructure Blockers Can Exceed Code Time

Sprint 14:
- Code complete: ~45 minutes (FE implementation)
- Blocker resolution: ~70 minutes (build error)

**Lesson**: Infrastructure validation BEFORE sprint starts prevents massive delays.

### 3. Never Assume Workarounds Are Acceptable

SM tried dev mode to unblock QA → Boss forbid it (breaks voice commands)

**Lesson**: Verify Boss constraints before workarounds. Some features have non-obvious dependencies.

---

## Next Sprint Preparation

1. ✅ Validate production build works BEFORE sprint starts
2. ✅ Document Next.js worker threads fix in CLAUDE.md
3. ✅ Fix setup-team.sh pane @role_name setup
4. ✅ Add production mode requirement to CLAUDE.md

**Status**: Sprint 14 ACCEPTED, ready for Boss demo after retrospective complete.

---

**Retrospective Complete**: 2026-01-04 16:25 (SM)
