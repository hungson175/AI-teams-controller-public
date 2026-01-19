# Product Backlog Analysis - 2026-01-02

**Prepared by:** PO
**Purpose:** Review current backlog, re-prioritize, clarify unclear items, and refine for next sprint

---

## Summary of Findings

### Items to Archive (Already Complete)
1. ✅ Send Special Keys Button (Escape/Enter) - Sprint 3
2. ✅ File Browser Scroll Fix - Sprint 4
3. ✅ File Browser Panel Width - Sprint 3
4. ✅ File Search (Cmd+P) - Sprint 3
5. ✅ Terminal-like Input with Autocomplete - Sprint 2
6. ✅ Responsive Tmux Pane Width - Sprint 1
7. ✅ Beautiful Terminal Display (ANSI Colors) - Sprint 1
8. ✅ File Browser: Add File/Folder - Sprint 8
9. ✅ New Terminal with Directory Picker - Sprint 8
10. ✅ Right-Click to Copy Full Path - Sprint 6

### Items Needing Clarification (Questions for Boss)
1. **Rename tmux session** (P1) - Shows 'command-center' → 'command-center' (same name?)
2. **Team List Notification Indicator** - Marked as "WRONG IMPLEMENTATION" but Sprint 8 QA shows 3/3 PASS
3. **Claude Code CLI for Team Operations** - Large epic, needs breaking down

### Items to Re-Prioritize
1. **Team List Notification Indicator** - Move to P0 if truly broken, or archive if Sprint 8 fixed it
2. **Voice Feedback Volume Control** - Should be P1 (high user impact)
3. **Package for Distribution** (NEW from Boss) - Add as P2

### Items to Break Down
1. **[EPIC] Claude Code CLI for Team Operations** - Break into 4 phases
2. **Polish File Browser Epic** - Already broken down, just needs prioritization

---

## Priority Re-Assessment

### P0 - Current/Next Sprint (CRITICAL)

**#1: Team List Notification Indicator - Rework (CLARIFICATION NEEDED)**
- **Status:** CONFLICTING INFO
  - Line 185: "❌ WRONG IMPLEMENTATION - Needs rework"
  - WHITEBOARD Sprint 8: "✅ QA PASS (3/3 tests)"
- **QUESTION FOR BOSS:** Is this actually broken or was it fixed in Sprint 8?
- **If broken:** Needs immediate rework to tie to voice feedback badge (not generic tmux activity)
- **If fixed:** Archive to completed

**#2: Voice Feedback Volume Control**
- **Current Priority:** P1 (should be P0)
- **Rationale:** High user impact - TTS too loud is a real pain point
- **Size:** S (simple slider + localStorage)
- **User Story:**
  - As a user listening to voice feedback
  - I want to control the TTS volume independently
  - So that I don't get blasted when system volume is high
- **Acceptance Criteria:**
  - [ ] Volume slider in Settings (0-100%)
  - [ ] Volume persists across sessions (localStorage)
  - [ ] Applies to voice feedback audio playback
  - [ ] Independent from system volume

---

### P1 - High Priority (Next 1-2 Sprints)

**#3: Clarify Rename Session Issue**
- **Current backlog says:** 'command-center' → 'command-center' (SAME NAME?)
- **QUESTION FOR BOSS:** What should the new name actually be? Or was this already done in Sprint 5?
- **Sprint 5 WHITEBOARD** shows rename story with QA PASS 4/4
- **Likely:** This is DONE and should be archived

**#4: Voice Command Context on Tab Switch**
- **Problem:** Voice commands sent to wrong team/role when user switches context during recording
- **Size:** M
- **Needs Clarification:** What's the expected behavior?
  - Option A: Lock context when recording starts
  - Option B: Update context dynamically as user switches
  - Option C: Show warning when context changes mid-recording
- **QUESTION FOR BOSS:** Which approach do you prefer?

**#5: File Browser: Pre-fill Path in Add File/Folder Dialog**
- **Source:** Sprint 8 Retrospective minor finding
- **Size:** XS
- **User Story:**
  - As a user adding a file/folder
  - I want the current directory path pre-filled in the dialog
  - So that I don't have to type the full path every time
- **Acceptance Criteria:**
  - [ ] Dialog pre-fills current directory path when opened
  - [ ] User can edit the pre-filled path
  - [ ] Works for both file and folder creation

---

### P2 - Medium Priority (When Capacity Allows)

**#6: Package Software for Distribution/Sale (NEW - Boss Request)**
- **Priority:** P2 (Boss specified low priority)
- **Size:** L (Large - needs research + implementation)
- **Problem:** Software runs locally on MacBook only. Need to package for distribution to reach more users.
- **User Story:**
  - As a potential customer
  - I want to install and run AI Teams Controller on my own machine
  - So that I can manage my own tmux teams without relying on Boss's deployment

**Needs Breaking Down - Key Questions:**

1. **Deployment Model:** Which approach?
   - **Option A:** Desktop App (Electron/Tauri wrapper)
     - Pros: Native feel, offline-first, bundled dependencies
     - Cons: Large download size, platform-specific builds
   - **Option B:** Docker Compose
     - Pros: Easy deployment, consistent environment
     - Cons: Requires Docker knowledge, not true "desktop app"
   - **Option C:** Cloud SaaS (multi-tenant)
     - Pros: No installation, centralized updates
     - Cons: Hosting costs, security complexity
   - **QUESTION FOR BOSS:** Which deployment model aligns with your vision?

2. **Monetization:** Is this free or paid?
   - If paid: Need license key system, payment integration
   - If free: Open source or closed binary?

3. **Scope of Work:**
   - Installation script/installer
   - Configuration management (user-specific settings)
   - Documentation (installation guide, user manual)
   - Support for multiple platforms (macOS, Linux, Windows?)
   - Auto-update mechanism
   - Telemetry/analytics (optional)

**Proposed Breakdown (After Boss Clarifies):**
1. Research phase: Evaluate deployment options
2. Proof of concept: Package minimal working version
3. Installation/setup flow
4. Documentation
5. Distribution channel (GitHub releases, website, etc.)

---

**#7: Terminal File Links → Open in File Browser**
- **Current Priority:** P2 (appropriate)
- **Size:** M
- **User Story:**
  - As a user viewing terminal output
  - I want to click on file paths in the terminal
  - So that it switches to file browser and opens that file
- **Implementation:** Parse terminal output for file path patterns, make clickable
- **Acceptance Criteria:**
  - [ ] File paths in terminal output are clickable
  - [ ] Click switches to "browse" tab
  - [ ] File opens in the file viewer
  - [ ] Works with relative and absolute paths

**#8: File Browser CRUD Operations**
- **Status:** Create ✅ Done (Sprint 8), Read ✅ Done, Update/Delete TODO
- **Remaining:**
  - Delete file/folder (P2 - Size S)
  - Rename file/folder (P2 - Size S)
- **Group these as:** "Complete File Browser CRUD Operations"

**#9: Keyboard Shortcuts**
- **Escape to Close Dialogs** (P2 - Size XS)
- **Acceptance Criteria:**
  - [ ] Pressing Escape closes any open dialog/modal
  - [ ] Works for all dialogs (file search, create file, directory picker, etc.)
  - [ ] Focus returns to previous element

---

### P3 - Low Priority / Nice to Have

**#10: [EPIC] Claude Code CLI for Team Operations**
- **Current Priority:** P1 (SHOULD BE P3 - Nice to have, not critical)
- **Rationale:** Current team operation buttons work well enough for now
- **Size:** L (Large - 4 phases)
- **Problem:** Current buttons work but could be improved with CLI approach
- **Proposed Re-prioritization:** Move to P3 unless Boss disagrees

**Phase Breakdown (If/When We Do This):**
1. Phase 1: Clean slate - Delete broken buttons
2. Phase 2: Restart Team via CLI
3. Phase 3: Load Team via CLI
4. Phase 4: Create Team via CLI

**#11: Security Hardening** (P3 - Future)
- Command injection risk in tmux_service.py
- JWT secret hardcoded
- CORS wildcard (*)
- **Note:** This is a LOCAL dev tool, not production SaaS - security less critical

**#12: Voice-Controlled Navigation** (P3 - EPIC Idea)
- "Commander" trigger keyword for hands-free control
- Fun but not essential

---

## Items with CONFLICTING Information

### Team List Notification Indicator
- **BACKLOG.md Line 185:** "❌ WRONG IMPLEMENTATION - Needs rework"
- **WHITEBOARD Sprint 8 QA:** "✅ PASS (3/3 tests)"
- **QUESTION FOR BOSS:** Which is correct?
  - If QA tested the WRONG feature (generic tmux activity vs voice feedback badge), then P0 rework needed
  - If QA tested the RIGHT feature and it works, archive to completed

---

## Questions for Boss (Need Answers to Proceed)

### Q1: Team List Notification Indicator - Broken or Fixed?
**Context:** Backlog says "WRONG IMPLEMENTATION", but Sprint 8 QA shows 3/3 PASS.

**What I need to know:**
- Is the current implementation correct (tied to voice feedback badge)?
- Or is it wrong (tied to generic tmux activity polling)?
- Should I prioritize rework or archive as complete?

### Q2: Rename Session - What's the Target Name?
**Context:** Backlog shows 'command-center' → 'command-center' (same name)

**What I need to know:**
- Was this already completed in Sprint 5?
- If not, what should the new session name be?

### Q3: Voice Command Context on Tab Switch - Expected Behavior?
**Options:**
- A) Lock context when recording starts (can't switch teams mid-recording)
- B) Update context dynamically (follow user's current team/role)
- C) Show warning when context changes mid-recording

**What I need to know:** Which approach do you prefer?

### Q4: Package for Distribution - Deployment Model?
**Options:**
- A) Desktop App (Electron/Tauri)
- B) Docker Compose package
- C) Cloud SaaS (multi-tenant)
- D) Something else?

**What I need to know:**
- Which deployment model aligns with your vision?
- Is this free or paid software?
- Which platforms to support (macOS, Linux, Windows)?

---

## Recommended Next Sprint Candidates

Based on this analysis, I recommend these for **Sprint 9:**

### Option A: Quick Wins (High User Value, Low Effort)
1. **Voice Feedback Volume Control** (P0 - Size S)
2. **Pre-fill Path in Add File/Folder** (P1 - Size XS)
3. **Escape to Close Dialogs** (P2 - Size XS)
4. **File Browser: Delete File/Folder** (P2 - Size S)

**Total Effort:** ~1.5-2 sprints worth (Medium sprint)
**User Value:** High - all address real pain points

### Option B: Focus on Clarity (Resolve Ambiguity)
1. **Team List Notification Rework** (IF Boss confirms it's broken - P0 - Size M)
2. **Voice Command Context on Tab Switch** (P1 - Size M - after Boss clarifies expected behavior)

**Total Effort:** ~1 sprint (Medium sprint)
**User Value:** High - fixes confusing/broken behaviors

### Option C: Let Boss Decide
- Present this analysis to Boss
- Ask Boss to pick top 3-5 items for Sprint 9
- Ensures alignment with Boss's priorities

---

## Actions Required

1. **PO (me):** Present this analysis to Boss
2. **Boss:** Answer 4 questions above
3. **PO:** Update BACKLOG.md based on Boss's answers
4. **PO:** Define Sprint 9 backlog
5. **SM:** Facilitate Sprint 9 planning

---

**Next:** Awaiting Boss feedback on the 4 questions before updating BACKLOG.md.
