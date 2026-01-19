# Playwright Test Scenarios - Sprint R1

**Purpose:** Automated browser testing scripts for Phase 4 regression testing
**Tool:** MCP Playwright via `webapp-testing` skill
**Target:** http://localhost:3334

---

## Critical User Flows

### Flow 1: Team Selection & Terminal Viewing

**User Story:** As a user, I want to select a team and view terminal output for a specific role

**Playwright Steps:**
1. Navigate to http://localhost:3334
2. Wait for team selector to load
3. Click team dropdown
4. Select "command-center" team
5. Verify role tabs appear (PO, SM, TL, FE, BE, QA)
6. Click "FE" tab
7. Verify terminal panel shows output
8. Verify terminal has ANSI color formatting

**Expected Evidence:**
- Screenshot: Team selector with available teams
- Screenshot: Role tabs displayed
- Screenshot: Terminal output for selected role

**Why Critical:** Tests `TerminalPanel.tsx` (755 lines → split into AutocompleteDropdown + CommandHistory)

---

### Flow 2: Send Message to Role

**User Story:** As a user, I want to send a message to a Claude Code role via tmux

**Playwright Steps:**
1. Continue from Flow 1 (team selected, role tab active)
2. Locate message input field
3. Type "test message from QA regression"
4. Click Send button (or press Enter)
5. Wait 2 seconds
6. Verify message appears in terminal output
7. Check Network tab for POST /api/send/{team}/{role}
8. Verify response status 200

**Expected Evidence:**
- Screenshot: Message input field with text
- Screenshot: Message appearing in terminal output
- Network log: POST request success

**Why Critical:** Core functionality - sending commands to AI agents

---

### Flow 3: Autocomplete & Command History

**User Story:** As a user, I want autocomplete suggestions and command history when typing messages

**Playwright Steps:**
1. Continue from Flow 1 (team selected, role active)
2. Click message input field
3. Type "/" character
4. Verify autocomplete dropdown appears
5. Verify dropdown shows command suggestions
6. Press Escape to close dropdown
7. Type "first command" and send
8. Type "second command" and send
9. Click message input field
10. Press Up arrow key
11. Verify "second command" appears in input
12. Press Up arrow again
13. Verify "first command" appears in input

**Expected Evidence:**
- Screenshot: Autocomplete dropdown with suggestions
- Screenshot: Command history navigation working

**Why CRITICAL:** Tests newly extracted `AutocompleteDropdown` and `CommandHistory` components from `TerminalPanel.tsx` refactoring

---

### Flow 4: File Browser Navigation

**User Story:** As a user, I want to browse project files and view their contents

**Playwright Steps:**
1. Navigate to http://localhost:3334
2. Click "File Browser" tab
3. Wait for directory tree to load
4. Verify root folders appear (backend, frontend, docs)
5. Click "docs" folder to expand
6. Verify subfolders appear
7. Click "README.md" file
8. Verify file content displays in right panel
9. Verify markdown rendering (headings, lists, code blocks)
10. Click "backend/app/main.py" file
11. Verify Python syntax highlighting

**Expected Evidence:**
- Screenshot: Directory tree loaded
- Screenshot: Folder expanded
- Screenshot: Markdown file rendered
- Screenshot: Python file with syntax highlighting

**Why Critical:** File service refactoring (`file_service.py` → FileValidator + PathResolver)

---

### Flow 5: Team Creator Visual Editor

**User Story:** As a user, I want to visually design a team configuration using drag-drop

**Playwright Steps:**
1. Navigate to http://localhost:3334
2. Click "Team Creator" tab
3. Wait for React Flow canvas to load
4. Verify role palette appears on left
5. Drag "PO" role from palette to canvas
6. Verify "PO" node appears on canvas
7. Drag "SM" role from palette to canvas
8. Verify "SM" node appears
9. Click "PO" node
10. Verify properties panel appears
11. Edit role name or config
12. Click Save button
13. Verify success message

**Expected Evidence:**
- Screenshot: Empty canvas with palette
- Screenshot: Nodes added to canvas
- Screenshot: Properties panel editing node
- Screenshot: Save confirmation

**Why Critical:** Complex component, tests template service (`template_service.py` → TemplateGenerator)

---

### Flow 6: Voice Command Flow (If MCP Playwright Supports Audio)

**User Story:** As a user, I want to send voice commands to AI agents

**Playwright Steps:**
1. Navigate to http://localhost:3334
2. Verify mic button visible in header
3. Click mic button
4. Verify recording UI appears ("Listening..." indicator)
5. Simulate audio input or type in transcript box (if testing mode)
6. Type "send message to team"
7. Type "thank you" (stop word)
8. Verify command sent to selected role
9. Verify TTS feedback notification appears

**Expected Evidence:**
- Screenshot: Mic button in header
- Screenshot: Recording UI active
- Screenshot: Transcript displayed
- Screenshot: Feedback notification

**Why CRITICAL:** Tests newly extracted hooks from `useVoiceRecorder.ts` → `useAudioManager` + `useWakeLockManager`

**Note:** If Playwright cannot simulate audio, test UI interactions only (button states, transcript display, manual input).

---

### Flow 7: Authentication & Session

**User Story:** As a user, I want to login and maintain authenticated session

**Playwright Steps:**
1. Navigate to http://localhost:3334/login
2. Verify login form displays
3. Enter username: "test@example.com"
4. Enter password: "testpassword"
5. Click Login button
6. Verify redirect to dashboard (/)
7. Check localStorage for JWT token
8. Verify token exists
9. Make API call (e.g., GET /api/teams)
10. Verify request includes Authorization header
11. Click Logout button
12. Verify redirect to /login
13. Check localStorage - token should be cleared

**Expected Evidence:**
- Screenshot: Login form
- Screenshot: Dashboard after login
- LocalStorage inspection: JWT token present
- Network log: Authorization header in requests
- Screenshot: Back to login after logout

**Why Critical:** Core security functionality

---

### Flow 8: Settings Persistence

**User Story:** As a user, I want my settings to persist across sessions

**Playwright Steps:**
1. Login to application
2. Click Settings icon/button
3. Verify settings modal opens
4. Change TTS provider (toggle Google/OpenAI)
5. Change theme (dark/light toggle)
6. Click Save button
7. Verify success message
8. Refresh browser page
9. Verify TTS provider setting persisted
10. Verify theme setting persisted
11. Open Settings again
12. Verify previous selections still active

**Expected Evidence:**
- Screenshot: Settings modal with options
- Screenshot: Settings changed and saved
- Screenshot: After refresh, settings still applied

**Why CRITICAL:** Tests newly extracted `TeamSettings` and `TeamActions` components from `TeamSidebar.tsx` refactoring

---

### Flow 9: Real-Time Activity Detection

**User Story:** As a user, I want to see which AI agents are actively working

**Playwright Steps:**
1. Navigate to http://localhost:3334
2. Select "command-center" team
3. Observe role tabs (PO, SM, TL, FE, BE, QA)
4. Send message to "FE" role
5. Wait 2 seconds
6. Verify "FE" tab shows green activity dot
7. Wait 10 seconds (activity polling interval)
8. If FE becomes idle, verify dot changes to gray
9. Send message to "BE" role
10. Verify "BE" tab shows green activity dot

**Expected Evidence:**
- Screenshot: Role tabs with activity indicators
- Screenshot: Green dot on active role
- Screenshot: Gray dot on idle role

**Why Critical:** Tests WebSocket streaming and activity detection service

---

### Flow 10: WebSocket Reconnection

**User Story:** As a user, I want the app to reconnect automatically if backend restarts

**Playwright Steps:**
1. Navigate to http://localhost:3334
2. Select team and role
3. Verify terminal output streaming
4. Open browser DevTools Network tab
5. Verify WebSocket connection established (ws://localhost:17061/...)
6. Simulate backend disconnect (if possible in test env)
7. Wait 5 seconds
8. Restart backend (if simulated disconnect)
9. Verify WebSocket reconnects automatically
10. Verify terminal output resumes streaming

**Expected Evidence:**
- Screenshot: WebSocket connection in Network tab
- Screenshot: Reconnection after disconnect
- Network log: WebSocket reconnection events

**Why Critical:** Resilience testing for long-running sessions

---

## Smoke Test Checklist (Run FIRST Before Feature Tests)

**Critical Gate:** If ANY smoke test fails, STOP and report blocker to SM

```playwright
// Pseudo-code for smoke test
async function smokeTest() {
  // 1. Navigate to app
  await page.goto('http://localhost:3334');

  // 2. Wait for app to load (max 10 seconds)
  await page.waitForSelector('[data-testid="app-loaded"]', { timeout: 10000 });

  // 3. Verify NOT stuck on loading screen
  const loadingScreen = await page.$('[data-testid="loading-screen"]');
  assert(loadingScreen === null, 'App stuck on loading screen');

  // 4. Verify basic interaction works
  await page.click('[data-testid="team-selector"]');
  const dropdown = await page.$('[data-testid="team-dropdown"]');
  assert(dropdown !== null, 'Team selector not interactive');

  console.log('✅ SMOKE TEST PASSED');
}
```

---

## Test Execution Strategy

### Sequential Execution (DO NOT PARALLELIZE)

Browser tests must run sequentially to avoid:
- Race conditions in WebSocket connections
- Conflicting state changes
- Port conflicts

**Order:**
1. Smoke Test (BLOCKER if fails)
2. Flow 1: Team Selection & Terminal Viewing
3. Flow 2: Send Message to Role
4. Flow 3: Autocomplete & Command History ⭐ (NEW COMPONENTS)
5. Flow 4: File Browser Navigation
6. Flow 5: Team Creator Visual Editor
7. Flow 6: Voice Command Flow ⭐ (NEW HOOKS)
8. Flow 7: Authentication & Session
9. Flow 8: Settings Persistence ⭐ (NEW COMPONENTS)
10. Flow 9: Real-Time Activity Detection
11. Flow 10: WebSocket Reconnection

**⭐ = Tests newly extracted components/hooks from refactoring**

---

## Test Evidence Collection

### Screenshot Naming Convention

```
test_evidence/
├── flow1_team_selection_01_dropdown.png
├── flow1_team_selection_02_role_tabs.png
├── flow3_autocomplete_01_dropdown.png  # NEW COMPONENT
├── flow3_command_history_01_navigation.png  # NEW COMPONENT
├── flow6_voice_audio_manager_01_recording.png  # NEW HOOK
├── flow8_settings_01_modal.png  # NEW COMPONENT
└── ...
```

### Test Results Log

```
test_results_r1.md
---
Date: 2026-01-19
Sprint: R1
Phase: 4 (QA Regression Testing)

SMOKE TEST: ✅ PASS
  - App loaded: ✅
  - No loading screen stuck: ✅
  - Basic interaction: ✅

FLOW 1 (Team Selection): ✅ PASS
FLOW 2 (Send Message): ✅ PASS
FLOW 3 (Autocomplete/History): ✅ PASS  # NEW COMPONENTS
...
```

---

## Baseline Comparison (Memory-Driven Pattern)

**Before Refactoring (Establish Baseline):**
- Run all flows before FE/BE start file splits
- Document expected outputs
- Save screenshots for comparison

**After Refactoring (Compare to Baseline):**
- Run same flows after file splits complete
- Compare outputs byte-for-byte (where deterministic)
- Compare screenshots visually
- Flag ANY differences as potential regressions

---

## Tools & Commands

**Playwright via webapp-testing skill:**
```bash
# In QA pane during Phase 4
/webapp-testing "Run Flow 1: Team Selection"
# Skill will use MCP Playwright to execute browser tests
```

**Manual browser testing:**
```bash
# If MCP Playwright unavailable (BLOCKER - notify SM)
# Open browser manually and follow test steps
# Take screenshots manually
```

---

## Success Criteria

- [ ] All 10 flows execute successfully
- [ ] All newly extracted components tested (Flows 3, 6, 8)
- [ ] Screenshots captured for evidence
- [ ] Results documented in test_results_r1.md
- [ ] NO regressions detected vs baseline
