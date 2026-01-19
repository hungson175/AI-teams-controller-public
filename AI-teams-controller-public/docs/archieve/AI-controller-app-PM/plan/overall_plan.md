# TMUX Team Controller - Overall Plan

**Project**: TMUX Team Controller
**Approach**: Product-Oriented Development (UI-first, progressive implementation)
**Last Updated**: 2024-12-09

---

## Milestones Overview

| Milestone | Goal | Status |
|-----------|------|--------|
| M1 | UI Shell & Components | ✅ COMPLETE |
| M2 | Next.js Mock APIs | ✅ COMPLETE |
| M3 | FastAPI Backend (Mock) | pending |
| M4 | Real tmux Integration | pending |
| M5 | Polish & Deploy | pending |
| Future | Voice Support, Multi-machine | out of scope |

---

## M1: UI Shell & Components

**Goal**: Build complete UI with hardcoded/mock data in components

**Deliverables**:
- Left Panel: Team list (hardcoded teams)
- Right Panel: Role tabs with terminal output area
- Message input box with send button
- Refresh button per tab
- Settings panel for delay configuration
- Responsive layout (mobile-friendly)

**Success Criteria**:
- UI matches frontend specs
- All interactions work with mock data
- No backend calls yet - all data in components

**Notes**:
- Focus on user experience
- Iterate UI until it feels right
- This validates the product direction

---

## M2: Next.js Mock APIs

**Goal**: Move mock data from components to `/api` routes

**APIs to Mock**:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/teams` | GET | List all teams (sessions) |
| `/api/teams/[team]/roles` | GET | List roles (panes) for a team |
| `/api/send/[team]/[role]` | POST | Send message to pane |
| `/api/state/[team]/[role]` | GET | Get pane output |

**Deliverables**:
- All 4 API routes returning mock data
- UI connected to mock APIs
- API contracts documented

**Success Criteria**:
- UI works exactly as before
- Data comes from API routes (not hardcoded)
- API response shapes are stable

**Notes**:
- This becomes our API specification
- No backend needed yet
- Fast iteration on API design

---

## M3: FastAPI Backend (Mock)

**Goal**: Move mock APIs from Next.js to FastAPI backend

**Deliverables**:
- FastAPI project setup
- All 4 endpoints implemented (still mock)
- Next.js proxies to FastAPI
- CORS configured

**Success Criteria**:
- UI works through FastAPI
- Same API contracts preserved
- Backend infrastructure ready

**Notes**:
- Still returning mock data
- Focus on infrastructure, not logic
- Prepares for real implementation

---

## M4: Real tmux Integration

**Goal**: Implement actual tmux communication

**Deliverables**:
- `tmux list-sessions` integration
- `tmux list-panes` integration
- `tm-send` for sending messages (handles two-enter rule)
- `tmux capture-pane` for reading output
- Configurable delay handling

**Success Criteria**:
- App controls real tmux sessions
- Messages sent to actual panes
- Output captured and displayed
- Works with existing tmux teams

**Notes**:
- One API at a time
- Test with real tmux sessions
- Handle edge cases (no sessions, etc.)

---

## M5: Polish & Deploy

**Goal**: Production-ready application

**Deliverables**:
- Error handling
- Loading states
- Edge case handling
- Documentation
- Deployment setup

**Success Criteria**:
- Robust error handling
- Good UX for all states
- Deployable to home server

**Notes**:
- Focus on reliability
- Handle network issues gracefully

---

## Future Scope (Out of v1)

- Voice input/output
- Multi-machine tmux registry
- Role-level automation
- Real-time streaming logs

---

## Sprint Documentation

All sprint-related docs stored in: `docs/tmux/AI-controller-app-PM/plan/sprints/sprint_{number}/`

Each sprint folder contains:
- Sprint goal and scope
- Implementation notes
- Any ADRs (Architecture Decision Records)
- Sprint summary on completion

---

## Pivot Notes

[PM tracks any pivots or changes to the plan here]

- None yet
