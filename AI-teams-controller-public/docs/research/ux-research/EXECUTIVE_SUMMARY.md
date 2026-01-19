# Executive Summary: Sprint 32 UX Research

**Date**: 2025-12-13  
**Feature**: Team Creator Real-time Status Indicators  
**Status**: Research Complete, Awaiting Approval  

---

## TL;DR

**Problem**: Team Creator has no team context, but Sprint 32 wants real-time tmux status on nodes.

**Solution**: Add Design/Monitor mode toggle. Monitor mode shows live status for selected team.

**Effort**: 13 hours (1.5 sprints)

**Risk**: Low (uses existing APIs, clear UX pattern)

---

## The Problem

Team Creator is a pure design canvas. It works with templates and localStorage configs. There's NO concept of "which tmux team am I working with?"

Meanwhile, Controller tab has team selection (agentic-rag-team, ai_controller_full_team, etc.) and shows live terminal output. But they're separate tabs - no shared state.

Sprint 32 wants to add green/gray status dots to Team Creator nodes based on tmux pane activity. But:

1. **Which team's status?** Creator has no team selector.
2. **How to map nodes to panes?** pm-1 node → PM pane? What about custom nodes?
3. **What about NEW designs?** User creates a team that doesn't exist in tmux yet.

---

## The Solution: Dual Context (Design + Monitor Modes)

Add a mode toggle to Team Creator:

**Design Mode (Default)**:
- Pure canvas for creating team workflows
- No team selection
- No status indicators
- Works offline (localStorage only)
- Use case: "I'm designing a new ML team layout"

**Monitor Mode (Opt-in)**:
- User selects a team from dropdown (ai_controller_full_team, etc.)
- WebSocket connects to tmux
- Status dots appear on nodes (green = active, gray = idle)
- Real-time updates every 5 seconds
- Use case: "I want to see my team's activity visually"

---

## Visual Preview

```
BEFORE (Current):
┌────────────────────────────────────────┐
│ Template: [Full Stack ▼]  [Save] [Load]│
├────────────────────────────────────────┤
│  [PM] → [SA]    (No status dots)      │
│   ↓       ↓                            │
│  [FE] → [BE]                           │
└────────────────────────────────────────┘

AFTER (Design Mode - Default):
┌────────────────────────────────────────┐
│ Mode: [● Design] [  Monitor]           │
│ Template: [Full Stack ▼]  [Save] [Load]│
├────────────────────────────────────────┤
│  [PM] → [SA]    (No status dots)      │
│   ↓       ↓                            │
│  [FE] → [BE]                           │
└────────────────────────────────────────┘

AFTER (Monitor Mode - Selected):
┌────────────────────────────────────────┐
│ Mode: [  Design] [● Monitor]           │
│ Team: [ai_controller_full_team ▼] 🟢  │
├────────────────────────────────────────┤
│  [PM●] → [SA●]  (● = Active green)   │
│   ↓        ↓    (○ = Idle gray)       │
│  [FE○] → [BE●]                        │
└────────────────────────────────────────┘
```

---

## Why This Solution?

**Compared 3 options**:

1. **Shared Global State** (Controller and Creator sync team selection)
   - ❌ Too coupled, can't design new teams

2. **Dual Context** (Design/Monitor toggle) ← RECOMMENDED
   - ✅ Supports all use cases (design new OR monitor existing)
   - ✅ Clear UX (explicit modes)
   - ✅ No coupling between tabs

3. **Auto-Detection** (System detects if nodes match a team)
   - ✅ Zero-config, smart
   - ❌ Complex, unreliable matching
   - ⏸️ Defer to Sprint 33

---

## Implementation Overview

**New Components**:
- Mode toggle button (Design/Monitor)
- Team selector dropdown (Monitor mode only)
- Status dot overlay on nodes
- useTeamStatus hook (WebSocket management)

**API Usage**:
- `GET /api/teams` - Fetch team list for dropdown
- `GET /api/teams/{id}/roles` - Get roles with isActive
- `WebSocket /api/ws/state/{team}/{role}` - Real-time updates

**Files Modified** (estimated 6 files):
- TeamCreatorPanel.tsx (add mode state)
- TeamToolbar.tsx (add mode toggle + team selector)
- types.ts (add paneId to node data)
- useTeamStatus.ts (new hook)
- templates.ts (add paneId mappings)
- RoleNode.tsx (future: custom node with status dot)

**Effort**: 13 hours
- Mode toggle: 2h
- Team selection: 2h
- WebSocket integration: 4h
- Visual indicators: 3h
- Edge cases: 2h

---

## User Personas Supported

1. **Team Designer**: Create new workflows (Design mode, no tmux)
2. **Team Monitor**: Visualize existing team status (Monitor mode)
3. **Hybrid User**: Edit layout while monitoring (both modes)

---

## Acceptance Criteria

- [ ] User can toggle between Design and Monitor modes
- [ ] In Monitor mode, team dropdown appears
- [ ] User can select any tmux team from dropdown
- [ ] Nodes with paneId show green (active) or gray (idle) dots
- [ ] Status updates within 5 seconds
- [ ] WebSocket connects when entering Monitor mode
- [ ] WebSocket disconnects when returning to Design mode
- [ ] Design mode has zero status indicators (pure canvas)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Node-pane mapping unclear | Medium | Document in templates, add tooltips |
| WebSocket performance (6 connections) | Low | Use multiplexed endpoint (optional) |
| User confusion about modes | Low | Clear labels, onboarding tooltip |
| Team not found error | Low | Show friendly error banner |

---

## Next Steps

1. **Review** this research with PM and SA (30 min)
2. **Approval** decision (Sprint 32 or defer?)
3. **Create ADR** if approved (FE task)
4. **Implement** mode toggle + team selector (Sprint 32)
5. **Test** with ai_controller_full_team
6. **Iterate** based on user feedback

---

## Questions for Stakeholders

1. **Default mode**: Should Team Creator open in Design or Monitor mode?
   - Recommendation: Design (most common use case)

2. **Mode persistence**: Should we remember user's last mode in localStorage?
   - Recommendation: Yes (Sprint 33 enhancement)

3. **Node mapping**: Should we provide UI for editing paneId mappings?
   - Recommendation: No (Sprint 32 MVP), JSON-only for now

4. **Multiple teams**: Should Monitor mode support comparing multiple teams?
   - Recommendation: No (defer to Sprint 34)

---

## Documentation Deliverables

**Created**:
1. `sprint-32-realtime-status-proposal.md` (599 lines) - Full research
2. `sprint-32-wireframes.md` (503 lines) - Visual specs
3. `solution-comparison.md` (280 lines) - Quick reference
4. `README.md` (131 lines) - Overview
5. `EXECUTIVE_SUMMARY.md` (this file) - Executive overview

**Total**: 1,513 lines of comprehensive UX research

---

## Recommendation

**APPROVE Solution B for Sprint 32 implementation.**

- ✅ Addresses core UX problem (team context)
- ✅ Supports all user personas
- ✅ Clear, intuitive UI pattern
- ✅ Medium effort (13 hours)
- ✅ Low risk (uses existing APIs)
- ✅ Scalable for future enhancements

**Defer** auto-detection (Solution C) to Sprint 33 as polish.

---

**Contact**: Review WHITEBOARD.md or discuss in ai_controller_full_team tmux session.

