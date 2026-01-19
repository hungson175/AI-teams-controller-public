# Technical Spec: Terminal File Path Click Popup (Phase 2)

**TL**: 2026-01-08
**Sprint Backlog**: `SPRINT_BACKLOG.md`
**Stories**: 1-3 (Story 4 = straightforward UI, no spec needed)

---

## Story 1: Enhanced Path Detection Regex

### Current Issue
- `filePathParser.ts:71` requires `./ ` or `../` or `/` prefix
- Paths like `src/components/Button.tsx` don't match (no prefix)
- Long wrapped paths break detection

### Design

**Fix:** Make path prefix OPTIONAL (currently required):
```typescript
// FROM: `(?:\./|\.\./|/)?[\\w./-]+`  - prefix optional but regex broken
// TO:   `(?:\./|\.\./|/)?[\\w.-]+(?:/[\\w.-]+)*`  - proper optional prefix
```

**Edge Cases to Handle:**
1. No prefix: `src/components/Button.tsx` → MATCH
2. Relative: `./Button.tsx`, `../lib/util.ts` → MATCH
3. Absolute: `/home/user/file.ts` → MATCH
4. With line:col: `file.ts:42:10` → MATCH
5. URLs: `http://example.com` → NO MATCH (already handled)
6. Flags: `--config` → NO MATCH (add negative lookahead for `--`)

**Files to Modify:**
- `frontend/lib/filePathParser.ts`

**Tests:**
- Edge cases 1-6 above
- Wrapped long paths (multi-line terminal output)

---

## Story 2: Improved Path Resolution

### Current Issue
- `usePathResolver.ts` uses simple suffix matching + length ranking
- No fuzzy matching for ambiguous paths
- No directory context consideration

### Design

**Scoring Algorithm (replace length-only ranking):**

```typescript
function scorePath(match: string, parsedPath: string): number {
  let score = 0

  // 1. Exact filename match (+100)
  const matchFilename = match.split('/').pop()
  const parsedFilename = parsedPath.split('/').pop()
  if (matchFilename === parsedFilename) score += 100

  // 2. Path segment overlap (+20 per segment)
  const matchSegments = match.toLowerCase().split('/')
  const parsedSegments = parsedPath.toLowerCase().split('/')
  const overlap = parsedSegments.filter(s => matchSegments.includes(s)).length
  score += overlap * 20

  // 3. Shorter paths preferred (+10 penalty per extra segment)
  score -= (matchSegments.length - parsedSegments.length) * 10

  return score
}
```

**Files to Modify:**
- `frontend/hooks/usePathResolver.ts`

**Tests:**
- Exact filename match ranks highest
- Directory context improves ranking
- Shorter paths beat longer paths (same filename)

---

## Story 3: Performance Optimization

### Current Issue
- No debouncing on path resolution
- No result caching
- Resolution runs on every render

### Design

**1. Debouncing (150ms):**
- Add `useDebouncedValue` for `parsedPath` in `usePathResolver`
- Only resolve after user stops typing/clicking

**2. Resolution Cache (Map with TTL):**
```typescript
const resolutionCache = new Map<string, { result: string[], timestamp: number }>()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

function getCachedResolution(key: string): string[] | null {
  const cached = resolutionCache.get(key)
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.result
  }
  return null
}
```

**3. Memoization:**
- Already using `useMemo` - ensure deps are correct

**Files to Modify:**
- `frontend/hooks/usePathResolver.ts`

**Tests:**
- Same path twice → cache hit (no re-computation)
- Cache expires after 5 minutes
- Debounce prevents rapid re-resolution

---

## Code Coverage Requirements

**Frontend:** 70% minimum
- Business logic (scoring, caching): 85%
- Regex parsing: 90%
- UI components: 65%

---

## Test Categories (TDD)

| Story | Test Count | Key Cases |
|-------|-----------|-----------|
| 1 | 8 | No-prefix paths, edge cases 1-6, wrapped paths |
| 2 | 6 | Scoring algorithm, segment overlap, ranking |
| 3 | 5 | Cache hit/miss, TTL expiry, debounce |

**Total: ~19 tests**

---

## Acceptance Criteria Summary

| AC | Story | Description |
|----|-------|-------------|
| 1.1-1.5 | 1 | Path detection (abs, rel, line:col, wrapped, no false positives) |
| 2.1-2.4 | 2 | Scoring (exact match, context, uFuzzy, confidence) |
| 3.1-3.4 | 3 | Performance (debounce, cache, progressive, no lag) |
