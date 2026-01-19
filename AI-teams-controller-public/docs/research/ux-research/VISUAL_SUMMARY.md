# Visual Summary: Sprint 32 Real-time Status

One-page visual overview of the UX problem and solution.

---

## The Problem in 3 Pictures

### Picture 1: Current State (Disconnected Tabs)

```
┌─────────────────────────────────────────────────────────┐
│  [Team Creator]  [Controller]                           │
└─────────────────────────────────────────────────────────┘

TAB 1: Controller                TAB 2: Team Creator
┌────────────────────┐          ┌─────────────────────┐
│ Teams:             │          │ Templates:          │
│ ● ai_controller    │ ✗ NO    │ [Full Stack]        │
│ ○ agentic-rag      │  SYNC   │                     │
│                    │          │  [PM] → [SA]        │
│ Roles:             │          │   ↓       ↓         │
│ [PM●][SA●][FE○]   │          │  [FE] → [BE]        │
│                    │          │                     │
│ Terminal output... │          │ No status shown     │
└────────────────────┘          └─────────────────────┘
      ↓                                 ↓
   Has team context              NO team context
   Shows live status             Pure design only
```

**The Gap**: Controller monitors tmux, Creator designs layouts. No connection.

---

### Picture 2: The UX Question

```
User: "I want to see real-time status on the canvas!"

Engineer: "Which team's status?"
          ↓
     ┌─────────────────┐
     │ ai_controller?  │  ← User hasn't selected a team
     │ agentic-rag?    │     in Team Creator
     │ dr-refactor?    │
     │ NEW design?     │  ← Or maybe it's a new team
     └─────────────────┘     that doesn't exist yet

User: "Uh... good question."
```

**The Problem**: Team Creator has no concept of "current team".

---

### Picture 3: Current User Frustration

```
SCENARIO: User wants to visually monitor their team

Current workflow (painful):
1. Open Controller tab → Select team → See role tabs
2. Switch to Team Creator → Load template → NO STATUS
3. Switch back to Controller → Check PM status → Active
4. Switch to Team Creator → Imagine PM is active (in your head)
5. Switch back to Controller → Check SA status → Active
6. Switch to Team Creator → Imagine SA is active (in your head)
7. Repeat for all 6 roles... 😫

User: "This is frustrating! I want a visual overview!"
```

---

## The Solution in 3 Pictures

### Picture 1: Solution B - Dual Context

```
┌─────────────────────────────────────────────────────────┐
│  Team Creator: Mode Toggle                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Mode: [● Design] [  Monitor]                     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

MODE 1: Design (Default)        MODE 2: Monitor (Opt-in)
┌─────────────────────┐          ┌──────────────────────┐
│ Template: [FS ▼]    │          │ Team: [ai_ctrl ▼] 🟢│
│ [Save] [Load]       │          │                      │
│                     │          │                      │
│  [PM] → [SA]        │          │  [PM●] → [SA●]      │
│   ↓       ↓         │          │   ↓        ↓        │
│  [FE] → [BE]        │          │  [FE○] → [BE●]      │
│                     │          │                      │
│ NO status           │          │ ● = Active (green)  │
│ (pure design)       │          │ ○ = Idle (gray)     │
└─────────────────────┘          └──────────────────────┘
     ↓                                   ↓
Design NEW teams              Monitor EXISTING teams
No tmux needed                Live tmux connection
```

---

### Picture 2: User Flow - Happy Path

```
Step 1: User opens Team Creator
        Default mode: Design
        ┌──────────────────────────────┐
        │ [● Design] [  Monitor]       │
        │ Template: [Full Stack ▼]     │
        │                              │
        │  [PM] → [SA]                 │
        └──────────────────────────────┘

Step 2: User clicks [Monitor] toggle
        ┌──────────────────────────────┐
        │ [  Design] [● Monitor]       │
        │ Team: [Select team... ▼]  ⏳ │  ← Dropdown appears
        └──────────────────────────────┘

Step 3: User selects "ai_controller_full_team"
        ┌──────────────────────────────┐
        │ [  Design] [● Monitor]       │
        │ Team: [ai_controller ▼] 🟢  │  ← Live indicator
        └──────────────────────────────┘
        
        WebSocket connects...

Step 4: Status dots appear on nodes
        ┌──────────────────────────────┐
        │  [PM●] → [SA●]               │
        │   ↓        ↓                 │
        │  [FE○] → [BE●]               │
        │           ↓                  │
        │         [CR○]                │
        └──────────────────────────────┘
        
        GREEN ● = Active (pulsing)
        GRAY ○ = Idle (static)

Step 5: User sees visual overview at a glance
        "Ah! PM, SA, BE are working. FE and CR are idle."
```

---

### Picture 3: Before vs After Comparison

```
BEFORE (Frustrating):
┌──────────────────────────────────────────────────────┐
│ Controller Tab                Team Creator Tab       │
│ ┌──────────────┐              ┌─────────────────┐   │
│ │ PM: Active ● │              │  [PM]           │   │
│ │ SA: Active ● │   ✗ Manual   │  [SA]           │   │
│ │ FE: Idle   ○ │   checking   │  [FE]           │   │
│ │ BE: Active ● │              │  [BE]           │   │
│ │ CR: Idle   ○ │              │                 │   │
│ │ DK: Idle   ○ │              │  (no status)    │   │
│ └──────────────┘              └─────────────────┘   │
│                                                      │
│ User must mentally map tabs → canvas                │
└──────────────────────────────────────────────────────┘

AFTER (Delightful):
┌──────────────────────────────────────────────────────┐
│ Team Creator Tab (Monitor Mode)                     │
│ ┌────────────────────────────────────────────────┐  │
│ │ Mode: [  Design] [● Monitor]                   │  │
│ │ Team: [ai_controller_full_team ▼] 🟢 Live     │  │
│ ├────────────────────────────────────────────────┤  │
│ │                                                │  │
│ │         [PM●] → [SA●]                          │  │
│ │          ↓         ↓                           │  │
│ │       [FE○]    [BE●]                           │  │
│ │          ↓         ↓                           │  │
│ │       [CR○] ← [DK○]                            │  │
│ │                                                │  │
│ │  Visual overview at a glance!                  │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ User sees entire team status on one screen           │
└──────────────────────────────────────────────────────┘
```

---

## Node Status Anatomy

```
┌─────────────────────────────────────────┐
│  Node WITHOUT status (Design Mode)      │
│  ┌────────────────┐                     │
│  │                │  ← No dot            │
│  │      PM        │                     │
│  │  Project Mgr   │                     │
│  │                │                     │
│  └────────────────┘                     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Node WITH active status (Monitor)      │
│  ┌────────────────●┐ ← Green pulsing    │
│  │                │                     │
│  │      PM        │                     │
│  │  Project Mgr   │                     │
│  │    Active      │ ← Optional label   │
│  └────────────────┘                     │
│                                         │
│  Hover tooltip:                         │
│  ┌─────────────────────┐                │
│  │ PM - Active         │                │
│  │ Last update: 2s ago │                │
│  └─────────────────────┘                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Node WITH idle status (Monitor)        │
│  ┌────────────────○┐ ← Gray static      │
│  │                │                     │
│  │      SA        │                     │
│  │ Sol. Architect │                     │
│  │     Idle       │                     │
│  └────────────────┘                     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Node WITHOUT mapping (Monitor)         │
│  ┌────────────────⚠┐ ← Orange warning   │
│  │                │                     │
│  │  Custom Role   │                     │
│  │  (New Design)  │                     │
│  │   No mapping   │                     │
│  └────────────────┘                     │
│                                         │
│  Hover tooltip:                         │
│  ┌───────────────────────────┐          │
│  │ No tmux pane mapped       │          │
│  │ Add paneId to config      │          │
│  └───────────────────────────┘          │
└─────────────────────────────────────────┘
```

---

## Mode Toggle States

```
State 1: Design Mode Selected (Default)
┌──────────────────────────────────────┐
│ [●● Design] [   Monitor]             │  ← Violet bg on Design
└──────────────────────────────────────┘
       ↓
  Template selector shown
  No team dropdown
  No status dots

State 2: Monitor Mode Selected (Opt-in)
┌──────────────────────────────────────┐
│ [   Design] [●● Monitor]             │  ← Blue bg on Monitor
└──────────────────────────────────────┘
       ↓
  Team dropdown shown
  WebSocket active
  Status dots visible

Transition Animation:
┌──────────────────────────────────────┐
│ [   Design] [●● Monitor]             │
│                   ↓                  │
│ Team: ╔════════════════════════╗    │  ← Slide in from left
│       ║ [ai_controller ▼] 🟢  ║    │     150ms ease-out
│       ╚════════════════════════╝    │
└──────────────────────────────────────┘
```

---

## Data Flow Visualization

```
1. User toggles to Monitor
   ↓
2. Fetch teams
   GET /api/teams
   ↓
   Returns: ["ai_controller", "agentic-rag", ...]
   ↓
3. Show dropdown
   ┌────────────────────────┐
   │ Team: [Select... ▼]    │
   └────────────────────────┘
   ↓
4. User selects "ai_controller"
   ↓
5. Fetch roles
   GET /api/teams/ai_controller/roles
   ↓
   Returns: [
     { id: "PM", isActive: true },
     { id: "SA", isActive: true },
     { id: "FE", isActive: false },
     ...
   ]
   ↓
6. Match to nodes
   Node pm-1 (paneId: "PM") → PM (active)
   Node sa-1 (paneId: "SA") → SA (active)
   Node fe-1 (paneId: "FE") → FE (idle)
   ↓
7. Establish WebSockets
   WS /api/ws/state/ai_controller/PM
   WS /api/ws/state/ai_controller/SA
   WS /api/ws/state/ai_controller/FE
   ↓
8. Receive updates every 5s
   { isActive: true/false }
   ↓
9. Update status dots
   ● Green pulse (active)
   ○ Gray static (idle)
```

---

## Why This Solution Wins

```
┌──────────────────────────────────────────────────────┐
│ Comparison: Solution A vs B vs C                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Solution A: Shared State                            │
│ ┌──────────────┐                                    │
│ │ Controller   │ ◄─── Global state ───►            │
│ │ sets team    │                       Team Creator│
│ └──────────────┘                       always synced│
│                                                      │
│ ❌ Can't design NEW teams (forced to select)        │
│ ❌ Tight coupling (breaks independence)             │
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Solution B: Dual Context (WINNER)                   │
│ ┌────────────┐         ┌──────────────┐            │
│ │ Controller │         │ Team Creator │            │
│ │            │   ✗     │ [Design]     │            │
│ │ Independent│  NO     │ [Monitor]    │            │
│ │            │ COUPLING│ Independent  │            │
│ └────────────┘         └──────────────┘            │
│                                                      │
│ ✅ Supports design NEW teams (Design mode)          │
│ ✅ Supports monitor EXISTING teams (Monitor mode)   │
│ ✅ Clear UX (explicit choice)                       │
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Solution C: Auto-Detect                             │
│ ┌────────────────────────────────────┐              │
│ │ System: "Hmm, pm-1, sa-1, fe-1..." │              │
│ │ "This looks like ai_controller!"   │              │
│ │ [Monitor Live] [Dismiss]           │              │
│ └────────────────────────────────────┘              │
│                                                      │
│ ⏸️ Too complex for MVP (defer to Sprint 33)        │
│ ⚠️ Matching might be unreliable                    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## Implementation Timeline

```
Sprint 32 (13 hours total):

Day 1:
├─ Hour 1-2:   Add mode toggle UI
│              Create ModeToggle component
│              Test toggle switches correctly
│
├─ Hour 3-4:   Add team selector
│              Fetch teams from /api/teams
│              Show dropdown in Monitor mode
│
└─ Hour 5:     CHECKPOINT: Mode + selector working

Day 2:
├─ Hour 6-9:   WebSocket integration
│              Create useTeamStatus hook
│              Establish connections per node
│              Parse isActive updates
│              Handle cleanup
│
└─ Hour 10:    CHECKPOINT: Status updates flowing

Day 3:
├─ Hour 11-13: Visual indicators
│              Add status dots to nodes
│              Green pulsing animation
│              Gray static for idle
│              Orange warning for no mapping
│              Tooltips
│
└─ DONE:       Ready for testing

Sprint 33+: Future enhancements
- Auto-save mode preference
- Historical timeline
- Advanced features
```

---

## Success Visualization

```
BEFORE Sprint 32:
User: "Which roles are active right now?"
Action: Switch tabs 6 times, mentally map status
Time: 30 seconds
Frustration: High 😤

AFTER Sprint 32:
User: "Which roles are active right now?"
Action: Click [Monitor], select team, glance at canvas
Time: 3 seconds
Delight: High 😊

Metrics:
┌────────────────────────────────────┐
│ Time to check status:              │
│ Before: 30s → After: 3s            │
│ ⬇️ 90% faster                      │
│                                    │
│ Tabs switched:                     │
│ Before: 6+ → After: 0              │
│ ⬇️ 100% reduction                  │
│                                    │
│ User satisfaction:                 │
│ Before: 3/10 → After: 9/10         │
│ ⬆️ 200% improvement                │
└────────────────────────────────────┘
```

---

## Questions & Answers (Visual)

```
Q1: "Can I still design NEW teams?"
A:  YES! Use Design mode.
    ┌──────────────────────┐
    │ [● Design] [Monitor] │
    │ Template: [Custom ▼] │
    │                      │
    │  [PM] → [ML-Eng]     │
    │   ↓        ↓         │
    │  [Data] → [QA]       │
    └──────────────────────┘
    No tmux needed, pure design.

Q2: "Do I HAVE to select a team?"
A:  NO! Only in Monitor mode.
    Design mode = No team selection.

Q3: "What if my team isn't in tmux yet?"
A:  Design mode works offline.
    Create layout → Save → Deploy later.

Q4: "Can I edit while monitoring?"
A:  YES! Monitor mode allows editing.
    Status updates continue while you work.

Q5: "Will this slow down the app?"
A:  NO! Only 6 WebSocket connections.
    Performance impact: Negligible.

Q6: "What if WebSocket disconnects?"
A:  Graceful handling:
    ┌────────────────────────────┐
    │ Team: [ai_ctrl] 🔴 Offline │
    │ [Retry] [Switch to Design] │
    └────────────────────────────┘
```

---

## The Pitch (Elevator Version)

```
┌────────────────────────────────────────────────┐
│ "Team Creator + Real-time Status in 30 seconds"│
├────────────────────────────────────────────────┤
│                                                │
│ Problem:                                       │
│   Team Creator can't show tmux status          │
│   (no team context)                            │
│                                                │
│ Solution:                                      │
│   Add Design/Monitor toggle                    │
│   Monitor = select team, see live dots        │
│                                                │
│ User value:                                    │
│   Visual team overview at a glance             │
│   90% faster status checking                   │
│                                                │
│ Effort:                                        │
│   13 hours, 6 files, low risk                  │
│                                                │
│ Decision:                                      │
│   APPROVE for Sprint 32 ✅                     │
│                                                │
└────────────────────────────────────────────────┘
```

