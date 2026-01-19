# Technical Spec: Simple File Search (Sprint 1)

## Overview

Add file search capabilities to file browser:
- **Story 1+3 (BE)**: Backend indexing with content search endpoint
- **Story 2 (FE)**: Inline filename fuzzy search (Boss directive: NOT content search)

---

## Story 1: File Indexing System (BE)

### New Endpoint

**GET** `/api/files/{team_id}/search?q={query}`

**Response:**
```json
{
  "results": [
    {"path": "src/app.py", "match_count": 3},
    {"path": "lib/utils.py", "match_count": 1}
  ],
  "total": 2,
  "query": "def process"
}
```

### Caching Strategy (Boss Directive)

```python
# In-memory cache with auto-recovery
_content_cache: Dict[str, ContentCache] = {}

class ContentCache:
    files: Dict[str, str]  # path -> content
    timestamp: float
    TTL = 300  # 5 minutes

def get_or_build_index(team_id: str) -> Dict[str, str]:
    cache = _content_cache.get(team_id)
    if cache and not cache.expired():
        return cache.files

    # Rebuild index (auto-recovery)
    files = build_index(team_id)
    _content_cache[team_id] = ContentCache(files)
    return files

def invalidate_cache(team_id: str):
    """Called on any search error"""
    _content_cache.pop(team_id, None)
```

### Files to Modify

- `backend/app/api/file_routes.py` - Add search endpoint
- `backend/app/services/file_service.py` - Add indexing logic

---

## Story 2: File Search by Name (FE) - REVISED

**Change:** Boss directive - filename search, NOT content search

### Search UI

Inline search box in left panel (above FileTree):
- Text input with search icon
- Fuzzy matching on file/folder names (like Cmd+P but inline)
- Show results inline (replaces file tree while searching)
- Click result → open file in viewer
- Clear button (X) to reset and show file tree

### Key Design

```typescript
// Reuse existing uFuzzy instance (from FileSearch.tsx)
const uf = new uFuzzy({
  intraMode: 1,  // Allow gaps between characters
  intraIns: 1,
  interIns: 3,
})

// Search using useFileListCache (already fetches file list)
const { files } = useFileListCache(teamId)
const results = uf.search(files, query)
```

### Behavior

1. **Empty query**: Show file tree (normal view)
2. **Has query**: Show fuzzy search results (inline list)
3. **Click result**: Call `onFileSelect(path)`, clear query
4. **Clear button**: Reset query, return to file tree

### Files to Modify

- `frontend/components/file-browser/FileNameSearch.tsx` (new) - Inline search component
- `frontend/components/file-browser/FileBrowser.tsx` - Replace ContentSearch with FileNameSearch

### Reuse Existing Code

- `useFileListCache` hook - file list fetching (FIX: map f.path)
- `uFuzzy` library - already installed, configured in FileSearch.tsx
- FileSearch.tsx - reference for uFuzzy usage pattern

---

## Story 3: Exclusion Configuration (BE)

### .gitignore Parser

```python
def parse_gitignore(project_root: Path) -> List[Pattern]:
    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        return []

    patterns = []
    for line in gitignore.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("!"):
            patterns.append(NegationPattern(line[1:]))
        else:
            patterns.append(GlobPattern(line))
    return patterns
```

### Hardcoded Exclusions

```python
EXCLUDED_DIRS = {"node_modules", ".git", "__pycache__", "venv", ".venv", "dist", "build", ".next"}
EXCLUDED_EXTENSIONS = {".pyc", ".log", ".lock"}
```

### Files to Modify

- `backend/app/services/file_service.py` - Add gitignore parsing
- `backend/app/services/exclusion_patterns.py` (new) - Pattern matching

---

## Test Cases

### Backend
1. Search finds substring matches
2. Match count is accurate per file
3. .gitignore patterns exclude files
4. Hardcoded exclusions work
5. Cache hit returns cached results
6. Cache miss rebuilds index
7. Error invalidates cache (auto-recovery)

### Frontend (Story 2 - File Name Search)
1. Search input visible above file tree
2. Typing triggers fuzzy search on file names
3. Results show matching file paths
4. Click result opens file in viewer
5. Empty query shows file tree (normal view)
6. "No results" shown when no matches
7. Clear button resets search and shows file tree

---

## Coverage Requirements

**Backend:** 80% minimum
**Frontend:** 70% minimum

