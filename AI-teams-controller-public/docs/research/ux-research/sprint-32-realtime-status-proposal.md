# UX Research Proposal: Team Creator Real-time Status Feature

**Sprint**: 32  
**Feature**: Real-time Status Indicators in Team Creator Canvas  
**Date**: 2025-12-13  
**Researcher**: UX/UI Design Analysis  

---

## Executive Summary

Sprint 32 aims to add real-time tmux pane status indicators (active/idle) to Team Creator canvas nodes. However, a critical UX problem exists: **Team Creator has no team context**, while Controller tab has team selection but they're separate tabs. This proposal analyzes the problem and presents 3 viable solutions with recommendations.

---

## 1. Current State Analysis

### 1.1 Application Architecture

The AI Teams Controller has a two-tab structure at the top level:

```
┌─────────────────────────────────────────────────────────┐
│  [Team Creator] [Controller]                    [Logout]│
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Tab Content (one active at a time)                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Controller Tab** (`/components/controller/TmuxController.tsx`):
- Left sidebar: Team selector (agentic-rag-team, ai_controller_full_team, etc.)
- Main area: Role tabs (PM, SA, FE, BE, CR, DK) with terminal output
- Real-time WebSocket connection: `/api/ws/state/{team_id}/{role_id}`
- Status polling: Background 5-second polling for role activity indicators
- Clear team context: One team selected at a time

**Team Creator Tab** (`/components/team-creator/TeamCreatorPanel.tsx`):
- Left sidebar: Role palette (drag roles - not yet implemented)
- Top toolbar: Template selector, Save, Load, Export buttons
- Canvas area: React Flow with draggable nodes and edges
- Two view modes: "Workflow" (matrix) and "Canvas" (graph)
- NO team context: Pure design canvas
- NO connection to tmux: Works with localStorage configs only

### 1.2 Data Flow

**Controller Tab Data Flow:**
```
User selects team → Fetch /api/teams/{team_id}/roles
                  ↓
         Get roles with isActive field
                  ↓
    User selects role → WebSocket connection
                  ↓
         Real-time pane output + isActive updates
```

**Team Creator Data Flow:**
```
User opens canvas → Load localStorage config OR template
                  ↓
         Nodes/edges with no tmux connection
                  ↓
         User edits → Save to localStorage
```

### 1.3 The Core Problem

**Question 1**: Which team's status should Team Creator display?
- Controller has: `agentic-rag-team`, `ai_controller_full_team`, `dr-refactor-team`, `claude-config`
- Team Creator has: No concept of "current team"

**Question 2**: How do nodes map to tmux panes?
- Controller roles: `{team_id}/{role_id}` (e.g., `ai_controller_full_team/PM`)
- Team Creator nodes: Generic `pm-1`, `sa-1` with no pane mapping

**Question 3**: What about NEW team designs?
- User creates a new team layout that doesn't exist in tmux yet
- Should status indicators be hidden? Grayed out? Show "N/A"?

**Question 4**: State synchronization
- If user switches teams in Controller, should Team Creator auto-update?
- If user edits canvas, do they expect to see live tmux status?

---

## 2. User Personas & Use Cases

### Persona 1: The Team Designer
**Goal**: Design a NEW team workflow from scratch

**Scenario**:
> "I want to create a custom team layout for a Machine Learning project. I need PM, SA, Data Engineer, ML Engineer, and Tester. I don't have a tmux session yet - I'm just designing the workflow."

**Expectation**: 
- Team Creator is a pure design tool
- No status indicators (team doesn't exist yet)
- Focus on workflow structure, not runtime status

### Persona 2: The Team Monitor
**Goal**: Monitor an EXISTING team's real-time status visually

**Scenario**:
> "I have `ai_controller_full_team` running in tmux. I want to see which agents are active right now on a visual canvas instead of just tabs."

**Expectation**:
- Team Creator shows live status for selected team
- Visual overview of entire team at a glance
- Status indicators: green (active) vs. gray (idle)

### Persona 3: The Hybrid User
**Goal**: Design a team based on an existing tmux session

**Scenario**:
> "I want to modify the layout of `agentic-rag-team` by adding a new Documentation role. I want to see the current team's status while I'm designing."

**Expectation**:
- Load existing team from tmux (with mappings)
- Add/remove roles in canvas
- See which roles are currently active
- Export new config for tmux setup

---

## 3. Proposed Solutions

### Solution A: Shared Global Team Context (State Sync)

**Concept**: Team Creator and Controller share a global "selected team" state at the app level.

**Implementation**:
```tsx
// app/page.tsx
const [globalSelectedTeam, setGlobalSelectedTeam] = useState<string | null>(null)

<TabsContent value="team-creator">
  <TeamCreatorPanel selectedTeam={globalSelectedTeam} />
</TabsContent>

<TabsContent value="controller">
  <TmuxController 
    selectedTeam={globalSelectedTeam} 
    onTeamChange={setGlobalSelectedTeam} 
  />
</TabsContent>
```

**User Flow**:
1. User selects team in Controller tab → Updates global state
2. User switches to Team Creator tab → Automatically loads that team's layout
3. Team Creator shows real-time status for globally selected team
4. Switching tabs maintains team context

**Pros**:
- Seamless experience: Team selection persists across tabs
- No duplicate UI: Team selector only in Controller
- Clear mental model: "One team at a time"
- Minimal UI changes

**Cons**:
- Couples two independent modules (tight coupling)
- Cannot design a NEW team while monitoring an EXISTING one
- Forces Team Creator to always have a team context
- Breaks pure "design mode" use case

**Visual Mockup**:
```
Controller Tab (team selected: ai_controller_full_team)
┌─────────────────────────────────────────────────┐
│ Teams:                                          │
│ [●] ai_controller_full_team  ← Selected        │
│ [ ] agentic-rag-team                           │
└─────────────────────────────────────────────────┘

         ↓ (Global state synced)

Team Creator Tab (auto-loaded same team)
┌─────────────────────────────────────────────────┐
│ [Synced with Controller: ai_controller_full_team]│
│                                                 │
│  [PM●]  →  [SA●]         ● = Active (green)    │
│     ↓         ↓          ○ = Idle (gray)       │
│  [FE○]  →  [BE●]                               │
└─────────────────────────────────────────────────┘
```

---

### Solution B: Independent Team Selector in Team Creator (Dual Context)

**Concept**: Team Creator gets its own team selector, completely independent from Controller.

**Implementation**:
```tsx
// TeamCreatorPanel.tsx
const [selectedTeam, setSelectedTeam] = useState<string | null>(null)
const [monitorMode, setMonitorMode] = useState<boolean>(false)

// Top toolbar:
// [Design Mode / Monitor Mode] toggle
// [Team: ai_controller_full_team ▼] (dropdown, only shown in Monitor Mode)
```

**User Flow**:
1. Team Creator has TWO modes:
   - **Design Mode** (default): Pure canvas, no tmux connection
   - **Monitor Mode**: User selects team from dropdown → Shows live status

2. Mode toggle button in toolbar:
   ```
   ┌──────────────────────────────────────┐
   │ [🎨 Design] [📊 Monitor (ai_controller)]│
   │ Template: [Full Stack ▼]  [Save] [Load]│
   └──────────────────────────────────────┘
   ```

3. In Monitor Mode:
   - Team dropdown appears (fetches from `/api/teams`)
   - Canvas loads team's role layout (from tmux or saved config)
   - WebSocket connections established for each node
   - Status indicators show green/gray

4. In Design Mode:
   - No team dropdown
   - No status indicators
   - Pure template/config editing

**Pros**:
- Clear separation of concerns: Design vs. Monitor
- Supports all user personas (Designer, Monitor, Hybrid)
- No coupling between tabs
- Users can monitor one team while designing another (multi-window)

**Cons**:
- Duplicate team selector UI (exists in both tabs)
- More complex UI (mode toggle + conditional dropdown)
- User must explicitly switch modes (extra step)
- Need to handle mode switching edge cases

**Visual Mockup**:
```
DESIGN MODE (No team context):
┌─────────────────────────────────────────────────┐
│ Mode: [🎨 Design] [📊 Monitor]                  │
│ Template: [Full Stack ▼]  [Save] [Load]        │
├─────────────────────────────────────────────────┤
│                                                 │
│  [PM]  →  [SA]         No status indicators    │
│    ↓        ↓          (pure design)           │
│  [FE]  →  [BE]                                 │
└─────────────────────────────────────────────────┘

MONITOR MODE (Team selected: ai_controller_full_team):
┌─────────────────────────────────────────────────┐
│ Mode: [🎨 Design] [📊 Monitor]                  │
│ Team: [ai_controller_full_team ▼] 🟢 Live      │
├─────────────────────────────────────────────────┤
│                                                 │
│  [PM●]  →  [SA●]       ● = Active (green)      │
│     ↓         ↓        ○ = Idle (gray)         │
│  [FE○]  →  [BE●]                               │
└─────────────────────────────────────────────────┘
```

---

### Solution C: Context-Aware Auto-Detection (Intelligent Binding)

**Concept**: Team Creator intelligently detects if canvas matches an existing tmux team, auto-binds if yes.

**Implementation**:
```tsx
// On canvas load:
1. User loads a saved config or template
2. System checks if node IDs match any tmux team:
   - Check `/api/teams` for all teams
   - For each team, get `/api/teams/{id}/roles`
   - Match role IDs to node IDs
3. If match found:
   - Show banner: "Detected team: ai_controller_full_team [Monitor ●] [Ignore]"
   - User can enable monitoring or dismiss
4. If monitoring enabled:
   - Establish WebSocket for each matched node
   - Show status indicators
```

**User Flow**:
1. User opens Team Creator → Loads a template (pm-1, sa-1, fe-1...)
2. System silently checks: "Do these IDs match ai_controller_full_team roles?"
3. If YES:
   ```
   ┌─────────────────────────────────────────────┐
   │ ⚡ This layout matches "ai_controller_full_team" │
   │ [Monitor Live Status] [Dismiss]            │
   └─────────────────────────────────────────────┘
   ```
4. User clicks "Monitor Live Status" → Status dots appear
5. User clicks "Dismiss" → Pure design mode, no distractions

**Pros**:
- Zero-config: Works automatically when applicable
- No UI clutter when designing new teams
- Smart context awareness
- Gentle opt-in (banner notification)

**Cons**:
- Complex matching logic (node IDs must align with role IDs)
- May confuse users ("Why does this sometimes show status?")
- Matching might be unreliable (false positives/negatives)
- Requires strict naming conventions for nodes

**Visual Mockup**:
```
SCENARIO 1: New team design (no match)
┌─────────────────────────────────────────────────┐
│ Template: [Custom Team]  [Save] [Load]         │
├─────────────────────────────────────────────────┤
│  [PM]  →  [ML-Eng]     No status               │
│    ↓          ↓        (doesn't match tmux)    │
│  [Data-Eng]  [QA]                              │
└─────────────────────────────────────────────────┘

SCENARIO 2: Matches ai_controller_full_team
┌─────────────────────────────────────────────────┐
│ ⚡ Detected: "ai_controller_full_team"          │
│ [🟢 Monitor Live] [Dismiss]                     │
├─────────────────────────────────────────────────┤
│  [PM●]  →  [SA●]       (after clicking Monitor)│
│     ↓         ↓                                 │
│  [FE○]  →  [BE●]                               │
└─────────────────────────────────────────────────┘
```

---

## 4. Comparative Analysis

| Criteria                     | Solution A (Shared State) | Solution B (Dual Context) | Solution C (Auto-Detect) |
|------------------------------|---------------------------|---------------------------|-------------------------|
| **Design new teams**         | ❌ Forced to select team   | ✅ Clean design mode      | ✅ Works seamlessly     |
| **Monitor existing teams**   | ✅ Auto-synced            | ✅ Explicit monitor mode  | ✅ Opt-in monitoring    |
| **UI complexity**            | ✅ Minimal                | ⚠️ Mode toggle required  | ✅ Smart, contextual    |
| **Implementation effort**    | ✅ Low (global state)     | ⚠️ Medium (new UI)       | ❌ High (matching logic)|
| **Tab independence**         | ❌ Tightly coupled        | ✅ Fully independent     | ✅ Independent          |
| **User confusion**           | ⚠️ "Why can't I design?"  | ✅ Clear modes           | ⚠️ "Why auto-detect?"  |
| **Multi-window support**     | ❌ Shared state conflicts | ✅ Each tab independent  | ✅ Works well           |
| **Node-pane mapping**        | ⚠️ Needs manual config    | ⚠️ Needs manual config   | ✅ Auto-detected        |
| **Supports ALL personas**    | ❌ Only Monitor          | ✅ All 3 personas        | ✅ All 3 personas       |

---

## 5. Recommended Solution

### Primary Recommendation: Solution B (Dual Context with Mode Toggle)

**Rationale**:
1. **Supports All Use Cases**: Handles Designer, Monitor, and Hybrid personas equally well
2. **Clear Mental Model**: Explicit modes prevent confusion ("Am I designing or monitoring?")
3. **Preserves Independence**: Team Creator remains usable without tmux
4. **Scalable**: Easy to add features (e.g., "Deploy to tmux" button in Design mode)
5. **Production-Ready**: Medium complexity but well-defined behavior

**Implementation Plan**:

```typescript
// 1. Add mode state to TeamCreatorPanel.tsx
type TeamCreatorMode = "design" | "monitor"
const [mode, setMode] = useState<TeamCreatorMode>("design")
const [monitoredTeam, setMonitoredTeam] = useState<string | null>(null)

// 2. Update toolbar to show mode toggle
<div className="toolbar">
  <ToggleGroup type="single" value={mode} onValueChange={setMode}>
    <ToggleGroupItem value="design">🎨 Design</ToggleGroupItem>
    <ToggleGroupItem value="monitor">📊 Monitor</ToggleGroupItem>
  </ToggleGroup>
  
  {mode === "monitor" && (
    <TeamSelector 
      teams={teams} 
      selected={monitoredTeam} 
      onChange={setMonitoredTeam} 
    />
  )}
</div>

// 3. Conditional WebSocket connections
{mode === "monitor" && monitoredTeam && (
  <StatusOverlay nodes={nodes} teamId={monitoredTeam} />
)}
```

**UI Specifications**:

**Mode Toggle Button Group**:
- Location: Top toolbar, left side
- Style: Segmented control (similar to "Workflow/Canvas" toggle)
- States:
  - Design: No live connection icon
  - Monitor: Green dot indicator when WebSocket connected

**Team Selector (Monitor Mode Only)**:
- Location: Top toolbar, right of mode toggle
- Component: Dropdown menu (shadcn/ui `Select`)
- Content: Fetch from `/api/teams`, show team names
- Visual feedback: Loading spinner, empty state ("No teams")

**Status Indicators on Nodes**:
- Location: Top-right corner of each node
- Visual:
  - Active: Green pulsing dot (h-3 w-3, bg-green-500, animate-pulse)
  - Idle: Gray static dot (h-3 w-3, bg-gray-400)
  - No mapping: No dot
- Tooltip: "Active: Last update 2s ago" / "Idle: No activity"

**Node-Pane Mapping Config**:
```typescript
// Add to node data:
interface RoleNodeData {
  role: RoleType
  label: string
  status: RoleStatus
  paneId?: string  // e.g., "PM", "SA", "FE"
  tmuxMapping?: {  // Optional: Explicit mapping
    teamPattern: string  // Regex or exact match
    roleId: string
  }
}

// In Monitor mode, match nodes to roles:
// 1. Try explicit tmuxMapping first
// 2. Fall back to role-based matching (PM node → PM pane)
// 3. Show warning if ambiguous
```

---

### Alternative Recommendation: Solution C (If time permits)

If implementation resources allow, **Solution C (Auto-Detection)** provides the best user experience:
- Zero-config monitoring
- No mode switching overhead
- Smart contextual behavior

However, defer this to a later sprint due to complexity.

---

## 6. Sprint 32 Implementation Scope

**RECOMMENDED SCOPE** (Solution B - MVP):

1. **Add mode toggle** (Design / Monitor)
2. **Add team selector** (Monitor mode only)
3. **Establish WebSocket connections** per node in Monitor mode
4. **Show status dots** (green/gray) on nodes
5. **Add paneId field** to node data schema
6. **Update templates** with default paneId mappings

**OUT OF SCOPE** (Defer to Sprint 33):
- Auto-detection logic (Solution C)
- Node-pane mapping UI (let users edit in JSON for now)
- Multi-team monitoring (parallel WebSockets)
- Historical status data (trend graphs)

**Acceptance Criteria**:
```
✅ User can toggle between Design and Monitor modes
✅ In Monitor mode, user can select a team from dropdown
✅ Nodes with matching paneIds show green (active) or gray (idle) dots
✅ WebSocket connects/disconnects when toggling modes
✅ Design mode has no status indicators (pure canvas)
✅ Status updates in real-time (5s polling interval)
```

---

## 7. Visual Design Specifications

### Color Palette
```css
/* Status Indicators */
--status-active: #22c55e;      /* green-500 */
--status-idle: #9ca3af;        /* gray-400 */
--status-error: #ef4444;       /* red-500 */
--status-no-mapping: transparent;

/* Mode Toggle */
--mode-design: #8b5cf6;        /* violet-500 */
--mode-monitor: #3b82f6;       /* blue-500 */
```

### Typography
- Mode labels: 14px, medium weight
- Team selector: 13px, regular weight
- Status tooltips: 12px, mono font

### Spacing
- Toolbar height: 44px (consistent with existing)
- Mode toggle padding: 8px 16px
- Team selector min-width: 200px
- Status dot size: 12px × 12px

### Animations
```css
@keyframes pulse-active {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.status-dot-active {
  animation: pulse-active 2s ease-in-out infinite;
}
```

---

## 8. Technical Considerations

### Performance
- **Problem**: WebSocket connections per node (6 nodes = 6 WebSockets)
- **Solution**: Use single WebSocket with multiplexing:
  ```typescript
  // ws://backend/api/ws/team-status/{team_id}
  // Returns: { "PM": { isActive: true }, "SA": { isActive: false }, ... }
  ```

### Error Handling
- **Team not found**: Show warning banner "Team 'xyz' not found in tmux"
- **WebSocket disconnect**: Gray out all dots, show "Reconnecting..." toast
- **Node-pane mismatch**: Show orange dot with tooltip "No pane mapping"

### Accessibility
- ARIA labels: "Toggle to monitor mode", "Select team to monitor"
- Keyboard navigation: Tab through mode toggle, team selector
- Screen reader: Announce status changes ("PM role is now active")

---

## 9. User Testing Plan

**Test Scenarios**:

1. **Designer Persona**:
   - Open Team Creator → Should default to Design mode
   - Create custom team → Should NOT see status dots
   - Save config → Should work without team selection

2. **Monitor Persona**:
   - Switch to Monitor mode → Team selector appears
   - Select `ai_controller_full_team` → Status dots appear
   - Run tmux command to trigger activity → Dots turn green within 5s

3. **Hybrid Persona**:
   - Load template → Switch to Monitor → Select team
   - Edit canvas while monitoring → Status updates continue
   - Add new node → Should NOT have status (no pane mapping)

**Success Metrics**:
- 100% of users understand Design vs. Monitor modes
- 0 confusion about "which team is this?"
- Status updates reflect reality within 5 seconds

---

## 10. Conclusion

The core UX problem is **context mismatch**: Team Creator is a design tool, while status monitoring requires team context. 

**Recommended Solution B** balances:
- ✅ User flexibility (design OR monitor)
- ✅ Clear mental model (explicit modes)
- ✅ Technical feasibility (medium effort)
- ✅ Future extensibility (add features per mode)

**Next Steps**:
1. Review this proposal with PM and SA
2. Create ADR if approved
3. FE implements mode toggle + team selector
4. BE adds multiplexed WebSocket endpoint (optional optimization)
5. Test with real tmux teams

---

**Appendix A: Alternative Naming Ideas**
- Instead of "Design / Monitor", consider:
  - "Edit / Live"
  - "Draft / Watch"
  - "Offline / Online"
  
Prefer "Design / Monitor" for clarity.

**Appendix B: Future Enhancements**
- Sprint 33: Auto-save mode preference to localStorage
- Sprint 34: "Deploy to tmux" button (creates session from canvas)
- Sprint 35: Historical timeline (show activity over last hour)

