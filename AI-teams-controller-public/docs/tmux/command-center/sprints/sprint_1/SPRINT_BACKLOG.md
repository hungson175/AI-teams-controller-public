# Sprint 1 Backlog - UI/UX Polish

**Sprint Goal**: Improve terminal display with responsive width and ANSI color support

**Owner**: Developers (TL, FE, BE, QA) - SM facilitates only
**Created**: 2025-12-29
**Status**: IN PROGRESS

---

## Sprint Items (Pulled from Product Backlog)

### Story 2: Beautiful Terminal Display (ANSI Colors) - DO FIRST
**Priority**: P0
**Assigned**: BE (backend) + FE (frontend)
**Status**: COMPLETE - QA PASSED

**Description**: Render ANSI escape sequences (colors, bold) in terminal output to match real tmux.

**Tasks**:
| Task | Assigned | Status | Notes |
|------|----------|--------|-------|
| Add `-e` flag to tmux capture-pane | BE | DONE | Commit a88c8b4, TL APPROVED |
| Add ansi-to-html dependency | FE | DONE | Commit 25a9798 |
| Create ansi-parser.ts utility | FE | DONE | Commit 25a9798 |
| Update TerminalPanel renderOutput | FE | DONE | Commit 25a9798 |
| Backend tests | BE | DONE | 4 ANSI tests, TL APPROVED |
| Frontend tests | FE | DONE | 19 tests passing |

**Acceptance Criteria** (from TL specs):
- [ ] Terminal shows colors matching real tmux
- [ ] Bold text appears bold
- [ ] 24-bit colors (RGB) render correctly
- [ ] No XSS vulnerabilities from ANSI parsing
- [ ] Text search/highlighting still works with colors
- [ ] Performance acceptable (no lag on large outputs)

**Technical Spec**: `TL_SPECS.md` (same directory)

---

### Story 1: Responsive Tmux Width - DO SECOND
**Priority**: P0
**Assigned**: FE
**Status**: COMPLETE - QA PASSED

**Description**: Recalculate terminal pane width dynamically based on container width to fix line wrapping issues.

**Tasks**:
| Task | Assigned | Status | Notes |
|------|----------|--------|-------|
| Create useTerminalResize hook | FE | DONE | Commit 2c4be1f |
| Update TerminalPanel CSS | FE | DONE | Commit 2c4be1f |
| Hook tests | FE | DONE | 7 tests passing |
| Integration tests | FE | DONE | Commit 2c4be1f |

**Acceptance Criteria** (from TL specs):
- [ ] Lines no longer wrap at 3-4 characters
- [ ] Long lines show horizontal scroll instead of breaking
- [ ] Resize events are debounced (no lag during resize)
- [ ] Terminal output respects natural line breaks from tmux
- [ ] Works on mobile (narrower viewport)

**Technical Spec**: `TL_SPECS.md` (same directory)

---

## Files to Modify

### Story 2 (ANSI Colors)
- `backend/app/services/tmux_service.py` - Add -e flag
- `backend/tests/test_tmux_service.py` - Backend tests
- `frontend/package.json` - Add ansi-to-html
- `frontend/lib/ansi-parser.ts` (NEW)
- `frontend/lib/ansi-parser.test.ts` (NEW)
- `frontend/components/controller/TerminalPanel.tsx`
- `frontend/components/controller/TerminalPanel.test.tsx`

### Story 1 (Responsive Width)
- `frontend/hooks/useTerminalResize.ts` (NEW)
- `frontend/hooks/useTerminalResize.test.ts` (NEW)
- `frontend/components/controller/TerminalPanel.tsx`
- `frontend/components/controller/TerminalPanel.test.tsx`

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All tests pass (`pnpm test`, `pytest`)
- [ ] Code reviewed by TL
- [ ] QA blackbox testing passed
- [ ] Build succeeds (`pnpm build`)
- [ ] Committed to feature branch
- [ ] Ready for PO acceptance

---

## Progress Log

| Date | Update |
|------|--------|
| 2025-12-29 | Sprint Backlog created. Story 2 assigned to BE+FE. |
| 2025-12-29 | BE completed Story 2 backend (commit a88c8b4). TL code review requested. FE proceeding. |
| 2025-12-29 | TL APPROVED BE code review. FE implementing frontend parser. |
| 2025-12-29 | FE completed BOTH stories (commits 25a9798, 2c4be1f). 26 tests. TL review requested. |
| 2025-12-29 | TL APPROVED both FE stories. QA blackbox testing requested. |
| 2025-12-29 | QA PASSED all tests (8/8 Story 2, 5/5 Story 1). SPRINT COMPLETE. Ready for PO acceptance. |
