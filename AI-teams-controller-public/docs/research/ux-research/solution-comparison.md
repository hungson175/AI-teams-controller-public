# Solution Comparison: Quick Reference

## Problem Statement

Team Creator (design canvas) + Controller (tmux monitor) = Separate tabs with NO shared context.

Sprint 32 wants: **Real-time status dots on Team Creator nodes**

But: **Which team? How to map nodes to panes?**

---

## Three Solutions at a Glance

### Solution A: Shared Global State

```
┌─────────────────────────────────────────────┐
│         Global App State                    │
│   selectedTeam: "ai_controller_full_team"   │
└──────────┬──────────────────────┬───────────┘
           │                      │
    ┌──────▼──────┐      ┌────────▼────────┐
    │ Controller  │      │ Team Creator    │
    │ (sets team) │      │ (syncs team)    │
    └─────────────┘      └─────────────────┘
```

**Pros**: Simple, auto-synced  
**Cons**: Tight coupling, can't design new teams  
**Verdict**: ❌ Too limiting

---

### Solution B: Dual Context (RECOMMENDED)

```
┌─────────────────┐         ┌──────────────────┐
│  Controller     │         │  Team Creator    │
│  ┌───────────┐  │         │  ┌────────────┐  │
│  │ Team:     │  │         │  │ Mode:      │  │
│  │ ai_ctrl.. │  │         │  │ [Design]   │  │
│  └───────────┘  │         │  │ [Monitor]  │  │
│                 │         │  └────────────┘  │
│  Independent    │         │  ┌────────────┐  │
│                 │         │  │ Team:      │  │
│                 │         │  │ (if Monitor)│  │
│                 │         │  └────────────┘  │
└─────────────────┘         └──────────────────┘
    No coupling                  Independent
```

**Design Mode**: No team, no status, pure canvas  
**Monitor Mode**: Select team → Live status dots

**Pros**: Flexible, supports all personas, clear UX  
**Cons**: Mode toggle UI, medium complexity  
**Verdict**: ✅ BEST BALANCE

---

### Solution C: Auto-Detection

```
User loads template
       ↓
   [pm-1, sa-1, fe-1, be-1]
       ↓
System checks: "Do these match any tmux team?"
       ↓
┌──────────────────────────────────────┐
│ ⚡ Detected: ai_controller_full_team │
│ [Monitor Live] [Dismiss]            │
└──────────────────────────────────────┘
```

**Pros**: Zero-config, smart UX  
**Cons**: Complex matching, unreliable  
**Verdict**: ⏸️ Defer to Sprint 33

---

## Recommended Implementation (Solution B)

### User Flow

```
1. User opens Team Creator → Default: Design Mode
   [Canvas with no status dots]

2. User toggles to Monitor Mode
   → Team dropdown appears
   
3. User selects "ai_controller_full_team"
   → WebSocket connects
   → Status dots appear (● green / ○ gray)

4. User toggles back to Design Mode
   → Status dots disappear
   → WebSocket disconnects
```

### UI Components

```
┌──────────────────────────────────────────────┐
│ Mode: [● Design] [  Monitor]                 │
│       └─ Default                             │
│                                              │
│ Template: [Full Stack ▼]  [Save] [Load]     │
└──────────────────────────────────────────────┘

         ↓ (User clicks Monitor)

┌──────────────────────────────────────────────┐
│ Mode: [  Design] [● Monitor]                 │
│                                              │
│ Team: [ai_controller_full_team ▼]  🟢 Live  │
│       └─ NEW: Appears in Monitor mode       │
└──────────────────────────────────────────────┘
```

### Node Status Visualization

```
Design Mode:              Monitor Mode:
┌────────┐                ┌────────●┐  ← Green pulse
│   PM   │                │   PM   │     (active)
└────────┘                └────────┘

┌────────┐                ┌────────○┐  ← Gray static
│   SA   │                │   SA   │     (idle)
└────────┘                └────────┘

No dots                   Live status
```

---

## Data Flow (Solution B - Monitor Mode)

```
1. User selects team in dropdown
   ↓
2. Fetch /api/teams/{team_id}/roles
   → Returns: [{ id: "PM", isActive: true }, ...]
   ↓
3. Match roles to canvas nodes by paneId
   PM node (paneId: "PM") → PM role
   ↓
4. Establish WebSocket /api/ws/state/{team}/{role}
   (One per node with paneId)
   ↓
5. Receive updates every 5s:
   { isActive: true } → Show green dot
   { isActive: false } → Show gray dot
   ↓
6. User toggles to Design Mode
   → Close all WebSockets
   → Remove status dots
```

---

## Implementation Checklist

**Phase 1: Mode Toggle (2 hours)**
- [ ] Add mode state to TeamCreatorPanel
- [ ] Create mode toggle button group
- [ ] Show/hide team selector based on mode
- [ ] Test: Toggle switches correctly

**Phase 2: Team Selection (2 hours)**
- [ ] Create TeamSelector dropdown component
- [ ] Fetch teams from /api/teams
- [ ] Store selected team in state
- [ ] Test: Dropdown shows all teams

**Phase 3: WebSocket Integration (4 hours)**
- [ ] Create useTeamStatus hook
- [ ] Establish WebSocket per node (when paneId exists)
- [ ] Handle connect/disconnect lifecycle
- [ ] Parse isActive from WebSocket messages
- [ ] Test: Status updates in real-time

**Phase 4: Visual Indicators (3 hours)**
- [ ] Add status dots to node rendering
- [ ] Green pulsing animation for active
- [ ] Gray static for idle
- [ ] Orange warning for no mapping
- [ ] Tooltips with status details
- [ ] Test: All states visible

**Phase 5: Edge Cases (2 hours)**
- [ ] Handle team not found
- [ ] Handle WebSocket errors
- [ ] Handle nodes without paneId
- [ ] Loading states (spinner)
- [ ] Test: Graceful degradation

**Total Estimate**: 13 hours (1.5 sprints)

---

## Success Metrics

1. **Functionality**
   - ✅ User can switch between Design/Monitor modes
   - ✅ Status dots appear only in Monitor mode
   - ✅ Status updates within 5 seconds
   - ✅ WebSocket cleans up on mode switch

2. **User Experience**
   - ✅ 100% of users understand mode difference
   - ✅ 0 confusion about team context
   - ✅ Status indicators are visually clear

3. **Performance**
   - ✅ Mode toggle < 100ms
   - ✅ WebSocket connects < 500ms
   - ✅ No memory leaks (cleanup verified)

---

## Future Enhancements (Post-Sprint 32)

**Sprint 33**:
- Auto-save mode preference to localStorage
- Historical status timeline (last hour)
- Multi-team comparison view

**Sprint 34**:
- "Deploy to tmux" button (create session from canvas)
- Auto-detection (Solution C)
- Advanced node-pane mapping UI

**Sprint 35**:
- Team health dashboard
- Notification when role becomes active/idle
- Export status report (PDF/CSV)

