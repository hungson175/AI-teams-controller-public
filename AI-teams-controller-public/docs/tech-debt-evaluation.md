# Technical Debt Evaluation

**Date:** 2026-01-11
**Evaluator:** TL (Tech Lead)
**Framework:** SQALE (Software Quality Assessment based on Lifecycle Expectations)

---

## Executive Summary

**Overall Debt Level: MEDIUM (B Rating)**

The AI-teams-controller codebase demonstrates solid foundational architecture with good test coverage and modern technology stack. Primary debt exists in file complexity (4 files >700 lines), incomplete auth migration, and large experimental code directories.

**SQALE Index Estimate:** ~40-60 hours remediation effort
**SQALE Ratio:** ~3-5% (Low-Medium debt relative to codebase size)

---

## Framework: SQALE Method

SQALE assesses technical debt by measuring the **remediation cost** to bring code to conformity with quality requirements. It evaluates 8 characteristics based on ISO 25010:

| Characteristic | Weight | Our Rating | Notes |
|---------------|--------|------------|-------|
| Testability | High | A | 32 backend + 20+ frontend tests |
| Reliability | High | B | Some debug code in production |
| Changeability | Medium | B | Large files reduce changeability |
| Efficiency | Medium | A | Async throughout, modern stack |
| Security | High | B | Mixed auth (JWT incomplete) |
| Maintainability | High | B | Good structure, some complexity |
| Portability | Low | A | Standard frameworks |
| Reusability | Medium | B | Some duplication in tests |

---

## Debt Assessment by Category

### 1. CODE COMPLEXITY (Changeability)

**Debt Level: MEDIUM**

Files exceeding 500-line threshold (harder to maintain/change):

| File | Lines | Remediation | Priority |
|------|-------|-------------|----------|
| backend/app/api/file_routes.py | 905 | 4h - Split into modules | HIGH |
| backend/app/api/voice_routes.py | 748 | 3h - Extract endpoints | HIGH |
| backend/app/services/tmux_service.py | 693 | 3h - Extract classes | MEDIUM |
| backend/app/services/file_service.py | 684 | 3h - Separate concerns | MEDIUM |
| frontend/components/controller/TmuxController.tsx | 913 | 4h - Extract hooks | HIGH |
| frontend/components/controller/TerminalPanel.tsx | 754 | 3h - Split components | MEDIUM |
| frontend/contexts/VoiceFeedbackContext.tsx | 608 | 3h - Compose contexts | MEDIUM |

**Subtotal: ~23 hours**

### 2. SECURITY (Auth Migration)

**Debt Level: MEDIUM**

Incomplete JWT migration creates inconsistent auth patterns:

```
Current State:
- /api/auth/* - JWT tokens (complete)
- /api/teams, /api/send, /api/state, /api/files - SESSION_TOKEN (legacy)
```

**Evidence:** 4 TODO comments in `main.py` marking incomplete migration

| Item | Remediation | Priority |
|------|-------------|----------|
| Complete JWT migration | 4h | HIGH |
| Remove SESSION_TOKEN fallback | 1h | HIGH |
| Update frontend auth headers | 2h | MEDIUM |

**Subtotal: ~7 hours**

### 3. MAINTAINABILITY (Debug Code)

**Debt Level: LOW-MEDIUM**

Debug artifacts left in production code:

| Location | Issue | Remediation |
|----------|-------|-------------|
| frontend/hooks/useFileListCache.ts | DEBUG console logs | 0.5h |
| frontend/hooks/usePathResolver.ts | DEBUG console logs | 0.5h |
| frontend/components/voice/* | "BUG FIX" markers | 1h review |
| backend/app/main.py | TODO comments | 0.5h |

**Subtotal: ~2.5 hours**

### 4. TESTABILITY (Test Organization)

**Debt Level: LOW**

Large test files could be better organized:

| Test File | Lines | Issue |
|-----------|-------|-------|
| useVoiceRecorder.test.ts | 1,211 | Could split by scenario |
| test_voice_routes.py | 1,033 | Consolidate fixtures |
| TerminalPanel.test.tsx | 992 | Split by feature |

**Note:** Large tests are better than no tests. This is LOW priority.

**Subtotal: ~4 hours (optimization, not critical)**

### 5. REUSABILITY (Code Duplication)

**Debt Level: LOW**

- Multiple test files mock same OpenAI/xAI APIs independently
- Mock patterns could be consolidated into shared fixtures

**Subtotal: ~3 hours**

### 6. PORTABILITY (Project Cleanliness)

**Debt Level: MEDIUM**

Large directories that should be separated:

| Directory | Size | Recommendation |
|-----------|------|----------------|
| /experiments | 668MB | Move to separate repo |
| /sample_codes | 164MB | Move to separate repo |
| /android + /android_apps | 478MB | Move to separate repo |

**Total: 1.3GB of non-core code in main repo**

**Subtotal: ~4 hours (repo restructuring)**

---

## Top 5 Debt Areas (Prioritized)

### 1. File Complexity - HIGH PRIORITY
- **What:** 4 backend + 3 frontend files exceed 700 lines
- **Impact:** Reduces changeability, increases bug risk
- **Remediation:** 23h - Extract modules, hooks, components
- **ROI:** High - Every future change benefits

### 2. Auth Migration Incomplete - HIGH PRIORITY
- **What:** Mixed SESSION_TOKEN + JWT authentication
- **Impact:** Security inconsistency, confusing codebase
- **Remediation:** 7h - Complete JWT rollout
- **ROI:** High - Security + code clarity

### 3. Debug Code in Production - MEDIUM PRIORITY
- **What:** Console logs, TODO markers, BUG FIX comments
- **Impact:** Log noise, unclear code state
- **Remediation:** 2.5h - Clean sweep
- **ROI:** Medium - Quick win

### 4. Repository Bloat - MEDIUM PRIORITY
- **What:** 1.3GB experimental/sample code in main repo
- **Impact:** Clone time, confusion about project scope
- **Remediation:** 4h - Split into repos
- **ROI:** Medium - One-time cleanup

### 5. Test Mock Duplication - LOW PRIORITY
- **What:** Repeated API mock patterns across tests
- **Impact:** Maintenance overhead for mock updates
- **Remediation:** 3h - Shared fixtures
- **ROI:** Low - Tests already work

---

## Refactoring Priorities

### Sprint 1 (High Priority - 14h)
1. **Split file_routes.py** (4h) - Extract into file_tree_routes, file_content_routes, file_search_routes
2. **Split voice_routes.py** (3h) - Extract into voice_token_routes, voice_command_routes, voice_task_routes
3. **Complete JWT migration** (7h) - Update 4 legacy endpoints + frontend

### Sprint 2 (High Priority - 13h)
1. **Split TmuxController.tsx** (4h) - Extract useTeamState, usePaneSelection hooks
2. **Refactor tmux_service.py** (3h) - Extract ActivityDetector, MessageTracker classes
3. **Refactor file_service.py** (3h) - Separate TreeBuilder, FileSearcher
4. **Clean debug code** (2.5h) - Remove console.logs, resolve TODOs

### Sprint 3 (Medium Priority - 10h)
1. **Split TerminalPanel.tsx** (3h)
2. **Compose VoiceFeedbackContext** (3h) - Extract ConnectionContext, AudioContext
3. **Repository cleanup** (4h) - Move experiments, samples, android to separate repos

### Backlog (Low Priority - 7h)
1. Consolidate test mock fixtures (3h)
2. Split large test files (4h)

---

## Positive Findings

The codebase has strong foundations:

- **Good SRP Example:** Voice Feedback service properly decomposed into 4 modules (content, summary, audio, broadcast)
- **Modern Stack:** React 19, Next.js 16, FastAPI async, SQLAlchemy 2.0
- **Strong Test Coverage:** 32 backend + 20+ frontend test files
- **Type Safety:** TypeScript strict mode + Pydantic validation
- **Documentation:** 102 markdown files including team playbook
- **Proper Async:** Backend uses async/await throughout
- **Clean Dependencies:** Lock files present, modern versions

---

## Conclusion

**Total Estimated Remediation: ~44 hours**

| Priority | Hours | Items |
|----------|-------|-------|
| High | 27h | File complexity (23h) + Auth (4h) |
| Medium | 10h | Debug cleanup (2.5h) + Repo bloat (4h) + Contexts (3.5h) |
| Low | 7h | Test organization |

**Recommendation:** Address High priority items over 2 sprints (~27h). This resolves 60% of technical debt and provides foundation for sustainable development.

---

## References

- [SQALE Method - IEEE](https://ieeexplore.ieee.org/document/6225997/)
- [SQALE Wikipedia](https://en.wikipedia.org/wiki/SQALE)
- [SonarSource SQALE](https://www.sonarsource.com/blog/sqale-the-ultimate-quality-model-to-assess-technical-debt/)
- ISO 25010:2011 Software Quality Model
