# Quick Start Guide: Sprint 32 UX Research

5-minute guide to understanding the Team Creator real-time status feature.

---

## Read This First (2 minutes)

### The Problem
Team Creator is a design canvas with NO team context. Controller monitors tmux teams but they're separate tabs. Sprint 32 wants real-time status dots on canvas nodes, but which team's status?

### The Solution
Add a **mode toggle** to Team Creator:
- **Design Mode** (default): Pure canvas, no team, no status
- **Monitor Mode**: User selects team → See live green/gray status dots

### Why This Matters
Users can now:
1. **Design new teams** (Design mode) without tmux
2. **Monitor existing teams** (Monitor mode) with visual overview
3. **Check status 90% faster** (3s vs 30s)

---

## Visual Overview (1 minute)

### Before
```
Team Creator: [PM] → [SA] → [BE]
              (no status indicators)

User must switch to Controller tab to check status.
```

### After
```
Design Mode (default):
  [PM] → [SA] → [BE]
  (no status, pure design)

Monitor Mode (when needed):
  Team: [ai_controller_full_team ▼] 🟢
  [PM●] → [SA●] → [BE○]
  ● = Active (green)  ○ = Idle (gray)
```

---

## Implementation Overview (1 minute)

**What's being added:**
1. Mode toggle button (Design/Monitor)
2. Team selector dropdown (Monitor mode only)
3. WebSocket connections (Monitor mode only)
4. Status dots on nodes (green/gray/orange)

**Files to modify:** ~6 files  
**Effort:** 13 hours (1.5 sprints)  
**Risk:** Low (uses existing APIs)

---

## Next Steps (1 minute)

### For Decision Makers (PM, SA)
1. Read [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md) (5 min)
2. Decide: Approve or defer Sprint 32?
3. If approved: FE implements

### For Implementers (FE)
1. Read [sprint-32-wireframes.md](./sprint-32-wireframes.md) (15 min)
2. Read [architecture-diagram.md](./architecture-diagram.md) (15 min)
3. Follow implementation checklist

### For Reviewers (CR)
1. Read [VISUAL_SUMMARY.md](./VISUAL_SUMMARY.md) (10 min)
2. Review code against wireframes
3. Test with real tmux team

---

## Key Decisions Made

| Decision | Rationale |
|----------|-----------|
| Mode toggle (not auto-detect) | Clear user control, predictable behavior |
| Monitor mode is opt-in | Preserves Design mode as default use case |
| Multiple WebSockets (not multiplexed) | MVP simplicity, optimize later if needed |
| No node-pane mapping UI | Defer to Sprint 33, JSON config for now |

---

## Success Criteria

- [ ] User can toggle Design/Monitor modes
- [ ] Monitor mode shows team selector
- [ ] Status dots appear (green/gray) in Monitor mode
- [ ] Design mode has ZERO status indicators
- [ ] Status updates within 5 seconds
- [ ] WebSocket cleans up on mode switch

---

## Full Documentation Map

```
START HERE:
  QUICK_START.md (this file) ────────┐
                                     │
EXECUTIVES:                          ▼
  EXECUTIVE_SUMMARY.md ───► Approve or defer?
  VISUAL_SUMMARY.md                  │
                                     │
IMPLEMENTERS:                        ▼
  sprint-32-wireframes.md ───► FE implements
  architecture-diagram.md            │
                                     │
DEEP DIVE:                           ▼
  sprint-32-realtime-status-proposal.md
  solution-comparison.md             │
                                     │
NAVIGATION:                          ▼
  INDEX.md ─────────────────► Find anything
  README.md ─────────────────► Overview
```

---

## Questions? Check These First

**Q: Where's the detailed UX research?**  
A: [sprint-32-realtime-status-proposal.md](./sprint-32-realtime-status-proposal.md)

**Q: How do I implement the UI?**  
A: [sprint-32-wireframes.md](./sprint-32-wireframes.md)

**Q: What are the technical details?**  
A: [architecture-diagram.md](./architecture-diagram.md)

**Q: How does this compare to alternatives?**  
A: [solution-comparison.md](./solution-comparison.md)

**Q: What's the executive summary?**  
A: [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)

**Q: Where's the visual overview?**  
A: [VISUAL_SUMMARY.md](./VISUAL_SUMMARY.md)

---

## Approval Checklist (For PM/SA)

Before approving Sprint 32:

- [ ] Read EXECUTIVE_SUMMARY.md (5 min)
- [ ] Review VISUAL_SUMMARY.md (10 min)
- [ ] Understand the 3 solutions, why B is best
- [ ] Effort estimate (13 hours) is acceptable
- [ ] Risk assessment (low) is acceptable
- [ ] Success criteria are clear
- [ ] Decide: ✅ Approve or ❌ Defer

---

## Implementation Checklist (For FE)

After approval:

**Phase 1: UI (4 hours)**
- [ ] Add mode state to TeamCreatorPanel
- [ ] Create ModeToggle component
- [ ] Create TeamSelector component
- [ ] Test: UI switches correctly

**Phase 2: WebSocket (4 hours)**
- [ ] Create useTeamStatus hook
- [ ] Establish connections in Monitor mode
- [ ] Handle cleanup on mode switch
- [ ] Test: Status updates flow

**Phase 3: Visual (3 hours)**
- [ ] Add status dots to nodes
- [ ] Green pulse animation
- [ ] Gray static for idle
- [ ] Orange warning for no mapping
- [ ] Test: All states render

**Phase 4: Edge Cases (2 hours)**
- [ ] Handle team not found
- [ ] Handle WebSocket errors
- [ ] Loading states
- [ ] Test: Graceful degradation

---

## Contact

**Questions about this research?**  
Review the [INDEX.md](./INDEX.md) for navigation

**Ready to implement?**  
Start with [sprint-32-wireframes.md](./sprint-32-wireframes.md)

**Need approval decision?**  
Read [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)

---

**Total research output:**
- 8 documents
- 3,000+ lines
- 132 KB
- ~8 hours of UX research

**Recommendation:** ✅ Approve for Sprint 32

