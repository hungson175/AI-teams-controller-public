# WHITEBOARD - Scrum Team

**Purpose:** Real-time workspace for CURRENT sprint only. Cleared after each sprint.

**Last Updated**: 2026-01-19 13:00 (SM - Sprint R1 started)
**Git Branch**: feature/refactor-sprint-r1

---

## Current Sprint: R1 - File Splitting Refactoring

**Status:** IN PROGRESS - Phase 1 (TDD Red)
**Sprint Goal:** Split large files (>400 lines) into single-responsibility modules
**Approach:** TDD-First (tests before refactoring)
**Backlog:** `docs/tmux/command-center/sprints/refactoring/SPRINT_R1_BACKLOG.md`

---

## Sprint Phases

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Write tests for new structure (TDD Red) | 🔄 Remaining: BE 3 files, FE 1 file |
| Phase 2 | TL review test specs | ✅ 4/4 approved (tree_routes, TerminalPanel, template_service, useVoiceRecorder) |
| Phase 3 | Refactor code (TDD Green) | 🔄 BE + FE extracting |
| Phase 4 | QA regression testing | ⏳ Pending |

---

## Work Assignments

### Backend (BE) - 5 Files
| File | Lines | Action | Status |
|------|-------|--------|--------|
| tree_routes.py | 515 | Split → tree_ops.py + crud_ops.py | ✅ COMPLETE (commit 2ab79dcb) |
| template_service.py | 477 | Extract TemplateGenerator class | ✅ COMPLETE (commit 9cd25a47) |
| command_routes.py | 455 | Extract CommandProcessor service | 🔄 Phase 3 (extraction) |
| file_service.py | 452 | Extract FileValidator + PathResolver | 🔄 Phase 3 (extraction) |
| tts_providers.py | 445 | Split → base.py + google_tts.py + hdtts.py | 🔄 Tests in progress |

### Frontend (FE) - 3 Files
| File | Lines | Action | Status |
|------|-------|--------|--------|
| TerminalPanel.tsx | 755 | Extract AutocompleteDropdown + CommandHistory | 🔄 Tests 102/104 (fixing last 2) |
| useVoiceRecorder.ts | 549 | Extract useAudioManager + useWakeLockManager | 🔄 Extracted, fixing tests (75%) |
| TeamSidebar.tsx | 544 | Extract TeamSettings + TeamActions | ⏳ May defer to R2 |

---

## Team Status

| Role | Status | Current Task |
|------|--------|--------------|
| PO | ✅ READY | Monitoring Sprint R1 |
| SM | 🔄 ACTIVE | Coordinating Sprint R1 |
| TL | ✅ READY | file_service approved, awaiting tts_providers |
| FE | 🔄 ACTIVE | Phase 1: Writing tests for file splits |
| BE | 🔄 ACTIVE | Phase 1: Writing tests for file splits |
| QA | ✅ READY | Phase 4 preparation complete (test plan + scenarios ready) |

---

## Blockers

(None currently)

---

## TDD Protocol (MANDATORY)

1. Write tests for new structure BEFORE splitting
2. TL reviews test specs before implementation
3. Refactor in small commits - run tests after each
4. No functional regressions allowed
