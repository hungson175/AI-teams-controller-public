# Sprint 1 Backlog: Simple File Search + Terminal Click Integration

**Epic:** Simple File Search + Terminal Click Integration (2 sprints total)
**Sprint Goal:** File indexing + word search in file browser
**Status:** PLANNING
**Priority:** P0 (Boss directive - START NOW)
**Size:** M (Medium)
**Created:** 2026-01-08 18:53

---

## Epic Overview (2 Sprints)

**Boss Requirements:**
- Simple file indexing (NO fancy algorithms)
- Word search capability in file browser
- Exclude .gitignore patterns and library folders
- TDD fully
- Keep it simple

**Sprint 1:** File Indexing + Word Search (this sprint)
**Sprint 2:** Terminal Click Integration (future)

---

## Sprint 1 Scope

### Story 1: File Indexing System (M)
**Goal:** Build simple file list with content indexing

**Requirements:**
- Index all files in project
- Exclude files matching .gitignore patterns
- Exclude library folders (node_modules, .git, __pycache__, etc.)
- Store file path + content for searching
- Simple in-memory index (no fancy algorithms)

**Acceptance Criteria:**
- [ ] AC1: API endpoint returns indexed file list
- [ ] AC2: .gitignore patterns are respected (excluded files not indexed)
- [ ] AC3: Library folders excluded (node_modules, .git, __pycache__, venv, dist, build)
- [ ] AC4: Index refreshes when file browser opens
- [ ] AC5: Index handles 1000+ files without performance issues

**TL Design Required:** Yes - indexing approach, exclusion logic

---

### Story 2: Word Search in File Browser (M)
**Goal:** Search for words/phrases across all indexed files

**Requirements:**
- Simple text search (substring matching)
- Search input in file browser UI
- Show matching files with match count
- Click result to open file viewer at match location
- NO fancy fuzzy matching - simple word search

**Acceptance Criteria:**
- [ ] AC1: Search input visible in file browser
- [ ] AC2: Typing shows matching files in real-time
- [ ] AC3: Each result shows file path + match count
- [ ] AC4: Clicking result opens file in viewer
- [ ] AC5: Search is case-insensitive
- [ ] AC6: Empty search clears results
- [ ] AC7: "No results" message when no matches

**TL Design Required:** Yes - search UI/UX, result display

---

### Story 3: Exclusion Configuration (S)
**Goal:** Respect .gitignore and standard exclusions

**Requirements:**
- Parse .gitignore file
- Apply patterns to exclude files from index
- Hardcoded exclusions for common library folders

**Acceptance Criteria:**
- [ ] AC1: .gitignore patterns parsed correctly
- [ ] AC2: Glob patterns work (*.log, **/*.tmp)
- [ ] AC3: Directory patterns work (node_modules/, .git/)
- [ ] AC4: Negation patterns work (!important.log)

**TL Design Required:** Yes - .gitignore parsing approach

---

## Total Acceptance Criteria: 16

| Story | Size | AC Count | Owner |
|-------|------|----------|-------|
| Story 1: File Indexing System | M | 5 | BE + FE |
| Story 2: Word Search in File Browser | M | 7 | FE |
| Story 3: Exclusion Configuration | S | 4 | BE |

---

## Technical Notes

**Keep It Simple (Boss directive):**
- NO fancy algorithms (no uFuzzy, no scoring)
- Simple substring matching
- In-memory index (no database)
- Standard string.includes() for search

**Exclusion Patterns (hardcoded):**
```
node_modules/
.git/
__pycache__/
venv/
.venv/
dist/
build/
.next/
*.pyc
*.log
```

**Plus:** Parse .gitignore for project-specific exclusions

---

## Sprint Workflow

1. [ ] SM creates sprint backlog (this file) ← CURRENT
2. [ ] TL creates technical spec
3. [ ] SM assigns work to FE/BE
4. [ ] BE implements file indexing + exclusions (Stories 1, 3)
5. [ ] FE implements search UI (Story 2)
6. [ ] TL code review
7. [ ] QA blackbox testing
8. [ ] PO acceptance
9. [ ] Boss demo

---

## Dependencies

- File list API already exists (`/api/files/{team}/list`)
- Need new endpoint for file content search
- FE file browser component exists

---

## TDD Requirements

**Coverage Targets:**
- Frontend: 70% minimum
- Backend: 80% minimum

**Test Categories:**
- Unit tests for indexing logic
- Unit tests for .gitignore parsing
- Integration tests for search API
- Component tests for search UI
