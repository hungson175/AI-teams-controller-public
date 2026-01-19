# Sprint 14 Backlog: Intelligent File Path Resolution in Terminal

**Sprint Goal:** Fix terminal file path parsing with intelligent search and caching

**Status:** PLANNING
**Started:** 2026-01-04
**Epic:** Mini Online IDE (P1)
**Sprint Complexity:** MEDIUM (Boss: "looks small but complicated")

---

## ⚠️ CRITICAL: Boss Warning (2026-01-04 14:44)

**Boss's exact words:**
- "The next sprint is going to be very challenging"
- "Tell the tech lead to design it carefully before handing it off to the coders"
- "This feature looks small, but complicated - THINK HARD from several perspectives"
- "BE/FE: TDD very carefully"

**TL Requirements:**
- Design VERY CAREFULLY before coding begins
- Review Boss's technical guidance thoroughly (lines below)
- Think hard from multiple perspectives
- Only after design approved → hand off to FE/BE

---

## Problem Statement

Terminal quick view popup currently fails to resolve file paths correctly. Claude Code outputs mixed path formats (relative, absolute, relative to subdirectories), causing parser to fail. Users click file paths that don't open or open wrong files.

**Examples of Current Failures:**
- Relative paths: `./src/file.ts` - may fail if current dir wrong
- Absolute paths: `/full/path/file.ts` - works but rare
- Subdirectory paths: `subdir/file.ts` - fails (ambiguous base)
- Long paths: Line wrap makes only part clickable

---

## User Story

**As a** developer viewing terminal output
**I want** file paths to resolve correctly regardless of format
**So that** clicking any file path opens the correct file

---

## Acceptance Criteria

- [ ] **AC1:** Resolve relative paths (e.g., `./src/file.ts`)
- [ ] **AC2:** Resolve absolute paths (e.g., `/full/path/file.ts`)
- [ ] **AC3:** Resolve paths relative to subdirectories (e.g., `subdir/file.ts`)
- [ ] **AC4:** Handle ambiguous paths - multiple matches show user choice popup
- [ ] **AC5:** Cache resolved paths (in-memory KV: `project+path` → file list)
- [ ] **AC6:** Cache initializes at project load
- [ ] **AC7:** Cache updates if file not found (search filesystem)
- [ ] **AC8:** Search scope covers all project files
- [ ] **AC9:** Terminal popup shows clickable paths for all formats
- [ ] **AC10:** Long paths remain fully clickable (handle line wrap)

**Success Criteria:** All 10 acceptance criteria PASS in QA testing

---

## Boss Technical Guidance for TL

**Architecture Approach:**
- **Search algorithm:** Similar to Cmd+P file search (fuzzy matching, ranking)
- **Caching strategy:** Simple in-memory KV store
  - Key: `project_name + file_path`
  - Value: List of matching file paths
- **Multi-match handling:** Show popup for user to choose correct file
- **Search lifecycle:**
  1. Initialize cache at project load (index all files)
  2. On path click: Check cache first
  3. If not found: Search filesystem, update cache
  4. If multiple matches: Show user choice popup

**Key Challenges TL Must Address:**
1. How to disambiguate relative vs. absolute paths?
2. What ranking algorithm for multiple matches?
3. How to handle cache invalidation (new files, deleted files)?
4. How to make long paths clickable despite line wrap?
5. Performance: Indexing 10K+ files efficiently?
6. Edge cases: Symlinks, case-sensitive vs. insensitive?

**Boss Emphasis:**
- "Looks small, but complicated"
- "Think hard from several perspectives"
- "TDD very carefully" (both FE and BE)

---

## Technical Scope

**Frontend:**
- Path parsing improvements (handle all formats)
- Search algorithm implementation (or API call to backend)
- Multi-match popup UI
- Cache management (if client-side)
- Line wrap handling for long paths

**Backend:**
- File indexing service (project file tree)
- Search endpoint (if backend handles search)
- Path resolution algorithm
- Cache implementation (if server-side)

**TL Design Questions:**
- Client-side search or backend search? (Performance vs. simplicity)
- When to initialize file index? (Startup vs. lazy load)
- Cache strategy: LRU, TTL, or manual invalidation?
- How to handle cross-project paths?

---

## Dependencies

- Sprint 13 complete (terminal quick view exists)
- File browser backend API (`GET /api/files/{team}/tree`)
- Frontend file path parsing (currently naive implementation)

---

## TL Design Phase (MANDATORY)

**TL must complete BEFORE FE/BE coding:**
1. ✅ Read Boss's technical guidance (above)
2. ⏳ Design architecture (client vs. server, caching, search algorithm)
3. ⏳ Answer key challenges (6 questions above)
4. ⏳ Create technical specs for FE/BE
5. ⏳ Get SM approval before handing off to FE/BE

**SM will NOT assign FE/BE until TL design is complete and approved.**

---

## Sprint Planning Status

- [x] Sprint backlog created
- [ ] TL design phase (CRITICAL - Boss requirement)
- [ ] TL specs reviewed and approved
- [ ] Work assigned to FE/BE
- [ ] Implementation (TDD)
- [ ] Code review (TL)
- [ ] QA testing
- [ ] PO acceptance
- [ ] Retrospective

---

**Next Steps:**
1. SM assigns TL with Boss's warning emphasized
2. TL designs carefully (multiple perspectives, thorough analysis)
3. TL creates specs for FE/BE
4. SM reviews and approves TL design
5. Only then: Hand off to FE/BE for implementation
