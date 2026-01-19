# Codebase Refactoring Plan

**Epic:** Tech Debt Reduction
**Status:** Planned
**Approach:** TDD-First (Boss directive)
**Lead:** TL

## TDD Refactoring Protocol

**MANDATORY for every refactor:**
1. **Verify existing tests pass** before any changes
2. **Add/improve tests** for code being refactored (coverage ≥80%)
3. **Refactor in small commits** - run tests after each change
4. **No functional regressions** - all tests must pass

## Sprint 1: High-Priority File Splitting

### Backend Files (>400 lines)

| File | Lines | Issue | Action |
|------|-------|-------|--------|
| `tree_routes.py` | 515 | Multiple endpoint types | Split: tree_ops.py, crud_ops.py |
| `template_service.py` | 477 | God class | Extract: TemplateGenerator class |
| `command_routes.py` | 455 | Business logic in routes | Extract: CommandProcessor service |
| `file_service.py` | 452 | Too many responsibilities | Extract: FileValidator, PathResolver |
| `tts_providers.py` | 445 | Multiple providers | Split: google_tts.py, hdtts.py, base.py |

### Frontend Files (>400 lines)

| File | Lines | Issue | Action |
|------|-------|-------|--------|
| `TerminalPanel.tsx` | 755 | Massive component | Extract: AutocompleteDropdown, CommandHistory |
| `useVoiceRecorder.ts` | 549 | Complex hook | Extract: AudioManager, WakeLockManager hooks |
| `TeamSidebar.tsx` | 544 | Many responsibilities | Extract: TeamSettings, TeamActions components |

## Sprint 2: Test Coverage Gaps

### Backend Services Without Tests

| Service | Priority | Tests Needed |
|---------|----------|--------------|
| `activity_detector.py` | High | Unit tests for detection logic |
| `content_indexer.py` | High | Unit tests for indexing |
| `tree_builder.py` | High | Unit tests for tree construction |
| `tmux_runner.py` | Medium | Unit tests with mocked subprocess |
| `skip_logic.py` | Medium | Additional edge case tests |

### Backend Routes Without Comprehensive Tests

| Route | Tests Needed |
|-------|--------------|
| `settings_routes.py` | CRUD operations, validation |
| `system_routes.py` | System info endpoints |
| `content_routes.py` | File content retrieval |

## Sprint 3: Code Quality Improvements

### Console.log Cleanup (343 statements)

**Files with most console statements:**
- `VoiceFeedbackContext.tsx` (48)
- Various hooks and contexts

**Action:** Create logging utility:
```typescript
// lib/logger.ts
export const logger = {
  debug: (msg, ...args) => process.env.NODE_ENV === 'development' && console.log(msg, ...args),
  info: (msg, ...args) => console.info(`[INFO] ${msg}`, ...args),
  warn: (msg, ...args) => console.warn(`[WARN] ${msg}`, ...args),
  error: (msg, ...args) => console.error(`[ERROR] ${msg}`, ...args),
}
```

### TypeScript `any` Cleanup

**Files with `any` usage:**
- Test files (acceptable for mocks)
- Hook implementations (needs proper typing)

**Action:** Add proper type definitions, use `unknown` with type guards

## Sprint 4: Configuration Extraction

### Hardcoded Values to Extract

| Location | Values | Target |
|----------|--------|--------|
| `file_service.py` | Blacklist patterns | `config/file_patterns.py` |
| `TerminalPanel.tsx` | Command suggestions | Settings/config |
| Various | Timeouts (30s, 60s, 120s) | `constants.py` / `constants.ts` |
| Various | File size limits (1MB) | Environment variables |

## Code Coverage Requirements

| Component | Current | Target |
|-----------|---------|--------|
| **Backend** | ~85% | 90% |
| **Frontend** | ~70% | 75% |

## Refactoring Rules

1. **One refactor per PR** - easier to review and revert
2. **Preserve public APIs** - internal changes only
3. **Document breaking changes** - if any public API must change
4. **Update imports** - ensure all dependents updated
5. **Run full test suite** - not just affected tests

## Sprint Cadence

| Sprint | Focus | Duration |
|--------|-------|----------|
| Sprint 1 | File splitting (BE + FE) | 2-3 days |
| Sprint 2 | Test coverage gaps | 2 days |
| Sprint 3 | Console.log + TypeScript cleanup | 1-2 days |
| Sprint 4 | Configuration extraction | 1 day |

## Success Criteria

- [ ] All files <400 lines
- [ ] Backend coverage ≥90%
- [ ] Frontend coverage ≥75%
- [ ] Zero console.log in production code
- [ ] TypeScript strict mode passing
- [ ] All existing functionality preserved

## Risk Mitigation

1. **Regression risk**: Full test suite runs on every commit
2. **Merge conflicts**: Small, focused PRs merged quickly
3. **Breaking changes**: Feature flags if needed
4. **Team coordination**: SM coordinates BE/FE refactoring
