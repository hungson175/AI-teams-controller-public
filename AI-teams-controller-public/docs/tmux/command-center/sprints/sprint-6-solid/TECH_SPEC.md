# Sprint 6 - SOLID Principles Refactoring

**Author:** TL | **Date:** 2026-01-12 | **Status:** READY FOR REVIEW

---

## Overview

Refactor codebase to address SOLID principle violations. Focus: HIGH severity items that improve maintainability and testability.

**Total Estimated Effort:** 8h | **TDD Required:** Yes

---

## HIGH Severity Violations (Fix This Sprint)

### Backend (BE - 3h)

| # | File | Violation | Fix |
|---|------|-----------|-----|
| 1 | routes.py:189 | **DIP** - Direct attribute mutation `service.capture_lines = x` | Add `set_capture_lines()` method to TeamService |
| 2 | TmuxService | **SRP** - 9 methods mixing pane state, lifecycle, detection | Extract PaneStateService (get/send) from lifecycle ops |
| 3 | TTSProviderFactory | **OCP** - Hardcoded google/openai checks despite registry | Remove legacy fallback, use registry only |

### Frontend (FE - 5h)

| # | File | Violation | Fix |
|---|------|-----------|-----|
| 4 | TeamSidebar.tsx | **ISP** - 18+ props, many unused | Split into TeamListSidebar, SettingsSidebar |
| 5 | useTeamState.ts | **DIP** - Direct API endpoint coupling | Extract TeamApiService interface |
| 6 | usePanePolling.ts | **DIP** - Direct `new WebSocket()` | Accept wsFactory param for testability |
| 7 | VoiceFeedbackContext | **SRP** - WS + audio in one context | Split: VoiceWebSocketContext, VoiceAudioContext |

---

## Work Items

### Work Item 1: Backend DIP/SRP Fixes (BE - 3h)

**1.1 routes.py - Fix DIP violation**
```python
# BEFORE (line 189)
service.capture_lines = capture_lines

# AFTER - Use method
service.set_capture_lines(capture_lines)
```

**1.2 TmuxService - Extract PaneStateService**
- Move: `get_pane_state()`, `send_message()` → PaneStateService
- Keep: lifecycle methods in TmuxService
- Inject PaneStateService into routes

**1.3 TTSProviderFactory - Remove legacy fallback**
- Delete hardcoded google/openai checks (lines 121-143)
- Use registry.get() only

### Work Item 2: Frontend ISP/DIP Fixes (FE - 5h)

**2.1 TeamSidebar.tsx - Split by concern**
- TeamListSidebar: teams[], selectedTeam, onTeamSelect
- SettingsSidebar: settings props only
- Pass focused prop objects, not 18+ individual props

**2.2 useTeamState.ts - Extract API service**
```typescript
// Create: lib/services/teamApi.ts
interface TeamApiService {
  getTeams(): Promise<Team[]>
  getRoles(teamId: string): Promise<Role[]>
}
```

**2.3 usePanePolling.ts - Inject WebSocket factory**
```typescript
// Accept factory for testability
interface UsePanePollingParams {
  wsFactory?: (url: string) => WebSocket  // Default: new WebSocket
}
```

**2.4 VoiceFeedbackContext - Split contexts**
- VoiceWebSocketContext: connection, messaging
- VoiceAudioContext: playback, tone, notifications

---

## TDD Requirements

| Step | Test First | Then Implement |
|------|------------|----------------|
| BE-1 | Test set_capture_lines() method | Add method to TeamService |
| BE-2 | Test PaneStateService isolation | Extract from TmuxService |
| FE-1 | Test TeamListSidebar props | Split TeamSidebar |
| FE-2 | Test TeamApiService interface | Extract from useTeamState |
| FE-3 | Test wsFactory injection | Add param to usePanePolling |

---

## Acceptance Criteria

- [ ] All HIGH severity violations fixed
- [ ] All existing tests pass (backend 100+, frontend E2E 16/16)
- [ ] New tests for extracted services/components
- [ ] Build passes, no type errors
- [ ] No breaking changes to existing functionality

---

## Code Coverage

**Backend:** 80% minimum | **Frontend:** 70% minimum
