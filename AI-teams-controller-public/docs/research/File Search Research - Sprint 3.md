# File Search Research - Sprint 3

**Author**: TL (Tech Lead)
**Date**: 2025-12-29
**Purpose**: Research file name search technology for File Browser feature

---

## 1. How IDEs Implement File Search

### VS Code (Cmd+P / Quick Open)
- Uses custom fuzzy matching algorithm (NOT Levenshtein distance)
- Optimized for command palettes and quick file navigation
- Supports toggling between fuzzy and continuous matching
- Implementation in Rust: [code-fuzzy-match](https://github.com/D0ntPanic/code-fuzzy-match)

### IntelliJ IDEA
- Pre-indexes file names on project open
- Uses in-memory index for instant results
- Supports CamelCase matching (e.g., "FBP" → "FileBrowserPanel")

### Sublime Text
- Goto Anything (Cmd+P) uses fuzzy matching
- Indexes file names in background
- Known for extremely fast response times

**Key Insight**: All major IDEs use file name indexing combined with optimized fuzzy matching algorithms (not generic string distance).

---

## 2. JavaScript Fuzzy Search Libraries

| Library | Size | Performance | Best For |
|---------|------|-------------|----------|
| **uFuzzy** | ~6KB | Fastest | Large datasets, file search |
| **Fuse.js** | ~15KB | Good | Feature-rich, weighted search |
| **fzf.js** | ~10KB | Very Fast | fzf algorithm port |
| **microfuzz** | ~2KB | Fast | Lightweight, already in project |

### uFuzzy - RECOMMENDED
- Best-in-class performance for large datasets
- Minimal memory overhead
- Excellent result quality/ordering
- Demo: [Interactive comparison](https://leeoniya.github.io/uFuzzy/demos/compare.html)

### Fuse.js
- Most popular (npm downloads)
- More features but slower on large datasets
- Better with `ignoreFieldNorm: true` for file search

### Why Not microfuzz?
We already use microfuzz for Sprint 2 command autocomplete. For file search with 1000s of files, uFuzzy offers better performance and result ranking.

---

## 3. Performance Considerations

### Indexing vs Live Search

| Approach | Pros | Cons | Use When |
|----------|------|------|----------|
| **Live Search** | Simple, no index maintenance | Slower for huge directories | < 10K files |
| **Pre-Indexing** | Instant results | Complex, storage overhead | > 100K files |
| **Hybrid** | Balanced | Moderate complexity | 10K - 100K files |

### Typical Project Sizes
- Small project: 100-500 files
- Medium project: 1K-5K files
- Large project: 5K-20K files
- Monorepo: 50K-500K files

**For our use case**: Most tmux agent projects are small-medium. Live search with uFuzzy should handle 10K+ files instantly.

### Memory Considerations
- File list of 10K paths: ~500KB - 1MB
- uFuzzy index: ~200KB additional
- Total: < 2MB for typical large project

---

## 4. Frontend-Only vs Backend API

### Option A: Frontend-Only
```
Backend: GET /api/files/{team}/list → flat file list
Frontend: Cache list + uFuzzy search
```
**Pros**: Instant results (no network latency), simpler architecture
**Cons**: Initial load time, memory usage on client

### Option B: Backend API
```
Frontend: Search query → Backend API → Search results
```
**Pros**: Handles huge directories, less client memory
**Cons**: Network latency (50-200ms per keystroke), server load

### Option C: Hybrid (RECOMMENDED)
```
1. Backend: Provide flat file list on project open
2. Frontend: Cache + uFuzzy for instant search
3. Pagination: Lazy load for directories > 5K files
```
**Pros**: Best UX (instant), scalable, manageable memory
**Cons**: Slightly more complex implementation

---

## 5. Recommended Approach

### Architecture
```
┌─────────────────────────────────────────────────────┐
│ File Browser Component                              │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Search Input (Cmd+P style)                      │ │
│ └─────────────────────────────────────────────────┘ │
│                      │                              │
│                      ▼                              │
│ ┌─────────────────────────────────────────────────┐ │
│ │ uFuzzy (client-side)                            │ │
│ │ - Searches cached file list                     │ │
│ │ - Returns ranked results instantly              │ │
│ └─────────────────────────────────────────────────┘ │
│                      │                              │
│                      ▼                              │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Results List (virtualized for performance)      │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘

Backend: GET /api/files/{team}/list?flat=true
Returns: ["src/app.py", "src/utils.py", "README.md", ...]
```

### Implementation Steps
1. **Backend**: Add flat file list endpoint (recursive, excludes content)
2. **Frontend**: Add uFuzzy dependency (~6KB)
3. **Frontend**: Create file search hook with caching
4. **Frontend**: Build search UI component (input + virtualized list)
5. **UX**: Add keyboard navigation (arrow keys, enter to open)

### API Contract
```
GET /api/files/{team}/list?flat=true&limit=10000

Response:
{
  "files": [
    { "path": "src/app.py", "isDir": false },
    { "path": "src/components/", "isDir": true },
    ...
  ],
  "total": 1234,
  "truncated": false
}
```

---

## 6. Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Library | **uFuzzy** | Best performance for file search |
| Approach | **Frontend + Cache** | Instant results, good UX |
| Backend | Flat file list API | Provides data, doesn't do search |
| Pagination | Lazy load > 5K files | Memory management |

### Bundle Impact
- uFuzzy: +6KB (gzipped: ~2.5KB)
- Total new dependencies: minimal

### Estimated Effort
- Backend (flat list endpoint): 1-2 hours
- Frontend (search component): 4-6 hours
- Tests: 2-3 hours
- **Total**: ~1 sprint

---

## Sources

- [uFuzzy GitHub](https://github.com/leeoniya/uFuzzy) - Performance benchmarks
- [Fuse.js](https://www.fusejs.io/) - Official docs
- [VS Code Fuzzy Match (Rust)](https://github.com/D0ntPanic/code-fuzzy-match) - Algorithm reference
- [JavaScript Fuzzy Search Comparison](https://themeselection.com/javascript-fuzzy-search/) - Library overview
- [uFuzzy vs Fuse.js Comparison](https://npm-compare.com/@leeoniya/ufuzzy,fuse.js,fuzzy,fuzzysearch,fuzzyset.js,string-similarity) - npm stats

---

**TL Recommendation**: Use **uFuzzy** with **frontend caching** approach. Best UX (instant results) with minimal complexity. Our existing file service can provide the flat list with minor modifications.
