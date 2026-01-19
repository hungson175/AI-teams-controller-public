# TL Spec: Sprint 14 - Intelligent File Path Resolution

**Author:** TL
**Date:** 2026-01-04
**Sprint:** 14
**Status:** DESIGN COMPLETE - Awaiting SM Approval

---

## Executive Summary

This spec addresses the terminal file path resolution problem where Claude Code outputs mixed path formats (relative, absolute, subdirectory-relative) that fail to open correctly in QuickViewPopup.

**Solution:** Client-side path resolution using existing file list cache with suffix matching algorithm.

---

## Design Decisions (6 Key Questions Answered)

### Q1: Client-side vs. Backend Search?

**Decision: Client-side**

| Factor | Client-side | Backend |
|--------|-------------|---------|
| Latency | ~0ms (in-memory) | ~50-100ms (network) |
| Complexity | Lower | Higher (new endpoint) |
| Existing infra | FileSearch already caches file list | Would need new endpoint |
| 10K files | Fine (array filter is O(n), ~1ms) | Overkill |

**Rationale:** FileSearch already fetches and caches the file list on project load. We can reuse this cache for path resolution. No backend changes needed.

### Q2: Search Algorithm (Ranking)?

**Decision: Suffix-based matching with path length ranking**

**Algorithm:**
```typescript
function resolveFilePath(parsedPath: string, fileList: string[]): string[] {
  // 1. Normalize: remove leading ./ or ../
  const normalized = parsedPath.replace(/^\.\.?\//, '')

  // 2. Find matches: paths ending with normalized path
  const matches = fileList.filter(f =>
    f.endsWith(normalized) || f.endsWith('/' + normalized)
  )

  // 3. Rank: shorter paths first (more likely correct)
  return matches.sort((a, b) => a.length - b.length)
}
```

**Examples:**
- `Button.tsx` matches `src/Button.tsx`, `lib/components/Button.tsx`
- `./src/Button.tsx` → normalized to `src/Button.tsx` → exact match
- `components/Button.tsx` matches `frontend/components/Button.tsx`

**Edge cases:**
- Case sensitivity: Case-insensitive match (works on all OS)
- Exact match priority: If exact path exists, return only that

### Q3: Caching Strategy?

**Decision: Shared file list cache with event-based invalidation**

**Cache structure:**
```typescript
// Shared with FileSearch (existing)
const fileListCache = {
  teamId: string,
  files: string[],       // All file paths
  lastFetched: Date,
  isStale: boolean
}

// New: resolution cache (memoization)
const resolutionCache = Map<string, string[]>  // parsedPath → matches
```

**Invalidation triggers:**
1. **Project/team change** → Clear both caches, fetch new list
2. **File not found (404)** → Mark file list stale, refetch
3. **Create/Delete/Rename actions** → Mark file list stale
4. **TTL: 5 minutes** → Mark stale (background refresh)

**Implementation:** Create `useFileListCache` hook shared between FileSearch and path resolution.

### Q4: Multi-match Handling?

**Decision: Modal popup with file list**

**UX Flow:**
1. User clicks terminal path
2. Resolution finds 0, 1, or N matches
3. If N > 1: Show `FileMatchPopup` with list of matches
4. User clicks correct file → opens QuickViewPopup

**Popup design:**
```
┌─────────────────────────────────────┐
│  Multiple files match "Button.tsx"  │
├─────────────────────────────────────┤
│  📄 src/components/Button.tsx       │
│  📄 docs/examples/Button.tsx        │
│  📄 test/__mocks__/Button.tsx       │
└─────────────────────────────────────┘
```

**States:**
- 0 matches: Show error toast "File not found: Button.tsx"
- 1 match: Open QuickViewPopup directly
- N matches: Show FileMatchPopup for user choice

### Q5: Long Path Clickability (Line Wrap)?

**Decision: CSS-based solution + hover tooltip**

**Problem:** Long paths wrap across lines, breaking clickability.

**Solution:**
```css
.terminal-file-link {
  /* Keep path together where possible */
  word-break: break-all;
  /* Ensure full path is clickable as single element */
  display: inline;
  /* Visual indicator */
  text-decoration: underline;
  cursor: pointer;
}
```

**Tooltip:** Show full path on hover for truncated displays.

**Note:** This is primarily a CSS fix. The path parser already captures the full path - it's just the display that breaks.

### Q6: Performance (10K+ files)?

**Decision: Acceptable with current approach**

**Analysis:**
- File list fetch: One-time on project load (~200ms for 10K files)
- In-memory filter: O(n) = ~1ms for 10K strings
- Resolution cache: O(1) for repeated paths

**Optimizations (if needed later):**
- Trie or suffix tree for O(k) lookup (k = path length)
- Web Worker for resolution to avoid main thread blocking
- **Not needed now** - simple filter is fast enough

---

## Architecture

### Component Diagram

```
Terminal Output
       ↓
filePathParser.ts (existing - no changes)
       ↓
NEW: usePathResolver hook
       ├── Uses useFileListCache (shared)
       ├── Calls resolveFilePath()
       └── Returns: { status, matches }
       ↓
TerminalFileLink.tsx (modify)
       ├── status === 'resolved' → QuickViewPopup
       ├── status === 'multiple' → FileMatchPopup (NEW)
       └── status === 'not_found' → Error toast
       ↓
QuickViewPopup.tsx (existing - no changes)
```

### New Components

#### 1. `useFileListCache.ts` (NEW)

Shared cache hook for file list.

```typescript
interface FileListCache {
  files: string[]
  isLoading: boolean
  isStale: boolean
  refetch: () => Promise<void>
}

function useFileListCache(teamId: string): FileListCache
```

#### 2. `usePathResolver.ts` (NEW)

Path resolution hook using cache.

```typescript
interface PathResolution {
  status: 'loading' | 'resolved' | 'multiple' | 'not_found'
  matches: string[]
  resolvedPath?: string  // First match if status === 'resolved'
}

function usePathResolver(teamId: string, parsedPath: string): PathResolution
```

#### 3. `FileMatchPopup.tsx` (NEW)

Multi-match selection popup.

```typescript
interface FileMatchPopupProps {
  isOpen: boolean
  onClose: () => void
  matches: string[]
  onSelect: (path: string) => void
}
```

### Modified Components

#### 4. `TerminalFileLink.tsx` (MODIFY)

Add resolution logic and multi-match handling.

**Current:** Just displays path, calls onClick.
**New:** Resolves path, handles 0/1/N match cases.

---

## Implementation Plan

### Work Items

| WI# | Component | Owner | Size | Dependencies |
|-----|-----------|-------|------|--------------|
| 1 | useFileListCache hook | FE | S | None |
| 2 | usePathResolver hook | FE | M | WI#1 |
| 3 | FileMatchPopup component | FE | S | None |
| 4 | TerminalFileLink integration | FE | M | WI#1, WI#2, WI#3 |
| 5 | CSS long path fix | FE | XS | None |

**Total Size:** M (Medium) - All frontend, no backend changes.

### Suggested Order

1. **WI#1 + WI#5** (parallel) - Cache hook + CSS fix
2. **WI#2 + WI#3** (parallel) - Resolver + Popup
3. **WI#4** - Integration (depends on all above)

---

## Test Strategy

### Unit Tests (TDD)

**useFileListCache.test.ts:**
- Fetches file list on mount
- Returns cached data on subsequent calls
- Refetches when stale
- Handles errors gracefully

**usePathResolver.test.ts:**
- Returns 'loading' initially
- Returns 'resolved' for single match
- Returns 'multiple' for multiple matches
- Returns 'not_found' for zero matches
- Handles case-insensitivity
- Handles edge cases (./path, ../path, absolute)

**FileMatchPopup.test.tsx:**
- Renders list of matches
- Calls onSelect when item clicked
- Closes on ESC key
- Closes on overlay click

**TerminalFileLink.test.tsx (extend):**
- Opens QuickViewPopup for single match
- Opens FileMatchPopup for multiple matches
- Shows toast for not found

### Integration Tests

- Click terminal path → correct file opens
- Click ambiguous path → popup shows → select → correct file opens
- File created → path resolves correctly (cache refresh)

### Coverage Target

Frontend: **80%** (higher than minimum due to critical path)

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance with 50K+ files | Low | Medium | Optimize if needed (trie) |
| Race condition in cache | Medium | Low | Use React Query or proper state |
| Path parsing edge cases | Medium | Medium | Comprehensive tests |

---

## Acceptance Criteria Mapping

| AC | Implementation |
|----|----------------|
| AC1: Resolve relative paths | usePathResolver normalizes ./ paths |
| AC2: Resolve absolute paths | Check if path exists in file list |
| AC3: Resolve subdirectory paths | Suffix matching algorithm |
| AC4: Multi-match popup | FileMatchPopup component |
| AC5: Cache resolved paths | useFileListCache + resolutionCache |
| AC6: Cache at project load | useFileListCache fetches on mount |
| AC7: Update if file not found | 404 triggers cache refetch |
| AC8: Search all project files | Uses /api/files/{team}/list (10K limit) |
| AC9: Clickable paths all formats | Parser unchanged, resolution handles all |
| AC10: Long paths clickable | CSS word-break fix |

---

## Questions for SM/PO

1. **Session memory for multi-match:** Should we remember user's choice for the session? (e.g., user picks `src/Button.tsx` once, always use that for `Button.tsx`)
   - **TL Recommendation:** No for MVP, add later if needed.

2. **Cache TTL:** 5 minutes suggested. Is this appropriate?
   - **TL Recommendation:** Yes, files don't change that often.

---

## Appendix: Code Examples

### resolveFilePath Algorithm

```typescript
export function resolveFilePath(
  parsedPath: string,
  fileList: string[]
): string[] {
  if (!parsedPath || !fileList.length) return []

  // Normalize: remove ./ or ../ prefix
  let normalized = parsedPath
  if (normalized.startsWith('./')) {
    normalized = normalized.slice(2)
  } else if (normalized.startsWith('../')) {
    // Can't resolve parent references without context
    normalized = normalized.replace(/^(\.\.\/)+/, '')
  }

  // Remove leading slash for consistent matching
  normalized = normalized.replace(/^\//, '')

  // Case-insensitive matching
  const normalizedLower = normalized.toLowerCase()

  // Find matches: exact suffix match
  const matches = fileList.filter(filePath => {
    const lower = filePath.toLowerCase()
    return lower === normalizedLower ||
           lower.endsWith('/' + normalizedLower)
  })

  // Rank by path length (shorter = more specific match)
  return matches.sort((a, b) => a.length - b.length)
}
```

### Example Resolutions

| Input | File List | Output |
|-------|-----------|--------|
| `Button.tsx` | `[src/Button.tsx, lib/Button.tsx]` | `[src/Button.tsx, lib/Button.tsx]` |
| `./src/Button.tsx` | `[src/Button.tsx, lib/Button.tsx]` | `[src/Button.tsx]` |
| `components/Button.tsx` | `[frontend/components/Button.tsx]` | `[frontend/components/Button.tsx]` |
| `/full/path/file.ts` | `[full/path/file.ts]` | `[full/path/file.ts]` |

---

**End of Spec**
