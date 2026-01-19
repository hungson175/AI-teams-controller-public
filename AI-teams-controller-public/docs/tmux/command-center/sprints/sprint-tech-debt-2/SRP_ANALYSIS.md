# SRP Analysis - Sprint 2 Post-Review

**Author:** TL
**Date:** 2026-01-11
**Purpose:** Analyze remaining large files for Single Responsibility Principle violations per Boss directive.

---

## Executive Summary

Boss is correct: **Files >500 lines signal SRP violations**. All 3 files violate SRP.

| File | Lines | SRP Violations | Primary Issue |
|------|-------|----------------|---------------|
| TmuxController.tsx | 534 | 4 | Polling logic not in hooks |
| tmux_service.py | 640 | 2 | Team lifecycle (245 lines) |
| file_service.py | 540 | 1 | TreeBuilder not extracted |

---

## 1. TmuxController.tsx (534 lines)

### Current Responsibilities (After Sprint 2)

| Responsibility | Lines | Extracted? |
|----------------|-------|------------|
| Team/Role State | ~20 | ✅ useTeamState |
| Pane Polling | ~30 | ✅ usePanePolling |
| Team Lifecycle | ~20 | ✅ useTeamLifecycle |
| **Team Activity Polling** | ~50 | ❌ Lines 188-236 |
| **Role Activity Polling** | ~40 | ❌ Lines 244-282 |
| **Scroll Management** | ~60 | ❌ Lines 152-176, 285-309 |
| **Audio Feedback** | ~25 | ❌ Lines 401-426 |
| UI State (misc) | ~20 | ✅ Local (acceptable) |
| Rendering | ~160 | ✅ Local (acceptable) |

### SRP Violations

1. **Team Activity Polling (lines 188-236)** - 48 lines
   - Polls teams every 10 seconds
   - Handles token refresh
   - Updates notifications
   - **Should be in:** `useTeamState` hook (already exists, needs merge)

2. **Role Activity Polling (lines 244-282)** - 38 lines
   - Polls role activity every 5 seconds
   - Handles token refresh
   - **Should be in:** `usePanePolling` hook or new `useRoleActivity`

3. **Scroll Management (lines 152-176, 285-309)** - 50 lines
   - handleScroll, scrollToBottom
   - Auto-scroll on role selection
   - Scroll FAB visibility
   - **Should be in:** `useScrollManager` hook (new)

4. **Audio Feedback (lines 401-426)** - 25 lines
   - Headphone toggle beeps
   - AudioContext creation
   - **Should be in:** `useAudioFeedback` hook or utility

### Sprint 3 Recommendation - FE

| Extraction | Est | Lines Saved | New Lines |
|------------|-----|-------------|-----------|
| Merge polling into useTeamState | 1h | 48 | 48 |
| Merge activity into usePanePolling | 1h | 38 | 38 |
| Extract useScrollManager | 1h | 50 | 60 |
| Extract useAudioFeedback | 0.5h | 25 | 30 |

**Expected Result:** TmuxController.tsx → ~370 lines

---

## 2. tmux_service.py (640 lines)

### Current Responsibilities (After Sprint 2)

| Responsibility | Lines | Extracted? |
|----------------|-------|------------|
| Activity Detection | ~10 | ✅ ActivityDetector (delegate) |
| Message Tracking | ~5 | ✅ MessageTracker (delegate) |
| Tmux Execution | ~5 | ✅ TmuxRunner (delegate) |
| **Team Lifecycle** | ~245 | ❌ Lines 327-572 |
| **Team Query** | ~80 | ❌ Lines 79-106, 574-637 |
| Role/Pane Query | ~80 | Acceptable (core responsibility) |
| Message Sending | ~60 | Acceptable (core responsibility) |
| Pane State | ~60 | Acceptable (core responsibility) |

### SRP Violations

1. **Team Lifecycle Management (lines 327-572)** - 245 lines (38% of file!)
   - `kill_team()` - 30 lines
   - `restart_team()` - 97 lines
   - `create_terminal()` - 63 lines
   - `_find_setup_script()` - 42 lines
   - `_validate_team_exists()` - 7 lines
   - **Should be in:** `TeamLifecycleManager` class (new)

2. **Team Query Methods (lines 79-106, 574-637)** - 76 lines
   - `get_teams()` - 28 lines
   - `list_available_teams()` - 54 lines
   - `_check_team_active()` - 8 lines
   - **Could be in:** `TeamQueryService` class (optional)

### Sprint 3 Recommendation - BE

| Extraction | Est | Lines Saved | New Lines |
|------------|-----|-------------|-----------|
| Extract TeamLifecycleManager | 2h | 245 | 260 |
| Keep team query in TmuxService | - | 0 | 0 |

**Expected Result:** tmux_service.py → ~395 lines (meets <400 target!)

---

## 3. file_service.py (540 lines)

### Current Responsibilities (After Sprint 2)

| Responsibility | Lines | Extracted? |
|----------------|-------|------------|
| Content Indexing | ~25 | ✅ ContentIndexer (delegate) |
| **Tree Building** | ~102 | ❌ Lines 277-379 |
| Project Root Resolution | ~48 | Acceptable (low complexity) |
| Path Validation | ~50 | Acceptable (security-critical) |
| Security Checks | ~65 | Acceptable (grouped properly) |
| File Content Reading | ~147 | Acceptable (core responsibility) |

### SRP Violations

1. **Tree Building NOT Extracted (lines 277-379)** - 102 lines
   - `list_directory()` - 35 lines
   - `_build_tree()` - 67 lines
   - **Sprint 2 spec said to extract TreeBuilder - NOT DONE!**
   - **Should be in:** `TreeBuilder` class (per original spec)

### Sprint 3 Recommendation - BE

| Extraction | Est | Lines Saved | New Lines |
|------------|-----|-------------|-----------|
| Extract TreeBuilder (per Sprint 2 spec) | 1.5h | 102 | 110 |

**Expected Result:** file_service.py → ~438 lines (close to <400 target)

---

## Sprint 3 Work Items (Boss Directive)

Based on this SRP analysis, Sprint 3 should include:

### High Priority (Required to Meet Line Targets)

| Item | Owner | Est | Impact |
|------|-------|-----|--------|
| Extract TeamLifecycleManager from tmux_service.py | BE | 2h | 640→395 |
| Extract TreeBuilder from file_service.py | BE | 1.5h | 540→438 |
| Merge polling into existing FE hooks | FE | 2h | 534→446 |

### Medium Priority (SRP Improvement)

| Item | Owner | Est | Impact |
|------|-------|-----|--------|
| Extract useScrollManager from TmuxController | FE | 1h | 446→396 |
| Extract useAudioFeedback from TmuxController | FE | 0.5h | 396→371 |

### Total Estimates

- **High Priority:** 5.5h
- **Medium Priority:** 1.5h
- **Total:** 7h

### Expected Final Line Counts

| File | Current | After High Priority | After All |
|------|---------|---------------------|-----------|
| TmuxController.tsx | 534 | 446 | ~370 ✅ |
| tmux_service.py | 640 | 395 | 395 ✅ |
| file_service.py | 540 | 438 | 438 (close) |

---

## Root Cause Analysis

**Why did Sprint 2 not meet targets?**

1. **TreeBuilder not extracted** - spec said to do it, BE didn't complete it
2. **Team Lifecycle not identified** - 245 lines (38%) wasn't in original spec
3. **Polling logic stayed in component** - should have been merged into hooks
4. **Line targets were achievable** - but extraction scope was underestimated

**Lesson Learned:** SRP analysis should drive extraction scope, not just "extract hooks/classes."

---

## Conclusion

Boss's insight is validated. All 3 files violate SRP:

1. **TmuxController.tsx** - Polling and scroll logic mixed with rendering
2. **tmux_service.py** - Team lifecycle is a separate concern (38% of file)
3. **file_service.py** - TreeBuilder specified but not extracted

Sprint 3 should focus on these specific extractions to meet the <500/<400 targets.
