# UX Research: Sprint 32 - Team Creator Real-time Status

## Overview

This directory contains comprehensive UX research for implementing real-time status indicators in the Team Creator canvas (Sprint 32).

## Documents

1. **sprint-32-realtime-status-proposal.md** - Main research proposal
   - Current state analysis
   - User personas and use cases
   - 3 proposed solutions with comparative analysis
   - Recommended implementation (Solution B: Dual Context)
   - Technical specifications
   - User testing plan

2. **sprint-32-wireframes.md** - Visual specifications
   - ASCII wireframes for all states
   - Component layouts and spacing
   - Animation specifications
   - Accessibility features
   - Responsive design mockups

## Quick Summary

### The Problem

Team Creator is a pure design canvas with NO team context, while Controller tab has team selection but they're separate tabs. Sprint 32 wants to add real-time tmux status to nodes, but:

- Which team's status should be displayed?
- How do canvas nodes map to tmux panes?
- What about NEW team designs (not in tmux)?

### Recommended Solution

**Solution B: Dual Context with Mode Toggle**

Add two modes to Team Creator:

1. **Design Mode** (default): Pure canvas, no tmux connection, no status indicators
2. **Monitor Mode**: User selects team, WebSocket connects, status dots appear

Benefits:
- Supports all user personas (Designer, Monitor, Hybrid)
- Clear mental model (explicit modes)
- No coupling between tabs
- Medium implementation complexity

### Key Features

```
Design Mode:
[● Design] [  Monitor]  Template: [Full Stack ▼]  [Save] [Load]
↓
Canvas with NO status dots (pure design)

Monitor Mode:
[  Design] [● Monitor]  Team: [ai_controller_full_team ▼] 🟢 Live
↓
Canvas WITH status dots:
  ● Green pulsing = Active pane
  ○ Gray static = Idle pane
```

### Implementation Scope (Sprint 32 MVP)

1. Add mode toggle (Design / Monitor)
2. Add team selector (Monitor mode only)
3. Establish WebSocket connections per node
4. Show status dots (green/gray) on nodes
5. Add paneId field to node data
6. Update templates with default mappings

**Out of scope**: Auto-detection, node-pane mapping UI, historical data

### Acceptance Criteria

- User can toggle between Design and Monitor modes
- In Monitor mode, user can select team from dropdown
- Nodes with matching paneIds show green/gray dots
- WebSocket connects/disconnects when toggling
- Design mode has no status indicators
- Status updates in real-time (5s interval)

## Files Modified (Estimated)

**Frontend**:
- `frontend/components/team-creator/TeamCreatorPanel.tsx` - Add mode state
- `frontend/components/team-creator/controls/TeamToolbar.tsx` - Add mode toggle + team selector
- `frontend/lib/team-creator/types.ts` - Add paneId to RoleNodeData
- `frontend/hooks/useTeamStatus.ts` (new) - WebSocket connections
- `frontend/components/team-creator/nodes/RoleNode.tsx` (future) - Custom node with status dot

**Backend**:
- No changes required (uses existing `/api/teams` and WebSocket endpoints)
- Optional: Add multiplexed WebSocket `/api/ws/team-status/{team_id}` for performance

## Next Steps

1. Review proposal with PM and SA
2. Create ADR if approved
3. FE implements mode toggle + team selector
4. Test with real tmux teams (ai_controller_full_team)
5. Gather user feedback

## Design Principles Applied

1. **Progressive Disclosure**: Default to simple Design mode, reveal Monitor features on demand
2. **Clear Affordances**: Explicit mode toggle (no hidden magic)
3. **Graceful Degradation**: Works without tmux (Design mode)
4. **Real-time Feedback**: Status updates within 5 seconds
5. **Accessibility**: Full keyboard navigation, ARIA labels, screen reader support

## Personas Supported

- **Team Designer**: Create new team workflows (Design mode)
- **Team Monitor**: View existing team status visually (Monitor mode)
- **Hybrid User**: Design while monitoring (both modes)

## Alternatives Considered

- **Solution A (Shared State)**: Sync team selection across tabs - Rejected (too coupled)
- **Solution C (Auto-Detect)**: Smart matching based on node IDs - Deferred (too complex for MVP)

## Contact

For questions about this research:
- Review WHITEBOARD.md for current sprint status
- Consult ADR: `docs/tmux/ai_controller_full_team/plan/sprints/sprint_22_team_creator/adr-team-creator.md`
- Discuss with PM in ai_controller_full_team tmux session

