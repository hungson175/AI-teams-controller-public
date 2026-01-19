# Sprint R1: File Splitting Refactoring

**Sprint Goal:** Split large files (>400 lines) into manageable, single-responsibility modules
**Approach:** TDD-First (tests before refactoring)
**Duration:** 2-3 days

---

## TDD Protocol (MANDATORY)

1. **Phase 1 (Red):** Write tests for new structure BEFORE splitting
2. **Phase 2 (Review):** TL reviews test specs
3. **Phase 3 (Green):** Refactor code to pass tests
4. **Phase 4 (Verify):** QA regression testing

---

## Backend Tasks (BE)

### 1. tree_routes.py (515 lines)
**Issue:** Multiple endpoint types mixed
**Action:** Split into:
- `tree_ops.py` - Tree operations (list, build, navigate)
- `crud_ops.py` - CRUD operations (create, read, update, delete)

**Tasks:**
- [ ] Write tests for tree_ops.py endpoints
- [ ] Write tests for crud_ops.py endpoints
- [ ] TL review tests
- [ ] Split file, ensure tests pass
- [ ] Update imports in dependent files

### 2. template_service.py (477 lines)
**Issue:** God class with too many responsibilities
**Action:** Extract TemplateGenerator class

**Tasks:**
- [ ] Write tests for TemplateGenerator class
- [ ] TL review tests
- [ ] Extract class, ensure tests pass

### 3. command_routes.py (455 lines)
**Issue:** Business logic mixed in routes
**Action:** Extract CommandProcessor service

**Tasks:**
- [ ] Write tests for CommandProcessor service
- [ ] TL review tests
- [ ] Extract service, ensure tests pass

### 4. file_service.py (452 lines)
**Issue:** Too many responsibilities
**Action:** Extract:
- FileValidator class
- PathResolver class

**Tasks:**
- [ ] Write tests for FileValidator
- [ ] Write tests for PathResolver
- [ ] TL review tests
- [ ] Extract classes, ensure tests pass

### 5. tts_providers.py (445 lines)
**Issue:** Multiple providers in one file
**Action:** Split into:
- `base.py` - Base TTS provider interface
- `google_tts.py` - Google TTS implementation
- `hdtts.py` - HDTTS implementation

**Tasks:**
- [ ] Write tests for each provider
- [ ] TL review tests
- [ ] Split file, ensure tests pass

---

## Frontend Tasks (FE)

### 1. TerminalPanel.tsx (755 lines)
**Issue:** Massive component with mixed concerns
**Action:** Extract:
- AutocompleteDropdown component
- CommandHistory component

**Tasks:**
- [ ] Write tests for AutocompleteDropdown
- [ ] Write tests for CommandHistory
- [ ] TL review tests
- [ ] Extract components, ensure tests pass

### 2. useVoiceRecorder.ts (549 lines)
**Issue:** Complex hook with multiple concerns
**Action:** Extract:
- useAudioManager hook
- useWakeLockManager hook

**Tasks:**
- [ ] Write tests for useAudioManager
- [ ] Write tests for useWakeLockManager
- [ ] TL review tests
- [ ] Extract hooks, ensure tests pass

### 3. TeamSidebar.tsx (544 lines)
**Issue:** Many responsibilities
**Action:** Extract:
- TeamSettings component
- TeamActions component

**Tasks:**
- [ ] Write tests for TeamSettings
- [ ] Write tests for TeamActions
- [ ] TL review tests
- [ ] Extract components, ensure tests pass

---

## Sprint Phases

### Phase 1: Test Creation (TDD Red)
- FE writes tests for 3 file splits (6 new components/hooks)
- BE writes tests for 5 file splits (8 new modules/classes)

### Phase 2: TL Review
- TL reviews all test specs
- TL provides architectural feedback
- Tests approved before implementation

### Phase 3: Implementation (TDD Green)
- FE refactors files to pass tests
- BE refactors files to pass tests
- Run full test suite after each split

### Phase 4: Integration & QA
- QA regression testing (blackbox, browser-based)
- All existing functionality verified
- TL final code review

---

## Success Criteria

- [ ] All 8 files split into smaller modules
- [ ] Each new file < 400 lines
- [ ] All tests passing
- [ ] Code coverage maintained (BE ≥85%, FE ≥70%)
- [ ] No functional regressions
- [ ] Imports updated across codebase

---

## Reference

- **Refactoring Plan:** `docs/tmux/command-center/sprints/refactoring/REFACTORING_PLAN.md`
- **TL Analysis:** See REFACTORING_PLAN.md for detailed file analysis
