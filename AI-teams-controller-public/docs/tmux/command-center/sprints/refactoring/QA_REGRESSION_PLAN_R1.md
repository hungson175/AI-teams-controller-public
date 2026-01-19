# QA Regression Test Plan - Sprint R1

**Sprint Goal:** Verify NO functional regressions after file splitting refactoring
**Testing Approach:** Blackbox browser-based testing at localhost:3334
**Date:** 2026-01-19
**QA Role:** Blackbox testing only (no code inspection)

---

## Testing Strategy (Based on Recalled Memories)

### Memory-Driven Approach

This plan incorporates 5 critical lessons from past sprints:

1. **Establish Baseline Before Refactoring** - Document expected outputs before splits
2. **True Blackbox Testing** - Browser automation only, no code access
3. **Full Test Suite Verification** - Run complete test suites, not just story-specific
4. **Smoke Test First** - Verify app loads before feature testing
5. **Entry Point Verification** - Confirm all old imports replaced with new files

---

## Phase 4 Testing Gates

### Gate 1: Smoke Test (CRITICAL - Run First)

**Purpose:** Catch integration breaks that unit tests miss

| Check | Expected Result | PASS/FAIL |
|-------|-----------------|-----------|
| Backend starts successfully | `uvicorn app.main:app --port 17061` runs without errors | |
| Frontend builds | `pnpm build` completes successfully | |
| Frontend serves | `PORT=3334 pnpm start` runs without errors | |
| App loads in browser | http://localhost:3334 loads (not stuck on loading screen) | |
| Basic interaction works | Click team selector, see response | |

**BLOCKER:** If ANY smoke test fails, report to SM immediately. Do NOT proceed to feature testing.

---

### Gate 2: Entry Point Verification

**Purpose:** Prevent "new files created but not integrated" anti-pattern

**Files Refactored (8 total):**

**Backend (5 files):**
1. `tree_routes.py` → `tree_ops.py` + `crud_ops.py`
2. `template_service.py` → Extract `TemplateGenerator`
3. `command_routes.py` → Extract `CommandProcessor`
4. `file_service.py` → Extract `FileValidator` + `PathResolver`
5. `tts_providers.py` → `base.py` + `google_tts.py` + `hdtts.py`

**Frontend (3 files):**
1. `TerminalPanel.tsx` → Extract `AutocompleteDropdown` + `CommandHistory`
2. `useVoiceRecorder.ts` → Extract `useAudioManager` + `useWakeLockManager`
3. `TeamSidebar.tsx` → Extract `TeamSettings` + `TeamActions`

**Verification Method:** FE/BE should run grep to verify old imports replaced

---

### Gate 3: Full Test Suite

**Purpose:** Catch regressions in dependent modules

```bash
# Backend - Run complete test suite
cd backend
uv run pytest --cov=app --cov-report=term-missing

# Frontend - Run complete test suite
cd frontend
pnpm test -- --coverage

# Expected: ALL tests passing (no new failures from refactoring)
```

**BLOCKER:** If tests fail, report to SM. Do NOT proceed until all tests pass.

---

### Gate 4: Comprehensive Browser-Based Regression Testing

**Purpose:** Validate ALL existing functionality from user perspective

---

## Browser Test Categories

### A. Team Management

| Test Case | Steps | Expected Result | PASS/FAIL |
|-----------|-------|-----------------|-----------|
| TC-A1: List teams | 1. Open http://localhost:3334<br/>2. Check team selector | Teams dropdown shows available tmux sessions | |
| TC-A2: Select team | 1. Click team dropdown<br/>2. Select "command-center" | Team switches, roles load in tabs | |
| TC-A3: View role tabs | 1. After team selected<br/>2. Check role tabs | Tabs show: PO, SM, TL, FE, BE, QA | |
| TC-A4: Switch roles | 1. Click "FE" tab | Terminal output switches to FE pane | |
| TC-A5: Activity indicators | 1. Observe role tabs<br/>2. Check for activity dots | Active roles show green dot, idle show gray | |

---

### B. Terminal Panel & Messaging

| Test Case | Steps | Expected Result | PASS/FAIL |
|-----------|-------|-----------------|-----------|
| TC-B1: View terminal output | 1. Select team and role<br/>2. Check terminal panel | Terminal shows pane output with ANSI colors | |
| TC-B2: Send message | 1. Type "test message" in input<br/>2. Click Send | Message appears in terminal output | |
| TC-B3: Autocomplete dropdown | 1. Type "/" in message input | Autocomplete dropdown appears with commands | |
| TC-B4: Command history | 1. Send 2 messages<br/>2. Press Up arrow | Previous command appears in input | |
| TC-B5: Terminal scrolling | 1. Send 50+ messages<br/>2. Scroll terminal output | Scrolling works, output persists | |

**CRITICAL:** TC-B3 and TC-B4 test newly extracted components (`AutocompleteDropdown`, `CommandHistory`)

---

### C. File Browser

| Test Case | Steps | Expected Result | PASS/FAIL |
|-----------|-------|-----------------|-----------|
| TC-C1: Load file tree | 1. Click File Browser tab<br/>2. Check tree display | Project directory tree loads | |
| TC-C2: Expand directory | 1. Click folder icon<br/>2. Check children | Directory expands, shows children | |
| TC-C3: View file | 1. Click "README.md"<br/>2. Check content panel | File content displays with syntax highlighting | |
| TC-C4: Syntax highlighting | 1. View `.ts` file | TypeScript syntax highlighted correctly | |
| TC-C5: Markdown rendering | 1. View `.md` file | Markdown rendered with formatting | |

---

### D. Team Creator

| Test Case | Steps | Expected Result | PASS/FAIL |
|-----------|-------|-----------------|-----------|
| TC-D1: Open creator | 1. Click Team Creator tab | Visual flow editor loads | |
| TC-D2: Add role node | 1. Drag role from palette<br/>2. Drop on canvas | Role node appears on canvas | |
| TC-D3: Connect nodes | 1. Drag from output handle<br/>2. Connect to input | Edge created between nodes | |
| TC-D4: Edit role config | 1. Click role node<br/>2. Edit properties | Properties panel shows/edits config | |
| TC-D5: Save template | 1. Design team<br/>2. Click Save | Template saved to backend | |

---

### E. Voice Commands

| Test Case | Steps | Expected Result | PASS/FAIL |
|-----------|-------|-----------------|-----------|
| TC-E1: Mic button visible | 1. Check header | Mic button shows in top-right | |
| TC-E2: Start recording | 1. Click mic button | Recording starts, UI shows "Listening..." | |
| TC-E3: Transcription display | 1. Speak "test command"<br/>2. Check transcript panel | Real-time transcription appears | |
| TC-E4: Stop word detection | 1. Speak "thank you"<br/>2. Check command sent | Command sent to selected role | |
| TC-E5: Voice feedback | 1. Complete voice command<br/>2. Listen for TTS | Audio feedback plays confirmation | |

**CRITICAL:** TC-E1, TC-E2 test newly extracted hooks (`useAudioManager`, `useWakeLockManager`)

---

### F. Authentication

| Test Case | Steps | Expected Result | PASS/FAIL |
|-----------|-------|-----------------|-----------|
| TC-F1: Login page | 1. Open http://localhost:3334/login | Login form displays | |
| TC-F2: Valid login | 1. Enter credentials<br/>2. Click Login | Redirects to dashboard, JWT stored | |
| TC-F3: Invalid login | 1. Enter wrong password<br/>2. Click Login | Error message shows, no redirect | |
| TC-F4: Token refresh | 1. Wait for token expiry<br/>2. Make API call | Token auto-refreshes, request succeeds | |
| TC-F5: Logout | 1. Click Logout button | Redirects to login, token cleared | |

---

### G. Settings

| Test Case | Steps | Expected Result | PASS/FAIL |
|-----------|-------|-----------------|-----------|
| TC-G1: Open settings | 1. Click Settings icon<br/>2. Check modal | Settings modal opens | |
| TC-G2: Change TTS provider | 1. Toggle TTS provider<br/>2. Click Save | Setting saved to backend + localStorage | |
| TC-G3: Change theme | 1. Toggle dark/light theme<br/>2. Check UI | Theme changes immediately | |
| TC-G4: Settings persistence | 1. Change settings<br/>2. Refresh page | Settings persist after refresh | |

**CRITICAL:** TC-G1, TC-G2 test newly extracted components (`TeamSettings`, `TeamActions`)

---

### H. WebSocket Real-Time Features

| Test Case | Steps | Expected Result | PASS/FAIL |
|-----------|-------|-----------------|-----------|
| TC-H1: Pane streaming | 1. Select role<br/>2. Watch terminal output | Output streams in real-time via WebSocket | |
| TC-H2: Activity detection | 1. Send message to role<br/>2. Watch activity indicator | Green dot appears on active role | |
| TC-H3: Voice feedback stream | 1. Complete voice command<br/>2. Check feedback panel | Feedback notification appears | |
| TC-H4: WebSocket reconnect | 1. Stop backend<br/>2. Restart backend<br/>3. Check connection | WebSocket reconnects automatically | |

---

### I. API Endpoints (Blackbox via Browser Network Tab)

| Test Case | Steps | Expected Result | PASS/FAIL |
|-----------|-------|-----------------|-----------|
| TC-I1: GET /api/teams | 1. Load dashboard<br/>2. Check Network tab | 200 OK, returns teams array | |
| TC-I2: POST /api/send | 1. Send message to role<br/>2. Check Network tab | 200 OK, message sent successfully | |
| TC-I3: GET /api/files/tree | 1. Open File Browser<br/>2. Check Network tab | 200 OK, returns directory tree | |
| TC-I4: GET /health | 1. Navigate to /health<br/>2. Check response | 200 OK, health status displayed | |
| TC-I5: POST /auth/login | 1. Login<br/>2. Check Network tab | 200 OK, JWT token returned | |

---

## Test Execution Order

**DO NOT SKIP OR REORDER - This sequence is critical:**

1. ✅ **Gate 1: Smoke Test** - If fails, STOP and report blocker
2. ✅ **Gate 2: Entry Point Verification** - Confirm imports updated
3. ✅ **Gate 3: Full Test Suite** - Backend + Frontend all tests passing
4. ✅ **Gate 4: Browser Tests** - Execute all test categories (A-I)

---

## Reporting Format

### If All Tests PASS:

```
QA [HH:mm] -> SM: Sprint R1 Phase 4 COMPLETE - ALL PASS.

Smoke Test: ✅ PASS
Entry Points: ✅ Verified (all imports updated)
Full Test Suite: ✅ PASS (BE: X/X, FE: Y/Y)
Browser Tests: ✅ PASS (9 categories, Z test cases)

NO REGRESSIONS FOUND.
All existing functionality verified working after refactoring.

WHITEBOARD updated.
```

### If Tests FAIL:

```
QA [HH:mm] -> SM: Sprint R1 Phase 4 INCOMPLETE - FAILURES FOUND.

Smoke Test: [✅/❌]
Entry Points: [✅/❌]
Full Test Suite: [✅/❌] - [N failed tests]
Browser Tests: [✅/❌] - [N failed test cases]

FAILURES:
1. [TC-X]: [Description]
   - Expected: [X]
   - Actual: [Y]
   - Screenshot: [path]

2. [TC-Y]: [Description]
   ...

Request FE/BE fixes before re-testing.
```

---

## Tools & Environment

**Browser Testing Tool:** MCP Playwright (via `webapp-testing` skill)
**Target URL:** http://localhost:3334
**Backend URL:** http://localhost:17061
**Test Evidence:** Screenshots saved to `docs/tmux/command-center/sprints/refactoring/test_evidence/`

---

## Success Criteria (Phase 4)

- [ ] All smoke tests pass
- [ ] Entry points verified (no orphaned new files)
- [ ] Full test suites pass (BE + FE, no new failures)
- [ ] All browser test categories pass (A-I)
- [ ] NO functional regressions detected
- [ ] Evidence documented (screenshots, test results)

**ONLY THEN** report Phase 4 COMPLETE to SM.
