# Technical Specs: Sprint 2 - Terminal Autocomplete

**Author**: TL (Tech Lead)
**Date**: 2025-12-29
**Sprint**: 2 - Terminal-like Input with Autocomplete

---

## Overview

Enhance the existing TerminalPanel autocomplete with fuzzy matching and real file system path completion via backend API.

**Tech Decision**: Option 2 - Custom Implementation with microfuzz (2KB)

**Rationale**: TerminalPanel already has 80% of autocomplete functionality. Adding fuzzy search and backend API integration is minimal effort compared to replacing with xterm.js (200KB, full rewrite).

---

## Story 1: Fuzzy Search for Command Suggestions

### Overview

Replace the current `startsWith` prefix matching with fuzzy matching using `@nozbe/microfuzz` library for smarter command completion.

### Current State

**File**: `frontend/components/controller/TerminalPanel.tsx` (lines 166-186)

```typescript
// Current: Simple prefix matching
const filteredSuggestions = (() => {
  if (!isTerminalMode || inputValue.length < 1) return []

  if (isPathInput) {
    return PATH_SUGGESTIONS
      .filter(path => path.toLowerCase().startsWith(prefix.toLowerCase()))
      .slice(0, 5)
  } else if (inputValue.length >= 2) {
    return COMMAND_SUGGESTIONS
      .filter(cmd => cmd.toLowerCase().startsWith(inputValue.toLowerCase()))
      .slice(0, 5)
  }
  return []
})()
```

### Architecture

#### Frontend Changes

**New dependency**: `pnpm add @nozbe/microfuzz`

**File**: `frontend/lib/fuzzy-search.ts` (NEW)

```typescript
import { createFuzzySearch } from '@nozbe/microfuzz'

export interface FuzzyResult<T> {
  item: T
  score: number
}

/**
 * Create a fuzzy search function for a list of strings
 */
export function createCommandSearch(commands: string[]) {
  const search = createFuzzySearch(commands)

  return (query: string, limit: number = 5): string[] => {
    if (!query || query.length < 1) return []

    const results = search(query)
    return results
      .slice(0, limit)
      .map(result => result.item)
  }
}

/**
 * Fuzzy search with highlighting support
 * Returns matches with indices for highlighting
 */
export function fuzzySearchWithHighlight(
  items: string[],
  query: string,
  limit: number = 5
): Array<{ item: string; highlighted: string }> {
  const search = createFuzzySearch(items, { getText: (item) => item })
  const results = search(query)

  return results.slice(0, limit).map(result => ({
    item: result.item,
    highlighted: highlightMatches(result.item, result.matches)
  }))
}

/**
 * Highlight matched characters with <mark> tags
 */
function highlightMatches(text: string, matches: number[][]): string {
  if (!matches || matches.length === 0) return text

  let result = ''
  let lastIndex = 0

  for (const [start, end] of matches) {
    result += text.slice(lastIndex, start)
    result += `<mark>${text.slice(start, end + 1)}</mark>`
    lastIndex = end + 1
  }
  result += text.slice(lastIndex)

  return result
}
```

**File**: `frontend/components/controller/TerminalPanel.tsx`

Update the `filteredSuggestions` logic:

```typescript
import { createCommandSearch } from '@/lib/fuzzy-search'

// Create search function once (outside component or useMemo)
const commandSearch = createCommandSearch(COMMAND_SUGGESTIONS)

// Replace filteredSuggestions logic
const filteredSuggestions = useMemo(() => {
  if (!isTerminalMode || inputValue.length < 1) return []

  if (isPathInput) {
    // Path suggestions will come from backend API (Story 2)
    return [] // Placeholder - Story 2 will implement
  } else if (inputValue.length >= 2) {
    // Use fuzzy search for commands
    return commandSearch(inputValue, 5)
  }
  return []
}, [isTerminalMode, inputValue, isPathInput])
```

### Test Cases (TDD)

#### Unit Tests (`fuzzy-search.test.ts`)

1. **returns empty array for empty query**
   - Input: `""`
   - Expected: `[]`

2. **matches exact prefix**
   - Commands: `["git status", "git diff", "git commit"]`
   - Query: `"git s"`
   - Expected: `["git status"]` as first result

3. **matches fuzzy (non-contiguous)**
   - Commands: `["git commit", "git checkout"]`
   - Query: `"gco"`
   - Expected: `["git commit"]` or `["git checkout"]` (both match g-c-o)

4. **respects limit parameter**
   - Commands: 20 items
   - Query: matches 10
   - Limit: 5
   - Expected: 5 results

5. **ranks better matches higher**
   - Commands: `["run tests", "run build", "refactor"]`
   - Query: `"run"`
   - Expected: `["run tests", "run build"]` before `["refactor"]`

6. **case insensitive matching**
   - Commands: `["Git Status", "GIT DIFF"]`
   - Query: `"git"`
   - Expected: Both should match

#### Integration Tests (`TerminalPanel.test.tsx`)

7. **shows fuzzy matched suggestions**
   - Type `"gco"` in terminal mode
   - Expect suggestions containing "commit" or "checkout"

8. **updates suggestions as user types**
   - Type `"g"`, then `"gi"`, then `"git"`
   - Suggestions should narrow with each keystroke

### Acceptance Criteria

- [ ] Fuzzy matching works for non-contiguous characters (e.g., "gco" matches "git commit")
- [ ] Better matches ranked higher in suggestions
- [ ] Existing Tab/Arrow key navigation still works
- [ ] No performance degradation with 20+ commands
- [ ] Bundle size increase < 3KB

---

## Story 2: Backend Path Autocomplete API

### Overview

Create a backend API endpoint that returns real file system path completions for the selected team's project directory.

### Architecture

#### Backend Changes

**File**: `backend/app/api/file_routes.py` (add new endpoint)

```python
from fastapi import APIRouter, Query, HTTPException
from pathlib import Path
import os

router = APIRouter()

# Maximum results to return
MAX_AUTOCOMPLETE_RESULTS = 10

# Maximum depth to search
MAX_DEPTH = 3

@router.get("/files/autocomplete")
async def autocomplete_path(
    path: str = Query(..., description="Partial path to complete"),
    team: str = Query(..., description="Team/project ID for base directory"),
    limit: int = Query(MAX_AUTOCOMPLETE_RESULTS, le=20)
):
    """
    Autocomplete file/directory paths within a team's project directory.

    Security:
    - Paths are restricted to team's project directory
    - No path traversal (../) allowed
    - Symlinks are not followed outside project
    """
    # Get team's project directory from PANE_ROLES or session config
    base_dir = get_team_project_dir(team)
    if not base_dir:
        raise HTTPException(status_code=404, detail=f"Team '{team}' not found")

    # Sanitize path - prevent traversal
    if ".." in path:
        raise HTTPException(status_code=400, detail="Path traversal not allowed")

    # Resolve the partial path
    partial = Path(path)

    # Determine search directory and prefix
    if path.endswith("/"):
        search_dir = base_dir / partial
        prefix = ""
    else:
        search_dir = base_dir / partial.parent if partial.parent != Path(".") else base_dir
        prefix = partial.name

    # Validate search_dir is within base_dir
    try:
        search_dir = search_dir.resolve()
        base_resolved = Path(base_dir).resolve()
        if not str(search_dir).startswith(str(base_resolved)):
            raise HTTPException(status_code=400, detail="Path outside project directory")
    except Exception:
        return {"completions": []}

    if not search_dir.exists() or not search_dir.is_dir():
        return {"completions": []}

    # Find matching entries
    completions = []
    try:
        for entry in search_dir.iterdir():
            if entry.name.startswith("."):
                continue  # Skip hidden files
            if prefix and not entry.name.lower().startswith(prefix.lower()):
                continue

            # Build completion path (relative to input)
            if path.endswith("/"):
                completion = path + entry.name
            else:
                parent = str(partial.parent)
                if parent == ".":
                    completion = entry.name
                else:
                    completion = f"{parent}/{entry.name}"

            # Add trailing slash for directories
            if entry.is_dir():
                completion += "/"

            completions.append({
                "path": completion,
                "isDir": entry.is_dir(),
                "name": entry.name
            })

            if len(completions) >= limit:
                break

    except PermissionError:
        pass

    # Sort: directories first, then alphabetically
    completions.sort(key=lambda x: (not x["isDir"], x["name"].lower()))

    return {"completions": completions}


def get_team_project_dir(team: str) -> str | None:
    """Get the project directory for a team from session config."""
    # Implementation depends on how team directories are configured
    # Option 1: Read from PANE_ROLES.md
    # Option 2: Use tmux session working directory
    # Option 3: Configuration file

    # For now, use tmux session start directory
    import subprocess
    result = subprocess.run(
        ["tmux", "display-message", "-t", team, "-p", "#{session_path}"],
        capture_output=True, text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None
```

**File**: `backend/app/main.py`

Add the new route:

```python
from app.api.file_routes import router as file_router

app.include_router(file_router, prefix="/api", tags=["files"])
```

#### Frontend Changes

**File**: `frontend/components/controller/TerminalPanel.tsx`

Add API integration for path completion:

```typescript
// State for async path suggestions
const [pathSuggestions, setPathSuggestions] = useState<string[]>([])
const [isLoadingPaths, setIsLoadingPaths] = useState(false)

// Debounced path autocomplete
const fetchPathSuggestions = useMemo(
  () =>
    debounce(async (partial: string, team: string) => {
      if (!partial || partial.length < 1) {
        setPathSuggestions([])
        return
      }

      setIsLoadingPaths(true)
      try {
        const res = await fetch(
          `/api/files/autocomplete?path=${encodeURIComponent(partial)}&team=${encodeURIComponent(team)}`
        )
        if (res.ok) {
          const data = await res.json()
          setPathSuggestions(data.completions.map((c: any) => c.path))
        }
      } catch (e) {
        console.error("Path autocomplete error:", e)
      } finally {
        setIsLoadingPaths(false)
      }
    }, 200),
  []
)

// Trigger path fetch when input changes
useEffect(() => {
  if (isTerminalMode && isPathInput && selectedTeam) {
    fetchPathSuggestions(inputValue, selectedTeam)
  }
}, [inputValue, isTerminalMode, isPathInput, selectedTeam])

// Update filteredSuggestions to use pathSuggestions
const filteredSuggestions = useMemo(() => {
  if (!isTerminalMode || inputValue.length < 1) return []

  if (isPathInput) {
    return pathSuggestions.slice(0, 5)
  } else if (inputValue.length >= 2) {
    return commandSearch(inputValue, 5)
  }
  return []
}, [isTerminalMode, inputValue, isPathInput, pathSuggestions])
```

### API Contract

**Endpoint**: `GET /api/files/autocomplete`

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| path | string | Yes | Partial path to complete |
| team | string | Yes | Team/project ID |
| limit | int | No | Max results (default: 10, max: 20) |

**Response**:
```json
{
  "completions": [
    { "path": "src/", "isDir": true, "name": "src" },
    { "path": "setup.py", "isDir": false, "name": "setup.py" }
  ]
}
```

**Error Responses**:
- `400`: Path traversal attempted
- `404`: Team not found

### Test Cases (TDD)

#### Backend Tests (`test_file_routes.py`)

1. **returns directory completions**
   - Path: `"src/"`
   - Expected: List of items in src/ directory

2. **returns file completions with prefix**
   - Path: `"src/ma"`
   - Expected: Files starting with "ma" (e.g., `main.py`)

3. **adds trailing slash to directories**
   - Path: `"sr"`
   - Expected: `"src/"` (with trailing slash)

4. **rejects path traversal**
   - Path: `"../../../etc/passwd"`
   - Expected: 400 error

5. **returns empty for nonexistent path**
   - Path: `"nonexistent/"`
   - Expected: `{"completions": []}`

6. **respects limit parameter**
   - Path: `""` (root), limit: 3
   - Expected: Max 3 results

7. **hides hidden files (dotfiles)**
   - Path: `""`
   - Expected: No `.git`, `.env`, etc.

8. **sorts directories before files**
   - Path: `""`
   - Expected: Directories appear first

#### Frontend Integration Tests

9. **fetches path completions from API**
   - Type `"src/"` in terminal mode
   - Verify API called with correct params

10. **debounces rapid typing**
    - Type `"s"`, `"sr"`, `"src"` rapidly
    - Verify only one API call after debounce

11. **shows loading state during fetch**
    - Start typing path
    - Verify loading indicator shown

### Security Considerations

1. **Path Traversal Prevention**: Reject any path containing `..`
2. **Directory Restriction**: Only allow paths within team's project directory
3. **Symlink Safety**: Do not follow symlinks outside project
4. **Input Sanitization**: Validate and escape path components
5. **Rate Limiting**: Consider adding rate limit for autocomplete endpoint

### Acceptance Criteria

- [ ] Real file/directory paths from project appear in suggestions
- [ ] Directories have trailing slash in suggestions
- [ ] Directories sorted before files
- [ ] Hidden files (.git, .env) not shown
- [ ] Path traversal attempts blocked
- [ ] API response < 100ms for typical directories
- [ ] Debounced to prevent excessive API calls

---

## Implementation Order

**Recommendation**: Implement Story 1 FIRST (frontend fuzzy search), then Story 2 (backend API).

**Story 1 (Fuzzy Search)**:
1. FE: Add microfuzz dependency (2 min)
2. FE: Create fuzzy-search.ts utility (30 min)
3. FE: Update TerminalPanel filteredSuggestions (30 min)
4. Tests: Unit + Integration (1 hour)

**Story 2 (Path API)**:
1. BE: Create file_routes.py endpoint (1 hour)
2. BE: Add security checks (30 min)
3. FE: Add API integration to TerminalPanel (1 hour)
4. Tests: Backend + Frontend (1.5 hours)

---

## Files to Modify

### Story 1
- `frontend/package.json` (add @nozbe/microfuzz)
- `frontend/lib/fuzzy-search.ts` (NEW)
- `frontend/lib/fuzzy-search.test.ts` (NEW)
- `frontend/components/controller/TerminalPanel.tsx`
- `frontend/components/controller/TerminalPanel.test.tsx`

### Story 2
- `backend/app/api/file_routes.py` (add endpoint)
- `backend/app/main.py` (register router)
- `backend/tests/test_file_routes.py` (NEW or extend)
- `frontend/components/controller/TerminalPanel.tsx`
- `frontend/components/controller/TerminalPanel.test.tsx`

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Path traversal attack | Reject `..` in paths, validate resolved path within project |
| Large directory slow response | Limit results (max 20), stop iteration early |
| Stale suggestions on fast typing | Debounce API calls (200ms) |
| microfuzz bundle size | Verified 2KB, acceptable |

---

**TL Sign-off**: Specs complete. Ready for FE/BE implementation with TDD.
