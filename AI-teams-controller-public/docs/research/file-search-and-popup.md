# File Search Algorithm Research

**Date**: 2026-01-08
**Task**: Research file search algorithms for "Intelligent File Path Search + Click Popup" feature
**Status**: Research Complete - Awaiting Boss Review

---

## Executive Summary

Research reveals the project **already has a comprehensive implementation** using uFuzzy + microfuzz. Recommendation: leverage existing implementation with minor enhancements rather than rebuild.

---

## Algorithm Comparison

| Library | Bundle Size | Speed | Best For | Stars |
|---------|-------------|-------|----------|-------|
| **uFuzzy** | 7.5KB | 5ms/162K items | File paths, large datasets | 2,952 |
| **fzf-for-js** | ~15KB | Fast | Comprehensive scoring | 947 |
| **Fuse.js** | 12-19KB | Moderate | Feature-rich, weighted search | 19,864 |
| **FlexSearch** | 5-7KB | Fastest indexing | Very large datasets | 13,527 |
| **microfuzz** | ~1KB | Fast | Simple search + highlighting | - |

---

## Algorithm Deep Dive

### uFuzzy (Recommended for File Paths)

**Why it's ideal:**
- Zero string allocations during search
- Intra-mode (within word) + Inter-mode (between words) matching
- Configurable: `intraMode: 0|1`, `interSplit`, `interLft/Rht`
- 5ms for 162K phrases benchmark

**Scoring factors:**
- Consecutive character matches
- Word boundary alignment
- Path segment awareness

### fzf Algorithm (VS Code-style)

**Scoring components:**
- Smith-Waterman variation for alignment
- Gap penalties (first gap more expensive)
- Consecutive match bonus
- Camel case and word boundary bonuses
- Position-based scoring (earlier = better)

### VS Code Quick Open Pattern

**Key techniques:**
1. Matrix-based fuzzy scoring
2. Multi-level caching (file list, search results)
3. 75-250ms debouncing
4. Progressive loading for large workspaces
5. Last-used file prioritization

---

## Existing Project Implementation

**Already implemented in this project:**

| Component | File | Purpose |
|-----------|------|---------|
| Fuzzy search | `frontend/lib/fuzzy-search.ts` | uFuzzy + microfuzz integration |
| File cache | `frontend/hooks/useFileListCache.ts` | Shared file list caching |
| Path resolver | `frontend/hooks/usePathResolver.ts` | Suffix matching algorithm |
| Clickable links | `frontend/components/terminal/TerminalFileLink.tsx` | Terminal file link detection |
| Quick view | `frontend/components/terminal/QuickViewPopup.tsx` | File content popup |
| Multi-match | `frontend/components/terminal/FileMatchPopup.tsx` | Selection for ambiguous paths |
| Cmd+P dialog | `frontend/components/file-browser/FileSearch.tsx` | File search modal |

**Current approach:**
- uFuzzy for file path fuzzy matching
- microfuzz for command search with highlighting
- Suffix matching for path resolution (e.g., "types.ts" finds "components/file-browser/types.ts")
- Length-based ranking for multiple matches

---

## Proposed Solution

### Option A: Enhance Existing (Recommended)

Leverage current uFuzzy + microfuzz implementation with:

1. **VS Code-style scoring enhancements**
   - Add camelCase bonus
   - Word boundary scoring
   - Position weighting (earlier matches rank higher)

2. **Performance optimizations**
   - Add debouncing (150ms recommended)
   - Implement result caching with TTL
   - Progressive search for large results

3. **UX improvements**
   - Last-used file prioritization
   - Frecency scoring (frequency + recency)

**Effort**: Low - builds on existing code

### Option B: Replace with fzf-for-js

Switch to fzf algorithm for more sophisticated matching:

**Pros:**
- Better scoring algorithm
- TypeScript native
- Proven in fzf CLI (widely used)

**Cons:**
- Larger bundle (~15KB vs 7.5KB)
- Requires rewriting existing integration
- May be overkill for file path search

**Effort**: Medium - requires migration

### Option C: Build Custom (Not Recommended)

Implement VS Code-style algorithm from scratch.

**Effort**: High - not justified given existing solutions

---

## Recommendation

**Go with Option A: Enhance Existing Implementation**

Rationale:
1. Project already has working uFuzzy integration
2. uFuzzy benchmarks (5ms/162K items) exceed our needs
3. Low risk - incremental improvements vs rebuild
4. Can always switch to fzf later if needed

### Specific Enhancements for Terminal File Links

1. **Path detection regex** - Already exists in TerminalFileLink.tsx
2. **Hover popup** - QuickViewPopup.tsx ready
3. **Multi-match disambiguation** - FileMatchPopup.tsx ready
4. **Keyboard navigation** - Add if not present

---

## GitHub References

| Repository | Stars | Description |
|------------|-------|-------------|
| [uFuzzy](https://github.com/leeoniya/uFuzzy) | 2,952 | Tiny, efficient fuzzy search |
| [fzf-for-js](https://github.com/ajitid/fzf-for-js) | 947 | FZF algorithm in JavaScript |
| [Fuse.js](https://github.com/krisk/Fuse) | 19,864 | Lightweight fuzzy-search |
| [FlexSearch](https://github.com/nextapps-de/flexsearch) | 13,527 | Full-text search library |
| [xterm.js](https://github.com/xtermjs/xterm.js) | 19,691 | Terminal for web (reference) |

---

## Next Steps (Post-Approval)

1. Review existing implementation files
2. Identify specific enhancement points
3. Create technical spec for FE implementation
4. Test with realistic file counts (1K-10K files)
