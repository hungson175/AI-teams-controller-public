# P0 Technical Spec: Cmd+P Filename-Prioritized Ranking

**Author:** TL
**Date:** 2026-01-09
**Priority:** P0 (Boss escalation)
**Size:** XS (~15 lines)

## Problem

Cmd+P search returns wrong results for exact filename searches.
- Search: `workflow.md`
- Expected: File named `workflow.md` as first result
- Actual: Random files with 'workflow' in path appear first

## Root Cause

`FileSearch.tsx` line 59 uses uFuzzy on full paths without filename prioritization.
uFuzzy ranks by overall fuzzy match, not filename relevance.

## Solution

Re-rank uFuzzy results to prioritize filename matches.

## Implementation

### File: `frontend/components/file-browser/FileSearch.tsx`

Replace lines 65-71 with:

```typescript
// Use order if available (sorted by relevance)
const sortedIndexes = order || indexes

// Re-rank to prioritize filename matches (Boss requirement)
const rerankedIndexes = [...sortedIndexes].sort((a, b) => {
  const fileA = files[a].path.split('/').pop()?.toLowerCase() || ''
  const fileB = files[b].path.split('/').pop()?.toLowerCase() || ''
  const q = query.toLowerCase()

  // 1. Exact filename match first
  if (fileA === q && fileB !== q) return -1
  if (fileB === q && fileA !== q) return 1

  // 2. Filename starts with query
  if (fileA.startsWith(q) && !fileB.startsWith(q)) return -1
  if (fileB.startsWith(q) && !fileA.startsWith(q)) return 1

  // 3. Filename contains query
  if (fileA.includes(q) && !fileB.includes(q)) return -1
  if (fileB.includes(q) && !fileA.includes(q)) return 1

  // 4. Keep uFuzzy order for remaining
  return 0
})

return rerankedIndexes.slice(0, 50).map(idx => ({
  item: files[idx],
  index: idx,
  highlight: info?.idx?.[order ? rerankedIndexes.indexOf(idx) : indexes.indexOf(idx)]
}))
```

## Test Cases

1. Search `workflow.md` → `workflow.md` is first result
2. Search `Button` → `Button.tsx` before `components/ui/button/index.ts`
3. Search `test` → `test.ts` before `utils/testing/helpers.ts`
4. Fuzzy search `wrkflw` still works (uFuzzy fallback)

## Acceptance Criteria

1. Exact filename match appears as first result
2. Filename prefix matches appear before directory matches
3. Fuzzy matching still works for non-exact queries
4. No performance regression (sort is O(n log n) on max 50 items)
