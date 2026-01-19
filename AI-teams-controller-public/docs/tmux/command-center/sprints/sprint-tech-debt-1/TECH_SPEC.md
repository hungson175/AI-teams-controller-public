# Technical Spec: Sprint 1 - Tech Debt Remediation

**TL:** Tech Lead | **Date:** 2026-01-11 | **Size:** M (14h)

---

## Overview

Split 2 large route files into smaller modules + complete JWT migration. No breaking changes.

---

## 1. Split file_routes.py (905 lines → 3 modules)

### Target Structure
```
backend/app/api/
├── file_routes/
│   ├── __init__.py          # Re-exports router, combines sub-routers
│   ├── tree_routes.py       # ~200 lines - Tree/list/CRUD operations
│   ├── content_routes.py    # ~150 lines - Read/write file content
│   └── search_routes.py     # ~170 lines - Autocomplete + content search
```

### Module Split

| Module | Endpoints | Lines |
|--------|-----------|-------|
| tree_routes.py | GET /{team_id}/tree, GET /{team_id}/list, POST /{team_id}/create, DELETE /{team_id}/delete, PATCH /{team_id}/rename | ~280 |
| content_routes.py | GET /{team_id}/content, PUT /{team_id}/{path:path} | ~150 |
| search_routes.py | GET /autocomplete, GET /{team_id}/search | ~170 |

### __init__.py Pattern
```python
from fastapi import APIRouter
from .tree_routes import router as tree_router
from .content_routes import router as content_router
from .search_routes import router as search_router

router = APIRouter(prefix="/api/files", tags=["files"])
router.include_router(tree_router)
router.include_router(content_router)
router.include_router(search_router)
```

### Shared Dependencies (keep in each module)
- `from app.services.file_service import get_file_service`
- Pydantic models stay in each module (co-located) OR extract to `file_schemas.py`

---

## 2. Split voice_routes.py (749 lines → 3 modules)

### Target Structure
```
backend/app/api/
├── voice_routes/
│   ├── __init__.py          # Re-exports router, combines sub-routers
│   ├── token_routes.py      # ~70 lines - Token generation endpoints
│   ├── command_routes.py    # ~290 lines - Command processing + helpers
│   └── task_routes.py       # ~200 lines - Task-done + WebSocket feedback
```

### Module Split

| Module | Endpoints | Lines |
|--------|-----------|-------|
| token_routes.py | POST /token, POST /token/soniox | ~70 |
| command_routes.py | POST /command/{team_id}/{role_id}, POST /transcribe + helper functions | ~290 |
| task_routes.py | POST /task-done/{team_id}/{role_id}, WS /ws/feedback/{team_id}/{role_id}, WS /ws/feedback/global | ~200 |

### Helper Functions Location
- `get_pane_id`, `get_tmux_pane_content`, `send_to_tmux_pane`, `correct_voice_command` → **command_routes.py**
- `RoutedCommand` class → **command_routes.py**

---

## 3. JWT Migration (4 legacy endpoints)

### Current State (main.py:90-96)
```python
UNPROTECTED_PREFIXES = (
    "/api/teams",    # TODO: migrate to JWT auth
    "/api/send",     # TODO: migrate to JWT auth
    "/api/state",    # TODO: migrate to JWT auth
    "/api/files",    # TODO: migrate to JWT auth
)
```

### Migration Steps

**Backend:**
1. Add JWT dependency to each route in `__init__.py` (teams, send, state)
2. Add JWT dependency to new `file_routes/__init__.py`
3. Remove these prefixes from `UNPROTECTED_PREFIXES` in main.py
4. Remove `SESSION_TOKEN` fallback after frontend migrates

**Frontend:**
1. Update API client to use `Authorization: Bearer <jwt_token>` header
2. Files: `lib/api.ts`, `contexts/AuthContext.tsx`
3. Ensure token refresh flow handles 401 responses

### JWT Dependency Pattern (existing in codebase)
```python
from app.api.auth_routes import get_current_user_from_token

@router.get("/teams")
async def get_teams(user = Depends(get_current_user_from_token)):
    ...
```

---

## Test Cases (TDD)

### Backend Tests
1. **Route split verification** - All existing endpoints return same responses
2. **Import test** - `from app.api.file_routes import router` still works
3. **JWT auth** - Protected endpoints return 401 without token, 200 with valid token
4. **JWT auth** - Expired token returns 401

### Frontend Tests
1. **API client** - Sends Authorization header on all requests
2. **401 handling** - Triggers token refresh or logout

---

## Code Coverage Requirements

**Backend:** 80% minimum
- Route handlers: 85%
- JWT validation: 90%

**Frontend:** 70% minimum
- API client changes: 80%

---

## Acceptance Criteria

- [ ] file_routes.py split into 3 modules (<300 lines each)
- [ ] voice_routes.py split into 3 modules (<300 lines each)
- [ ] All endpoints use JWT (SESSION_TOKEN removed from UNPROTECTED_PREFIXES)
- [ ] Frontend uses Authorization: Bearer headers
- [ ] All existing tests pass
- [ ] No breaking changes to API contracts

---

## Files to Modify

**Backend:**
- `backend/app/api/file_routes.py` → Split into `file_routes/` directory
- `backend/app/api/voice_routes.py` → Split into `voice_routes/` directory
- `backend/app/main.py` → Update imports, remove legacy prefixes
- `backend/app/api/__init__.py` → Update if needed

**Frontend:**
- `frontend/lib/api.ts` → Add Authorization header
- `frontend/contexts/AuthContext.tsx` → Ensure token in API calls

**Tests:**
- `backend/tests/test_file_routes.py` → Update imports
- `backend/tests/test_voice_routes.py` → Update imports
