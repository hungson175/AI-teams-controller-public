# Team Hooks

React hooks for team state and lifecycle management.

## useTeamState

Team and role selection with activity polling.

**Location:** `frontend/hooks/useTeamState.ts`

```tsx
const {
  teams,              // Team[] - Available teams
  selectedTeam,       // string | null
  roles,              // Role[] - Roles in selected team
  selectedRole,       // string | null
  teamNotifications,  // Set<string> - Teams with new activity
  roleActivity,       // Record<string, boolean>
  fetchTeams,         // () => Promise<void>
  fetchRoles,         // (teamId) => Promise<void>
  handleSelectTeam,   // (teamId) => void
} = useTeamState()
```

**Features:**
- Auto-fetches teams on mount
- Activity polling every 10 seconds
- Team notification indicators for non-selected teams
- 401 token refresh handling

## usePanePolling

WebSocket pane output streaming.

**Location:** `frontend/hooks/usePanePolling.ts`

```tsx
const {
  paneStates,    // Record<string, PaneState>
  wsConnected,   // boolean
} = usePanePolling({
  selectedTeam,
  selectedRole,
  pollingInterval,  // 0.5 | 1 | 2 seconds
  captureLines,     // Lines to capture
  onRoleActivityUpdate,  // (roleId, isActive) => void
})
```

**Features:**
- WebSocket connection to `/api/ws/state/{team}/{role}`
- Keepalive ping/pong (30s interval)
- Auto-reconnect on disconnect (5s delay)
- Role activity detection

## useTeamLifecycle

Kill, restart, and create team operations.

**Location:** `frontend/hooks/useTeamLifecycle.ts`

```tsx
const {
  isKillingTeam,        // boolean
  restartProgress,      // RestartProgress
  isCreatingTerminal,   // boolean
  handleKillTeam,       // (teamId) => Promise<void>
  handleRestartTeam,    // (teamId) => Promise<void>
  handleCreateTerminal, // (name?, directory?) => Promise<void>
} = useTeamLifecycle({
  teams,
  selectedTeam,
  onTeamListRefresh,
  onTeamSelect,
})
```

**RestartProgress states:**
- `idle` → `killing` → `looking_for_script` → `running_script` → `complete` | `no_script`

## useScrollManager

Auto-scroll behavior management.

**Location:** `frontend/hooks/useScrollManager.ts`

```tsx
const {
  isAutoScrollEnabled,
  showScrollFab,
  handleScroll,
  scrollToBottom,
} = useScrollManager({
  outputRef,
  selectedRole,
})
```

## useAudioFeedback

Audio beep for UI interactions.

**Location:** `frontend/hooks/useAudioFeedback.ts`

```tsx
const { playBeep } = useAudioFeedback()

playBeep(true)   // High beep (880Hz) - ON
playBeep(false)  // Low beep (440Hz) - OFF
```
