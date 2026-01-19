# Sprint Backlog: Terminal File Path Click Popup (Phase 2)

**Sprint Goal:** Enhance terminal file path detection and clicking with improved search algorithm
**Status:** PLANNING
**Priority:** P0 (Boss directive)
**Size:** M (Medium)
**Created:** 2026-01-08 17:33

---

## Background

### Existing Implementation (Sprint 13/14)
The project already has terminal file path clicking:
- `TerminalFileLink.tsx` - Clickable link component
- `QuickViewPopup.tsx` - File content popup
- `FileMatchPopup.tsx` - Multi-match selection
- `usePathResolver.ts` - Suffix matching algorithm
- `useFileListCache.ts` - File list caching

### Known Issues (from Sprint 13 Boss Demo)
1. **Long paths only partially clickable** - Line wrap causes issues
2. **Inconsistent clickability** - Naive path detection regex
3. **Path parsing bugs** - Not all paths detected correctly

### TL Research Recommendation (Option A)
Enhance existing uFuzzy + microfuzz implementation:
- VS Code-style scoring enhancements
- Performance optimizations (debouncing, caching)
- UX improvements (frecency scoring)

---

## Sprint Scope

### Story 1: Enhanced Path Detection Regex (S)
**Goal:** Improve regex to detect more file path patterns in terminal output

**Current Issue:** Naive regex misses edge cases (wrapped lines, special characters)

**Acceptance Criteria:**
- [ ] AC1: Detect absolute paths (e.g., `/home/user/file.ts`)
- [ ] AC2: Detect relative paths (e.g., `./src/component.tsx`, `../lib/util.ts`)
- [ ] AC3: Detect paths with line numbers (e.g., `file.ts:42`, `file.ts:42:10`)
- [ ] AC4: Handle wrapped long paths (multi-line)
- [ ] AC5: Ignore false positives (URLs, command flags like `--option`)

**TL Design Required:** Yes - regex patterns + edge case handling

---

### Story 2: Improved Path Resolution (S)
**Goal:** Better matching when multiple files have same name

**Current Issue:** Simple suffix matching, length-based ranking only

**Acceptance Criteria:**
- [ ] AC1: Prefer exact filename matches over partial
- [ ] AC2: Consider directory context from terminal output
- [ ] AC3: Use uFuzzy scoring for ambiguous matches
- [ ] AC4: Show match confidence in FileMatchPopup

**TL Design Required:** Yes - scoring algorithm

---

### Story 3: Performance Optimization (S)
**Goal:** Ensure smooth UX with large file lists

**Acceptance Criteria:**
- [ ] AC1: Add debouncing (150ms) for path resolution
- [ ] AC2: Cache resolution results (TTL-based)
- [ ] AC3: Progressive loading for large match lists
- [ ] AC4: No visible lag when clicking file paths

**TL Design Required:** Yes - caching strategy

---

### Story 4: UX Polish (XS)
**Goal:** Improve popup and interaction experience

**Acceptance Criteria:**
- [ ] AC1: Click-outside closes popup (currently broken per Sprint 13)
- [ ] AC2: Keyboard navigation in multi-match popup (arrow keys + enter)
- [ ] AC3: Show file path breadcrumb in QuickViewPopup header
- [ ] AC4: Visual indication of clickable paths (consistent styling)

**TL Design Required:** No - straightforward UI fixes

---

## Total Acceptance Criteria: 17

| Story | Size | AC Count | Owner |
|-------|------|----------|-------|
| Story 1: Enhanced Path Detection | S | 5 | FE |
| Story 2: Improved Path Resolution | S | 4 | FE |
| Story 3: Performance Optimization | S | 4 | FE |
| Story 4: UX Polish | XS | 4 | FE |

---

## Dependencies

- TL technical design required for Stories 1-3
- Existing components: TerminalFileLink, QuickViewPopup, FileMatchPopup, usePathResolver, useFileListCache
- uFuzzy already installed
- No backend changes expected (FE-only sprint)

---

## Sprint Workflow

1. [ ] SM creates sprint backlog (this file) ← CURRENT
2. [ ] TL creates technical spec for Stories 1-3
3. [ ] SM assigns work to FE
4. [ ] FE implements with TDD
5. [ ] TL code review
6. [ ] QA blackbox testing
7. [ ] PO acceptance
8. [ ] Boss demo

---

## Reference Files

| File | Purpose |
|------|---------|
| `frontend/components/terminal/TerminalFileLink.tsx` | Main clickable link component |
| `frontend/components/terminal/QuickViewPopup.tsx` | File content popup |
| `frontend/components/terminal/FileMatchPopup.tsx` | Multi-match selection |
| `frontend/hooks/usePathResolver.ts` | Path resolution logic |
| `frontend/hooks/useFileListCache.ts` | File list caching |
| `docs/research/file-search-and-popup.md` | TL research document |
