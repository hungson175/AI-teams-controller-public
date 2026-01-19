# Architecture Diagram: Team Creator Monitor Mode

Visual representation of how Monitor Mode integrates with existing infrastructure.

---

## System Architecture (Current - Before Sprint 32)

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────┐   ┌──────────────────────────┐  │
│  │  Controller Tab       │   │  Team Creator Tab        │  │
│  │  ----------------     │   │  -------------------     │  │
│  │  - Team selector      │   │  - Template selector     │  │
│  │  - Role tabs          │   │  - React Flow canvas     │  │
│  │  - Terminal output    │   │  - Save/Load (localStorage)│
│  │  - WebSocket (single) │   │  - NO tmux connection    │  │
│  └──────────┬────────────┘   └──────────────────────────┘  │
│             │                                                │
│             │ /api/teams                                    │
│             │ /api/teams/{id}/roles                         │
│             │ /ws/state/{team}/{role}                       │
│             │                                                │
└─────────────┼────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  GET  /api/teams                                            │
│  GET  /api/teams/{id}/roles → Returns roles with isActive  │
│  WS   /api/ws/state/{team}/{role} → Real-time pane output  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  tmux sessions  │
              │  -------------  │
              │  - agentic-rag  │
              │  - ai_controller│
              │  - dr-refactor  │
              └─────────────────┘
```

**Key Point**: Controller has tmux integration, Team Creator does NOT.

---

## Proposed Architecture (Sprint 32 - Solution B)

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Frontend (Next.js)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────┐     ┌──────────────────────────────┐    │
│  │  Controller Tab       │     │  Team Creator Tab            │    │
│  │  ----------------     │     │  -------------------         │    │
│  │  - Team selector      │     │  ┌────────────────────────┐ │    │
│  │  - Role tabs          │     │  │ Mode: [Design][Monitor]│ │    │
│  │  - Terminal output    │     │  └────────────────────────┘ │    │
│  │  - WebSocket (single) │     │                              │    │
│  └──────────┬────────────┘     │  IF Design Mode:             │    │
│             │                  │  - Template selector         │    │
│             │                  │  - React Flow canvas         │    │
│             │                  │  - Save/Load (localStorage)  │    │
│             │                  │  - NO tmux connection        │    │
│             │                  │                              │    │
│             │                  │  IF Monitor Mode:            │    │
│             │                  │  - Team selector (NEW)       │    │
│             │                  │  - React Flow canvas         │    │
│             │                  │  - WebSocket (multi) ───┐    │    │
│             │                  │  - Status dots on nodes │    │    │
│             │                  └───────────────────────┬──┘    │    │
│             │                                          │       │    │
└─────────────┼──────────────────────────────────────────┼───────┼────┘
              │                                          │       │
              │ /api/teams                               │       │
              │ /api/teams/{id}/roles                    │       │
              │ /ws/state/{team}/{role}                  │       │
              └──────────────────────────────────────────┘       │
                                                                 │
┌────────────────────────────────────────────────────────────────┼────┐
│                       Backend (FastAPI)                        │    │
├────────────────────────────────────────────────────────────────┼────┤
│  GET  /api/teams ◄──────────────────────────────────────────┐  │    │
│  GET  /api/teams/{id}/roles                                 │  │    │
│  WS   /api/ws/state/{team}/{role} ◄─────────────────────────┼──┘    │
│                                                              │       │
│  Optional (Performance):                                     │       │
│  WS   /api/ws/team-status/{team} (multiplexed) ◄────────────┘       │
│       Returns: { "PM": {isActive}, "SA": {isActive}, ... }          │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  tmux sessions  │
              │  -------------  │
              │  - agentic-rag  │
              │  - ai_controller│
              │  - dr-refactor  │
              └─────────────────┘
```

**Key Change**: Team Creator Monitor Mode connects to same APIs as Controller.

---

## Data Flow: Monitor Mode Activation

```
User clicks [Monitor] mode toggle
           │
           ▼
┌──────────────────────────────────┐
│ 1. Fetch available teams         │
│    GET /api/teams                │
│    → Returns: [                  │
│        {id: "ai_controller_...", │
│         name: "ai_controller"}   │
│      ]                           │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ 2. Show team selector dropdown   │
│    User selects:                 │
│    "ai_controller_full_team"     │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ 3. Fetch team's roles            │
│    GET /api/teams/ai_ctrl.../roles│
│    → Returns: [                  │
│        {id: "PM", isActive: true},│
│        {id: "SA", isActive: true},│
│        {id: "FE", isActive: false}│
│      ]                           │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ 4. Match roles to canvas nodes   │
│    Node pm-1 (paneId: "PM")      │
│      → Role "PM" (isActive: true)│
│                                  │
│    Node sa-1 (paneId: "SA")      │
│      → Role "SA" (isActive: true)│
│                                  │
│    Node fe-1 (paneId: "FE")      │
│      → Role "FE" (isActive: false)│
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ 5. Establish WebSocket per node  │
│    WS /api/ws/state/ai_ctrl../PM │
│    WS /api/ws/state/ai_ctrl../SA │
│    WS /api/ws/state/ai_ctrl../FE │
│    ...                           │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ 6. Receive real-time updates     │
│    Every 5s:                     │
│    { output: "...",              │
│      isActive: true/false }      │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ 7. Update status dots on nodes   │
│    ● Green pulse (isActive: true)│
│    ○ Gray static (isActive: false)│
└──────────────────────────────────┘
```

---

## Component Hierarchy (Team Creator)

```
TeamCreatorPanel (mode state)
    │
    ├─ TeamToolbar
    │   ├─ ModeToggle (Design/Monitor)
    │   ├─ TemplateSelector (Design mode only)
    │   └─ TeamSelector (Monitor mode only) ◄── NEW
    │
    ├─ TeamFlowCanvas
    │   ├─ ReactFlow
    │   │   ├─ Node (default, with inline label)
    │   │   │   └─ StatusDot (Monitor mode only) ◄── NEW
    │   │   └─ Edge (communication edges)
    │   │
    │   ├─ Background
    │   ├─ Controls
    │   └─ MiniMap
    │
    └─ useTeamStatus hook (Monitor mode only) ◄── NEW
        ├─ Establishes WebSocket connections
        ├─ Parses isActive updates
        └─ Manages cleanup on mode switch
```

---

## State Management

```typescript
// TeamCreatorPanel.tsx
type TeamCreatorMode = "design" | "monitor"

interface TeamCreatorState {
  // Existing state
  mode: TeamCreatorMode              // NEW
  nodes: Node[]
  edges: Edge[]
  hasUnsavedChanges: boolean
  
  // Monitor mode state (NEW)
  selectedTeam: string | null        // NEW
  availableTeams: Team[]             // NEW
  roleStatuses: Record<string, {     // NEW
    isActive: boolean
    lastUpdate: string
  }>
}

// State transitions:
// Design → Monitor:  Fetch teams, show selector
// Monitor → Design:  Close WebSockets, clear team
// Team change:       Re-establish all WebSockets
```

---

## WebSocket Management Strategy

### Approach A: Multiple WebSockets (Initial MVP)

```
Canvas with 6 nodes:
  PM  → WS /api/ws/state/team/PM
  SA  → WS /api/ws/state/team/SA
  FE  → WS /api/ws/state/team/FE
  BE  → WS /api/ws/state/team/BE
  CR  → WS /api/ws/state/team/CR
  DK  → WS /api/ws/state/team/DK

Total: 6 concurrent WebSocket connections
```

**Pros**: Simple, uses existing endpoint  
**Cons**: 6 connections per user (acceptable for MVP)

### Approach B: Multiplexed WebSocket (Future Optimization)

```
Canvas with 6 nodes:
  All → Single WS /api/ws/team-status/team
        Returns: {
          "PM": { isActive: true },
          "SA": { isActive: true },
          "FE": { isActive: false },
          ...
        }

Total: 1 WebSocket connection
```

**Pros**: Efficient, single connection  
**Cons**: Requires new backend endpoint (defer to Sprint 33)

**Recommendation**: Start with Approach A, optimize with B if needed.

---

## Error Handling Flow

```
User selects team in Monitor mode
           │
           ▼
    Team not found?
           │
           ├─ YES → Show error banner
           │        "Team 'xyz' not found in tmux"
           │        [Switch to Design Mode]
           │
           └─ NO → Fetch roles
                      │
                      ▼
                 WebSocket fails?
                      │
                      ├─ YES → Show reconnecting indicator
                      │        Gray out all status dots
                      │        Retry connection (3 attempts)
                      │
                      └─ NO → Show live status
                                  │
                                  ▼
                            Node has no paneId?
                                  │
                                  ├─ YES → Show orange warning dot
                                  │        Tooltip: "No pane mapping"
                                  │
                                  └─ NO → Show green/gray status
```

---

## Performance Considerations

### Network Traffic

**Per user in Monitor mode**:
- Initial: 2 HTTP requests (teams, roles)
- Real-time: 6 WebSocket connections
- Update frequency: Every 5 seconds per WebSocket
- Bandwidth: ~500 bytes/update × 6 = 3 KB/5s = 0.6 KB/s

**Verdict**: Negligible network impact

### Memory Footprint

**Additional state per user**:
- Mode: 8 bytes (enum)
- Selected team: 50 bytes (string)
- Available teams: ~500 bytes (array)
- Role statuses: ~300 bytes (6 roles)
- WebSocket instances: ~5 KB (6 connections)

**Total**: ~6 KB additional memory

**Verdict**: Minimal memory impact

### Rendering Performance

**Re-renders triggered by**:
- Mode toggle: Full component (acceptable, one-time)
- Team selection: Full component (acceptable, one-time)
- Status update: Only affected nodes (optimized)

**Optimization**: Use React.memo for individual nodes to prevent cascading re-renders.

---

## Security Considerations

1. **Authentication**: Team selector uses existing JWT auth (no new vulnerabilities)
2. **Authorization**: Backend already validates team access per user
3. **WebSocket Security**: Uses same auth as Controller tab
4. **No new attack surface**: Reuses existing APIs

**Verdict**: No additional security concerns

---

## Accessibility Diagram

```
Keyboard Navigation Flow:

1. Tab → Mode toggle (Design/Monitor)
   │
   ├─ Space → Toggle mode
   │
   └─ Arrow keys → Navigate between modes

2. Tab → Team selector (if Monitor)
   │
   ├─ Space/Enter → Open dropdown
   │
   └─ Arrow keys → Navigate teams

3. Tab → Canvas nodes
   │
   └─ Enter → Focus node (edit mode)

Screen Reader Announcements:

[Monitor mode activated]
  → "Switched to Monitor mode. Select a team to view live status."

[Team selected: ai_controller_full_team]
  → "Monitoring ai_controller_full_team. 4 roles active, 2 idle."

[Status change: PM active → idle]
  → "PM role is now idle."
```

---

## Testing Strategy

### Unit Tests

```
✓ Mode toggle switches between Design/Monitor
✓ Team selector fetches teams correctly
✓ WebSocket establishes on team selection
✓ WebSocket closes on mode switch
✓ Status dots render based on isActive
✓ Nodes without paneId show warning dot
```

### Integration Tests

```
✓ End-to-end: Toggle → Select team → See status
✓ Team not found error displays correctly
✓ WebSocket reconnects on disconnect
✓ Multiple users don't interfere (separate connections)
```

### User Acceptance Tests

```
✓ Designer: Create team in Design mode (no status)
✓ Monitor: View ai_controller_full_team status
✓ Hybrid: Switch between modes without data loss
✓ Error: Handle deleted team gracefully
```

---

## Deployment Plan

1. **Merge to feature branch**: `feature/sprint-32-monitor-mode`
2. **Test locally**: Use ai_controller_full_team (known working team)
3. **Deploy to staging**: Cloudflare tunnel (voice-ui.hungson175.com)
4. **Smoke test**: Verify WebSocket connections work
5. **Merge to main**: After PM approval
6. **Production deploy**: Restart frontend LaunchAgent

**Rollback plan**: Revert commit, restart frontend (< 1 minute downtime)

---

## Future Enhancements Roadmap

### Sprint 33: Polish
- Auto-save mode preference to localStorage
- Historical timeline (last hour of activity)
- Keyboard shortcuts (M = toggle mode, T = team selector)

### Sprint 34: Advanced Features
- "Deploy to tmux" button (create session from canvas)
- Node-pane mapping UI (drag-drop to assign)
- Multi-team comparison view (side-by-side)

### Sprint 35: Analytics
- Team health dashboard (uptime, activity metrics)
- Export status report (PDF/CSV)
- Notification when role becomes active/idle

