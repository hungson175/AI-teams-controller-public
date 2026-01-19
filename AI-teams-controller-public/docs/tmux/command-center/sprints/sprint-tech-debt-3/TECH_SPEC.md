# Tech Debt Sprint 3 - SRP Remediation Technical Specification

**Author:** TL
**Date:** 2026-01-11
**Status:** DESIGN COMPLETE
**Basis:** SRP_ANALYSIS.md from Sprint 2 post-review

---

## Overview

Sprint 3 addresses Single Responsibility Principle violations identified in Sprint 2 post-review per Boss directive. Total estimated effort: 7h.

**Targets:**
| File | Current | Target | Expected |
|------|---------|--------|----------|
| TmuxController.tsx | 534 | <400 | ~370 |
| tmux_service.py | 640 | <400 | ~395 |
| file_service.py | 540 | <450 | ~438 |

---

## CRITICAL: TDD + Revertability Protocol (Boss Directive)

**Carried forward from Sprint 2. Same rules apply.**

### TDD Workflow for ALL Refactoring

1. **BEFORE refactoring:**
   - Write tests for existing behavior
   - Tests MUST PASS with current code
   - Commit tests: `test: add tests for [component] existing behavior`

2. **DURING refactoring:**
   - Make incremental changes
   - Run tests after each change
   - Tests MUST PASS at every step

3. **AFTER refactoring:**
   - All existing tests MUST PASS
   - Add new tests for extracted modules
   - Commit: `refactor: extract [module] from [component]`

4. **IF tests fail after refactor:**
   - REVERT immediately
   - Analyze what broke
   - Fix approach, try again

**Breaking working code is DISASTROUS. Tests are the safety net.**

---

## MANDATORY: Refactor Safety Protocol Tables (Boss Directive)

### Test Table - What to Test After Each Section

| Step | Extraction | Test Command | Expected Result | STOP IF |
|------|------------|--------------|-----------------|---------|
| **BE-1** | TeamLifecycleManager | `cd backend && uv run python -m pytest tests/test_tmux_service.py -v` | All tests pass | ANY test fails |
| **BE-2** | TreeBuilder | `cd backend && uv run python -m pytest tests/test_file_routes.py -v` | All tests pass | ANY test fails |
| **FE-1** | Merge team polling into useTeamState | `cd frontend && pnpm test && pnpm build` | All tests + build pass | ANY failure |
| **FE-2** | Merge role polling into usePanePolling | `cd frontend && pnpm test && pnpm build` | All tests + build pass | ANY failure |
| **FE-3** | Extract useScrollManager | `cd frontend && pnpm test && pnpm build` | All tests + build pass | ANY failure |
| **FE-4** | Extract useAudioFeedback | `cd frontend && pnpm test && pnpm build` | All tests + build pass | ANY failure |

### Review Table - TL Checkpoints After Each Extraction

| Checkpoint | After Step | TL Verifies | Pass Criteria |
|------------|------------|-------------|---------------|
| **BE-R1** | TeamLifecycleManager | kill/restart/create APIs work | Teams can be killed, restarted, created via UI |
| **BE-R2** | TreeBuilder | File tree loads correctly | File browser shows tree, navigation works |
| **FE-R1** | Team polling merge | Team notifications work | Activity indicators update, notifications appear |
| **FE-R2** | Role polling merge | Role activity works | Green dots on active roles |
| **FE-R3** | useScrollManager | Scroll behavior preserved | Auto-scroll, FAB, scroll position all work |
| **FE-R4** | useAudioFeedback | Audio beeps work | Headphone toggle plays correct beeps |

### Revert Table - How to Rollback Each Step

| Step | Commit Pattern | Revert Command | Verify After Revert |
|------|----------------|----------------|---------------------|
| **BE-1** | `refactor: extract TeamLifecycleManager` | `git revert HEAD` | `pytest test_tmux_service.py` passes |
| **BE-2** | `refactor: extract TreeBuilder` | `git revert HEAD` | `pytest test_file_routes.py` passes |
| **FE-1** | `refactor: merge team polling into useTeamState` | `git revert HEAD` | `pnpm test && pnpm build` passes |
| **FE-2** | `refactor: merge role polling into usePanePolling` | `git revert HEAD` | `pnpm test && pnpm build` passes |
| **FE-3** | `refactor: extract useScrollManager` | `git revert HEAD` | `pnpm test && pnpm build` passes |
| **FE-4** | `refactor: extract useAudioFeedback` | `git revert HEAD` | `pnpm test && pnpm build` passes |

### Protocol Enforcement

**BEFORE each extraction:**
1. Run test command from Test Table
2. Verify all tests pass
3. Note test count for comparison

**AFTER each extraction:**
1. Run test command from Test Table
2. If ANY test fails → **IMMEDIATE REVERT** using Revert Table
3. If tests pass → Proceed to Review Table checkpoint
4. TL verifies per Review Table criteria
5. If TL rejects → **REVERT** and discuss approach

**Git History Must Be Clean:**
- Each extraction = 1 commit
- Commits must be atomic and revertable
- No mixing multiple extractions in one commit

---

## HIGH PRIORITY Work Items (5.5h)

### Work Item 1: TeamLifecycleManager Extraction (BE)

**Owner:** BE
**Estimate:** 2h
**Impact:** tmux_service.py 640 → ~395 lines

#### Analysis

Team lifecycle is 245 lines (38% of tmux_service.py) - **MAJOR SRP VIOLATION**.

**Methods to extract from TmuxService (lines 327-572):**
```python
# From tmux_service.py
kill_team()              # lines 380-409 (30 lines)
restart_team()           # lines 411-508 (97 lines)
create_terminal()        # lines 510-572 (63 lines)
_find_setup_script()     # lines 329-370 (42 lines)
_validate_team_exists()  # lines 372-378 (7 lines)
list_available_teams()   # lines 574-627 (54 lines)
_check_team_active()     # lines 629-636 (8 lines)
```

#### New Class: TeamLifecycleManager

**Location:** `backend/app/services/team_lifecycle_manager.py`

```python
class TeamLifecycleManager:
    """Manages team (tmux session) lifecycle operations.

    Extracted from TmuxService (Sprint 3) to satisfy SRP.
    Handles: kill, restart, create, list available teams.
    """

    def __init__(self, tmux_runner: TmuxRunner):
        self._runner = tmux_runner

    def kill_team(self, team_id: str) -> dict
    def restart_team(self, team_id: str) -> dict
    def create_terminal(self, name: Optional[str], directory: Optional[str]) -> dict
    def list_available_teams(self) -> list[dict]

    # Private helpers
    def _find_setup_script(self, readme_path: str) -> Optional[str]
    def _validate_team_exists(self, team_id: str) -> bool
    def _check_team_active(self, team_name: str) -> bool
```

#### TmuxService Changes

```python
class TmuxService(TeamService):
    def __init__(self, ...):
        ...
        # Sprint 3: Delegate lifecycle to TeamLifecycleManager
        self._lifecycle_manager = TeamLifecycleManager(TmuxRunner)

    # Facade methods (keep API stable)
    def kill_team(self, team_id: str) -> dict:
        return self._lifecycle_manager.kill_team(team_id)

    def restart_team(self, team_id: str) -> dict:
        return self._lifecycle_manager.restart_team(team_id)

    def create_terminal(self, name, directory) -> dict:
        return self._lifecycle_manager.create_terminal(name, directory)

    def list_available_teams(self) -> list[dict]:
        return self._lifecycle_manager.list_available_teams()
```

#### Test Requirements

- Existing tests in `test_tmux_service.py` must pass unchanged
- New tests in `test_team_lifecycle_manager.py` for extracted class
- Coverage target: 85%

---

### Work Item 2: TreeBuilder Extraction (BE)

**Owner:** BE
**Estimate:** 1.5h
**Impact:** file_service.py 540 → ~438 lines

#### Analysis

TreeBuilder was specified in Sprint 2 but not extracted. 102 lines.

**Methods to extract from FileService (lines 277-379):**
```python
# From file_service.py
list_directory()    # lines 277-311 (35 lines)
_build_tree()       # lines 313-379 (67 lines)
```

#### New Class: TreeBuilder

**Location:** `backend/app/services/tree_builder.py`

```python
class TreeBuilder:
    """Builds file tree structures for directory listing.

    Extracted from FileService (Sprint 3) to satisfy SRP.
    """

    def __init__(self, path_validator: Callable):
        self._validate_path = path_validator

    def list_directory(
        self,
        project_root: Path,
        path: str = "/",
        depth: int = 1,
        show_hidden: bool = True,
    ) -> TreeResponse

    def _build_tree(
        self,
        project_root: Path,
        directory: Path,
        depth: int,
        show_hidden: bool,
    ) -> list[FileNode]
```

#### FileService Changes

```python
class FileService:
    def __init__(self):
        ...
        # Sprint 3: Delegate tree building to TreeBuilder
        self._tree_builder = TreeBuilder(self._validate_path)

    # Facade method (keep API stable)
    def list_directory(self, project_root, path, depth, show_hidden) -> TreeResponse:
        return self._tree_builder.list_directory(project_root, path, depth, show_hidden)
```

#### Test Requirements

- Existing tests in `test_file_routes.py` must pass unchanged
- New tests in `test_tree_builder.py` for extracted class
- Coverage target: 85%

---

### Work Item 3: Merge Polling into FE Hooks (FE)

**Owner:** FE
**Estimate:** 2h
**Impact:** TmuxController.tsx 534 → ~446 lines

#### Analysis

Two polling effects in TmuxController.tsx should be in their respective hooks:

**3a. Team Activity Polling (lines 188-236) → useTeamState**

Move 48 lines into existing `useTeamState` hook:
- Poll teams every 10 seconds
- Handle token refresh
- Update notifications on activity change

**3b. Role Activity Polling (lines 244-282) → usePanePolling**

Move 38 lines into existing `usePanePolling` hook:
- Poll role activity every 5 seconds
- Handle token refresh
- Update roleActivity state

#### useTeamState Hook Changes

```typescript
export function useTeamState() {
  // ... existing state ...

  // NEW: Team activity polling (moved from TmuxController)
  useEffect(() => {
    const pollTeams = async () => {
      // ... polling logic from TmuxController lines 190-232 ...
    }
    const intervalId = setInterval(pollTeams, 10000)
    return () => clearInterval(intervalId)
  }, [selectedTeam, teamNotifications])

  // ... rest of hook ...
}
```

#### usePanePolling Hook Changes

```typescript
export function usePanePolling({
  selectedTeam,
  selectedRole,
  // ... existing params ...
  onRoleActivityUpdate,  // Already exists
}: UsePanePollingParams) {
  // ... existing state ...

  // NEW: Role activity polling (moved from TmuxController)
  useEffect(() => {
    if (!selectedTeam) return
    const pollActivity = async () => {
      // ... polling logic from TmuxController lines 248-277 ...
    }
    const intervalId = setInterval(pollActivity, 5000)
    return () => clearInterval(intervalId)
  }, [selectedTeam])

  // ... rest of hook ...
}
```

#### Test Requirements

- Existing hook tests must pass
- Add tests for polling behavior in hook test files
- Verify UI still works (team notifications, role activity dots)

---

## MEDIUM PRIORITY Work Items (1.5h)

### Work Item 4: useScrollManager Hook (FE)

**Owner:** FE
**Estimate:** 1h
**Impact:** TmuxController.tsx 446 → ~396 lines

#### Analysis

Scroll management is 50 lines spread across TmuxController.tsx.

**Code to extract (lines 152-176, 285-309):**
- `handleScroll` callback
- `scrollToBottom` callback
- Auto-scroll on role selection effect
- Scroll to highlight effect

#### New Hook: useScrollManager

**Location:** `frontend/hooks/useScrollManager.ts`

```typescript
interface UseScrollManagerParams {
  outputRef: RefObject<HTMLDivElement>
  selectedRole: string | null
  paneStates: Record<string, PaneState>
}

interface UseScrollManagerReturn {
  isAutoScrollEnabled: boolean
  showScrollFab: boolean
  handleScroll: () => void
  scrollToBottom: () => void
}

export function useScrollManager({
  outputRef,
  selectedRole,
  paneStates,
}: UseScrollManagerParams): UseScrollManagerReturn {
  const [isAutoScrollEnabled, setIsAutoScrollEnabled] = useState(true)
  const [showScrollFab, setShowScrollFab] = useState(false)
  const isAutoScrollEnabledRef = useRef(true)

  const handleScroll = useCallback(() => { /* ... */ }, [])
  const scrollToBottom = useCallback(() => { /* ... */ }, [])

  // Auto-scroll on role selection
  useEffect(() => { /* ... */ }, [selectedRole])

  // Scroll to highlight
  useEffect(() => { /* ... */ }, [paneStates, selectedRole, isAutoScrollEnabled])

  return { isAutoScrollEnabled, showScrollFab, handleScroll, scrollToBottom }
}
```

---

### Work Item 5: useAudioFeedback Hook (FE)

**Owner:** FE
**Estimate:** 0.5h
**Impact:** TmuxController.tsx 396 → ~370 lines

#### Analysis

Audio feedback is 25 lines in TmuxController.tsx (lines 401-426).

#### New Hook: useAudioFeedback

**Location:** `frontend/hooks/useAudioFeedback.ts`

```typescript
export function useAudioFeedback() {
  const playBeep = useCallback((isActive: boolean) => {
    try {
      const ctx = new AudioContext()
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.frequency.value = isActive ? 880 : 440  // High = ON, Low = OFF
      gain.gain.value = 0.3
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.start()
      setTimeout(() => { osc.stop(); ctx.close() }, 150)
    } catch (e) {
      console.error("[useAudioFeedback] Error:", e)
    }
  }, [])

  return { playBeep }
}
```

#### TmuxController Changes

```typescript
const { playBeep } = useAudioFeedback()

// In onHeadphoneToggle:
onHeadphoneToggle={async (isActive) => {
  playBeep(isActive)
  // ... rest of handler ...
}}
```

---

## Acceptance Criteria

### Technical Criteria
- [ ] TmuxController.tsx: <400 lines (from 534)
- [ ] tmux_service.py: <400 lines (from 640)
- [ ] file_service.py: <450 lines (from 540)
- [ ] All extracted classes/hooks properly typed
- [ ] No code duplication

### Quality Criteria
- [ ] All tests pass (frontend + backend)
- [ ] Lint passes (frontend)
- [ ] Build passes (frontend)
- [ ] No breaking changes to existing functionality
- [ ] Code coverage maintained or improved

### TDD Criteria (Boss Mandate)
- [ ] Tests written BEFORE refactoring (for new classes/hooks)
- [ ] Tests pass with original code
- [ ] Tests pass after refactoring
- [ ] Progressive commits showing TDD workflow

---

## File Structure After Refactoring

### Backend
```
backend/app/services/
├── team_lifecycle_manager.py  # NEW - Kill/restart/create teams
├── tree_builder.py            # NEW - File tree building
├── tmux_service.py            # REFACTORED - ~395 lines
└── file_service.py            # REFACTORED - ~438 lines

backend/tests/
├── test_team_lifecycle_manager.py  # NEW
└── test_tree_builder.py            # NEW
```

### Frontend
```
frontend/hooks/
├── useTeamState.ts        # UPDATED - Team polling merged
├── usePanePolling.ts      # UPDATED - Role polling merged
├── useScrollManager.ts    # NEW - Scroll management
└── useAudioFeedback.ts    # NEW - Audio feedback

frontend/components/controller/
└── TmuxController.tsx     # REFACTORED - ~370 lines
```

---

## Commit Strategy

### BE Commits (Progressive)
1. `test: add tests for TeamLifecycleManager behavior`
2. `refactor: extract TeamLifecycleManager from TmuxService`
3. `test: add tests for TreeBuilder behavior`
4. `refactor: extract TreeBuilder from FileService`

### FE Commits (Progressive)
1. `refactor: merge team polling into useTeamState`
2. `refactor: merge role polling into usePanePolling`
3. `test: add tests for useScrollManager behavior`
4. `refactor: extract useScrollManager from TmuxController`
5. `refactor: extract useAudioFeedback from TmuxController`

---

## Risk Mitigation

1. **API breakage:** Use facade pattern - TmuxService/FileService keep same public API
2. **State sync issues:** Ensure polling effects have correct dependencies
3. **Audio context issues:** Handle browser restrictions on AudioContext creation
4. **Scroll position loss:** Preserve scroll behavior during extraction

---

## Definition of Done

1. All acceptance criteria met
2. TL code review approved
3. QA blackbox testing passed
4. No regression in existing functionality
5. Line count targets met
