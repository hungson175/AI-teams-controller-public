# Tech Debt Sprint 2 - Technical Specification

**Author:** TL
**Date:** 2026-01-11
**Status:** DESIGN COMPLETE

---

## Overview

Sprint 2 addresses component complexity and debug code cleanup from the tech debt evaluation. Total estimated effort: 13h.

**Targets:**
| File | Current | Target | Reduction |
|------|---------|--------|-----------|
| TmuxController.tsx | 913 lines | <500 lines | ~45% |
| tmux_service.py | 693 lines | <400 lines | ~42% |
| file_service.py | 684 lines | <400 lines | ~42% |

---

## CRITICAL: TDD Requirements (Boss Directive)

**Refactoring is HIGH RISK. TDD is NON-NEGOTIABLE.**

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
| **FE-1** | useTeamState hook | `cd frontend && pnpm test` | All existing tests pass | ANY test fails |
| **FE-2** | usePanePolling hook | `cd frontend && pnpm test` | All existing tests pass | ANY test fails |
| **FE-3** | useTeamLifecycle hook | `cd frontend && pnpm test` | All existing tests pass | ANY test fails |
| **FE-4** | Debug cleanup | `cd frontend && pnpm lint && pnpm build` | Lint + build pass | ANY error |
| **BE-1** | ActivityDetector class | `cd backend && uv run python -m pytest` | All tests pass | ANY test fails |
| **BE-2** | MessageTracker class | `cd backend && uv run python -m pytest` | All tests pass | ANY test fails |
| **BE-3** | TmuxRunner utility | `cd backend && uv run python -m pytest` | All tests pass | ANY test fails |
| **BE-4** | TreeBuilder class | `cd backend && uv run python -m pytest` | All tests pass | ANY test fails |
| **BE-5** | ContentIndexer class | `cd backend && uv run python -m pytest` | All tests pass | ANY test fails |
| **BE-6** | Debug cleanup | `cd backend && uv run python -m pytest` | All tests pass | ANY test fails |

### Review Table - TL Checkpoints After Each Extraction

| Checkpoint | After Step | TL Verifies | Pass Criteria |
|------------|------------|-------------|---------------|
| **FE-R1** | useTeamState | Hook interface matches spec, TmuxController imports correctly | Interface matches section 1.1, no TypeScript errors |
| **FE-R2** | usePanePolling | WebSocket logic preserved, pane states work | WS connects, pane content updates |
| **FE-R3** | useTeamLifecycle | Kill/restart/create work via hook | API calls succeed, UI updates |
| **FE-R4** | Debug cleanup | No console.log except BuildVersionLogger | `grep -r "console\." frontend/` shows only allowed |
| **BE-R1** | ActivityDetector | Background polling works, activity flags accurate | Pane activity detection works in UI |
| **BE-R2** | MessageTracker | Highlight text appears for sent messages | Boss messages highlighted in pane |
| **BE-R3** | TmuxRunner | All tmux operations work | send_message, get_pane_state, get_teams work |
| **BE-R4** | TreeBuilder | File tree loads correctly | File browser shows correct tree |
| **BE-R5** | ContentIndexer | File search works | Search returns correct results |
| **BE-R6** | Debug cleanup | No print() or TODO in app/ | `grep` shows no debug code |

### Revert Table - How to Rollback Each Step

| Step | Commit Pattern | Revert Command | Verify After Revert |
|------|----------------|----------------|---------------------|
| **FE-1** | `refactor: extract useTeamState` | `git revert HEAD` | `pnpm test` passes |
| **FE-2** | `refactor: extract usePanePolling` | `git revert HEAD` | `pnpm test` passes |
| **FE-3** | `refactor: extract useTeamLifecycle` | `git revert HEAD` | `pnpm test` passes |
| **FE-4** | `chore: remove console.log` | `git revert HEAD` | `pnpm build` passes |
| **BE-1** | `refactor: extract ActivityDetector` | `git revert HEAD` | `pytest` passes |
| **BE-2** | `refactor: extract MessageTracker` | `git revert HEAD` | `pytest` passes |
| **BE-3** | `refactor: extract TmuxRunner` | `git revert HEAD` | `pytest` passes |
| **BE-4** | `refactor: extract TreeBuilder` | `git revert HEAD` | `pytest` passes |
| **BE-5** | `refactor: extract ContentIndexer` | `git revert HEAD` | `pytest` passes |
| **BE-6** | `chore: resolve TODO markers` | `git revert HEAD` | `pytest` passes |

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

## Work Item 1: TmuxController.tsx Hook Extraction

**Owner:** FE
**Estimate:** 4h
**Current:** 913 lines → **Target:** <500 lines

### Analysis

TmuxController has ~30 useState hooks and ~15 useEffect hooks tightly coupled. State can be grouped into 3 extractable custom hooks:

#### 1.1 Extract `useTeamState` Hook

**Location:** `frontend/hooks/useTeamState.ts`
**Lines saved:** ~150

**State to extract:**
```typescript
// From TmuxController.tsx lines 57-62, 83-84
const [teams, setTeams] = useState<Team[]>([])
const [selectedTeam, setSelectedTeam] = useState<string | null>(null)
const [roles, setRoles] = useState<Role[]>([])
const [selectedRole, setSelectedRole] = useState<string | null>(null)
const [roleActivity, setRoleActivity] = useState<Record<string, boolean>>({})
const [teamNotifications, setTeamNotifications] = useState<Set<string>>(new Set())
const prevTeamActivityRef = useRef<Record<string, boolean>>({})
```

**Functions to extract:**
- `fetchTeams()` (lines 430-460)
- `fetchRoles()` (lines 462-497)
- `handleSelectTeam()` (lines 549-558)
- `handleRoleChange()` (lines 545-547)
- Team polling useEffect (lines 146-193)
- Role activity polling useEffect (lines 202-239)

**Return interface:**
```typescript
interface UseTeamStateReturn {
  teams: Team[]
  selectedTeam: string | null
  roles: Role[]
  selectedRole: string | null
  roleActivity: Record<string, boolean>
  teamNotifications: Set<string>
  selectTeam: (teamId: string) => void
  selectRole: (roleId: string) => void
  refreshTeams: () => Promise<void>
}
```

#### 1.2 Extract `usePanePolling` Hook

**Location:** `frontend/hooks/usePanePolling.ts`
**Lines saved:** ~120

**State to extract:**
```typescript
// From TmuxController.tsx lines 61, 69, 72-73, 87-88
const [paneStates, setPaneStates] = useState<Record<string, PaneState>>({})
const [wsConnected, setWsConnected] = useState(false)
const wsRef = useRef<WebSocket | null>(null)
const pingIntervalRef = useRef<NodeJS.Timeout | null>(null)
const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
```

**Logic to extract:**
- WebSocket connection useEffect (lines 241-375)
- Polling interval update useEffect (lines 377-381)
- Capture lines update useEffect (lines 383-387)
- Visibility change handler useEffect (lines 390-402)

**Return interface:**
```typescript
interface UsePanePollingReturn {
  paneStates: Record<string, PaneState>
  wsConnected: boolean
  currentPaneState: PaneState | null
  updateRoleActivity: (roleId: string, isActive: boolean) => void
}
```

#### 1.3 Extract `useTeamLifecycle` Hook

**Location:** `frontend/hooks/useTeamLifecycle.ts`
**Lines saved:** ~130

**State to extract:**
```typescript
// From TmuxController.tsx lines 79-81
const [isKillingTeam, setIsKillingTeam] = useState(false)
const [restartProgress, setRestartProgress] = useState<RestartProgress>("idle")
const [isCreatingTerminal, setIsCreatingTerminal] = useState(false)
```

**Functions to extract:**
- `handleKillTeam()` (lines 560-605)
- `handleRestartTeam()` (lines 607-669)
- `handleCreateTerminal()` (lines 671-716)
- `handleCreateTeam()` (lines 718-729)
- `handleLoadTeam()` (lines 731-742)

**Return interface:**
```typescript
interface UseTeamLifecycleReturn {
  isKillingTeam: boolean
  restartProgress: RestartProgress
  isCreatingTerminal: boolean
  killTeam: (teamId: string) => Promise<void>
  restartTeam: (teamId: string) => Promise<void>
  createTerminal: (name?: string, directory?: string) => Promise<void>
  createTeam: (teamId: string) => Promise<void>
  loadTeam: (teamName: string) => Promise<void>
}
```

### FE TDD Requirements

**Before refactoring:**
```bash
cd frontend
# Write tests for existing behavior
pnpm test TmuxController.test.tsx
# Tests must pass with current code
```

**Test coverage targets:**
- useTeamState: 80% (business logic)
- usePanePolling: 75% (API integration)
- useTeamLifecycle: 80% (business logic)

**Test file locations:**
- `frontend/__tests__/hooks/useTeamState.test.ts`
- `frontend/__tests__/hooks/usePanePolling.test.ts`
- `frontend/__tests__/hooks/useTeamLifecycle.test.ts`

---

## Work Item 2: tmux_service.py Class Extraction

**Owner:** BE
**Estimate:** 3h
**Current:** 693 lines → **Target:** <400 lines

### Analysis

TmuxService mixes concerns: activity detection, message tracking, team lifecycle. Extract into focused classes.

#### 2.1 Extract `ActivityDetector` Class

**Location:** `backend/app/services/activity_detector.py`
**Lines saved:** ~100

**Methods to extract from TmuxService:**
```python
# From tmux_service.py lines 30-31, 36-86, 230-252
_previous_pane_output: dict[str, str]
_polling_thread: Optional[threading.Thread]
_stop_polling: threading.Event

start_background_polling()      # lines 36-53
stop_background_polling()       # lines 55-60
_poll_all_panes_loop()          # lines 62-75
_poll_all_panes()               # lines 77-86
_get_pane_activity()            # lines 230-252
```

**New class interface:**
```python
class ActivityDetector:
    def __init__(self, tmux_runner: TmuxRunner, poll_interval: int = 5):
        self._previous_pane_output: dict[str, str] = {}
        self._polling_thread: Optional[threading.Thread] = None
        self._stop_polling = threading.Event()

    def start_polling(self, get_teams_fn, get_roles_fn) -> None
    def stop_polling(self) -> None
    def get_activity(self, team_id: str, pane_index: str) -> bool
    def get_last_output(self, key: str) -> Optional[str]
```

#### 2.2 Extract `MessageTracker` Class

**Location:** `backend/app/services/message_tracker.py`
**Lines saved:** ~50

**State to extract:**
```python
# From tmux_service.py line 29, 303-306, 368-371
_sent_messages: dict[str, dict[str, str]]

# Track sent message (in send_message)
key = f"{team_id}-{role_id}"
timestamp = datetime.now().strftime("%H:%M")
self._sent_messages[key] = {"message": message, "timestamp": timestamp}

# Get highlight text (in get_pane_state)
last_message = self._sent_messages.get(key)
highlight_text = f"BOSS [{last_message['timestamp']}]: {last_message['message']}"
```

**New class interface:**
```python
class MessageTracker:
    def __init__(self):
        self._sent_messages: dict[str, dict[str, str]] = {}

    def track_message(self, team_id: str, role_id: str, message: str) -> None
    def get_highlight_text(self, team_id: str, role_id: str) -> Optional[str]
    def clear_message(self, team_id: str, role_id: str) -> None
```

#### 2.3 Extract `TmuxRunner` Utility

**Location:** `backend/app/services/tmux_runner.py`
**Lines saved:** ~30

**Method to extract:**
```python
# From tmux_service.py lines 102-117
def _run_tmux(self, args: list[str]) -> tuple[bool, str]
```

**New utility interface:**
```python
class TmuxRunner:
    @staticmethod
    def run(args: list[str], timeout: int = 5) -> tuple[bool, str]

    @staticmethod
    def capture_pane(target: str, lines: int = 100) -> tuple[bool, str]

    @staticmethod
    def send_keys(target: str, keys: str) -> bool
```

### BE TDD Requirements

**Before refactoring:**
```bash
cd backend
# Write tests for existing behavior
uv run python -m pytest tests/test_tmux_service.py -v
# Tests must pass with current code
```

**Test coverage targets:**
- ActivityDetector: 85% (business logic)
- MessageTracker: 90% (simple state)
- TmuxRunner: 80% (integration)

**Test file locations:**
- `backend/tests/test_activity_detector.py`
- `backend/tests/test_message_tracker.py`
- `backend/tests/test_tmux_runner.py`

---

## Work Item 3: file_service.py Separation

**Owner:** BE
**Estimate:** 3h
**Current:** 684 lines → **Target:** <400 lines

### Analysis

FileService mixes tree building, content indexing, and file validation. Separate concerns.

#### 3.1 Extract `TreeBuilder` Class

**Location:** `backend/app/services/tree_builder.py`
**Lines saved:** ~100

**Methods to extract:**
```python
# From file_service.py lines 421-523
list_directory()    # lines 421-455
_build_tree()       # lines 457-523
```

**New class interface:**
```python
class TreeBuilder:
    def __init__(self, path_validator: PathValidator):
        pass

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

#### 3.2 Extract `ContentIndexer` Class

**Location:** `backend/app/services/content_indexer.py`
**Lines saved:** ~120

**Methods to extract:**
```python
# From file_service.py lines 107-277
_content_cache: dict[str, tuple[datetime, dict[str, str]]]

get_or_build_content_index()    # lines 107-134
invalidate_content_cache()      # lines 136-146
_build_content_index()          # lines 148-216
_parse_gitignore()              # lines 218-248
_matches_gitignore()            # lines 250-277
```

**New class interface:**
```python
class ContentIndexer:
    def __init__(self, cache_ttl: timedelta = timedelta(seconds=300)):
        self._content_cache: dict[str, tuple[datetime, dict[str, str]]] = {}

    def get_or_build_index(self, team_id: str, project_root: Path) -> dict[str, str]
    def invalidate_cache(self, team_id: str) -> None
    def _build_index(self, project_root: Path) -> dict[str, str]
    def _parse_gitignore(self, project_root: Path) -> list[str]
    def _matches_gitignore(self, rel_path: str, patterns: list[str]) -> bool
```

#### 3.3 Keep `PathValidator` in FileService

The path validation methods are small and tightly coupled to file operations. Keep in FileService but clearly group:
- `_validate_path()` (lines 303-352)
- `_is_blacklisted()` (lines 354-378)
- `_is_binary()` (lines 380-407)
- `_get_mime_type()` (lines 409-419)

### BE TDD Requirements

**Before refactoring:**
```bash
cd backend
# Write tests for existing behavior
uv run python -m pytest tests/test_file_service.py -v
# Tests must pass with current code
```

**Test coverage targets:**
- TreeBuilder: 85% (business logic)
- ContentIndexer: 85% (business logic)
- FileService (remaining): 80%

**Test file locations:**
- `backend/tests/test_tree_builder.py`
- `backend/tests/test_content_indexer.py`

---

## Work Item 4: Debug Code Cleanup

**Owner:** FE + BE (split)
**Estimate:** 2.5h total (1.5h FE, 1h BE)

### 4.1 Frontend console.log Removal (FE - 1.5h)

**Files with console.log statements (18 total):**

| File | Count | Action |
|------|-------|--------|
| components/controller/TmuxController.tsx | 22 | Remove or convert to debug flag |
| contexts/VoiceFeedbackContext.tsx | ~5 | Remove |
| hooks/useVoiceRecorder.ts | ~3 | Remove |
| hooks/usePathResolver.ts | ~2 | Remove |
| hooks/useFileListCache.ts | ~2 | Remove |
| hooks/useTeamStatus.ts | ~1 | Remove |
| lib/auth.ts | ~3 | Remove |
| lib/notification-sounds.ts | ~1 | Remove |
| lib/stt/soniox-service.ts | ~2 | Remove |
| lib/stt/audio-capture.ts | ~2 | Remove |
| lib/stt/silence-detector.ts | ~1 | Remove |
| components/voice/VoiceInputToggle.tsx | ~2 | Remove |
| components/controller/HeadphoneButton.tsx | ~1 | Remove |
| contexts/SettingsContext.tsx | ~1 | Remove |
| contexts/AuthContext.tsx | ~1 | Remove |
| app/login/page.tsx | ~1 | Remove |
| components/BuildVersionLogger.tsx | ~1 | Keep (intentional) |

**Approach:**
1. Search: `grep -r "console\." frontend/`
2. Remove all `console.log`, `console.error`, `console.warn`
3. Exception: Keep intentional debug logging with `[DEBUG]` prefix if needed
4. Run lint + build after cleanup

### 4.2 Backend Debug Code (BE - 1h)

**TODO markers found (1 file):**
- `tests/test_template_service.py` - Review and resolve

**Action:** Search for and remove:
```bash
cd backend
grep -rn "TODO\|FIXME\|XXX\|HACK" app/
grep -rn "print(" app/  # Remove debug prints
```

### Cleanup TDD Requirements

**Before cleanup:**
```bash
# FE
cd frontend && pnpm lint && pnpm build

# BE
cd backend && uv run python -m pytest
```

**After cleanup:** Same commands must pass.

---

## Acceptance Criteria

### Technical Criteria
- [ ] TmuxController.tsx: <500 lines (from 913)
- [ ] tmux_service.py: <400 lines (from 693)
- [ ] file_service.py: <400 lines (from 684)
- [ ] All console.log statements removed (except intentional debug)
- [ ] All TODO markers resolved or documented

### Quality Criteria
- [ ] All tests pass (frontend + backend)
- [ ] Lint passes (frontend)
- [ ] Build passes (frontend)
- [ ] No breaking changes to existing functionality
- [ ] Code coverage maintained or improved

### TDD Criteria (Boss Mandate)
- [ ] Tests written BEFORE refactoring
- [ ] Tests pass with original code
- [ ] Tests pass after refactoring
- [ ] Progressive commits showing TDD workflow

---

## File Structure After Refactoring

### Frontend
```
frontend/
├── hooks/
│   ├── useTeamState.ts          # NEW - Team/role selection state
│   ├── usePanePolling.ts        # NEW - WebSocket pane polling
│   ├── useTeamLifecycle.ts      # NEW - Kill/restart/create
│   └── ... (existing hooks)
├── components/controller/
│   └── TmuxController.tsx       # REFACTORED - <500 lines
└── __tests__/hooks/
    ├── useTeamState.test.ts     # NEW
    ├── usePanePolling.test.ts   # NEW
    └── useTeamLifecycle.test.ts # NEW
```

### Backend
```
backend/app/services/
├── activity_detector.py    # NEW - Pane activity detection
├── message_tracker.py      # NEW - Sent message tracking
├── tmux_runner.py          # NEW - Tmux command execution
├── tree_builder.py         # NEW - File tree building
├── content_indexer.py      # NEW - Content indexing
├── tmux_service.py         # REFACTORED - <400 lines
└── file_service.py         # REFACTORED - <400 lines

backend/tests/
├── test_activity_detector.py   # NEW
├── test_message_tracker.py     # NEW
├── test_tmux_runner.py         # NEW
├── test_tree_builder.py        # NEW
└── test_content_indexer.py     # NEW
```

---

## Commit Strategy

### FE Commits (Progressive)
1. `test: add tests for TmuxController team state behavior`
2. `refactor: extract useTeamState hook from TmuxController`
3. `test: add tests for TmuxController pane polling behavior`
4. `refactor: extract usePanePolling hook from TmuxController`
5. `test: add tests for TmuxController team lifecycle behavior`
6. `refactor: extract useTeamLifecycle hook from TmuxController`
7. `chore: remove console.log statements from frontend`

### BE Commits (Progressive)
1. `test: add tests for TmuxService activity detection`
2. `refactor: extract ActivityDetector from TmuxService`
3. `test: add tests for TmuxService message tracking`
4. `refactor: extract MessageTracker from TmuxService`
5. `refactor: extract TmuxRunner utility`
6. `test: add tests for FileService tree building`
7. `refactor: extract TreeBuilder from FileService`
8. `test: add tests for FileService content indexing`
9. `refactor: extract ContentIndexer from FileService`
10. `chore: resolve TODO markers in backend`

---

## Risk Mitigation

1. **Breaking WebSocket connection:** Test reconnection behavior thoroughly
2. **State synchronization issues:** Ensure hooks share state correctly via context if needed
3. **Import cycles:** Use dependency injection pattern for extracted classes
4. **Performance regression:** Profile before/after, especially pane polling

---

## Definition of Done

1. All acceptance criteria met
2. TL code review approved
3. QA blackbox testing passed
4. No regression in existing functionality
5. Documentation updated if needed
