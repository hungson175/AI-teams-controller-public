# -*- coding: utf-8 -*-
"""File search and autocomplete routes.

Contains endpoints for:
- GET /autocomplete - Path autocomplete for file browser
- GET /{team_id}/search - Content search across files
"""

import logging
from pathlib import Path
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.auth_routes import get_current_user_from_token
from app.models.auth_schemas import UserResponse
from app.services.file_service import get_file_service

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================
# Sprint 2 Story 2: Path Autocomplete API
# ============================================================

# Configuration
MAX_AUTOCOMPLETE_RESULTS = 10


class PathCompletion(BaseModel):
    """Single path completion result."""
    path: str
    isDir: bool
    name: str


class AutocompleteResponse(BaseModel):
    """Autocomplete API response."""
    completions: List[PathCompletion]


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_path(
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    path: str = Query("", description="Partial path to complete"),
    team: str = Query(..., description="Team/project ID for base directory"),
    limit: int = Query(MAX_AUTOCOMPLETE_RESULTS, le=20, description="Max results")
) -> AutocompleteResponse:
    """
    Autocomplete file/directory paths within a team's project directory.

    Security:
    - Paths are restricted to team's project directory
    - No path traversal (../) allowed
    - Hidden files (dotfiles) are excluded
    - Symlinks outside project are not followed

    Args:
        path: Partial path to complete (e.g., "src/ma" to find "src/main.py")
        team: Team ID to determine project root
        limit: Maximum number of results (default: 10, max: 20)

    Returns:
        AutocompleteResponse with list of matching completions
    """
    service = get_file_service()

    # Resolve project root for team
    base_dir = service.resolve_project_root(team)
    if base_dir is None:
        logger.warning(f"[AUTOCOMPLETE] Team not found: {team}")
        raise HTTPException(status_code=404, detail=f"Team '{team}' not found")

    # Security: Reject path traversal attempts
    if ".." in path:
        logger.warning(f"[AUTOCOMPLETE] Path traversal blocked: {path}")
        raise HTTPException(status_code=400, detail="Path traversal not allowed")

    # Parse the partial path
    partial = Path(path) if path else Path("")

    # Determine search directory and prefix
    if path.endswith("/"):
        # User typed "src/" - list contents of src/
        search_dir = base_dir / partial
        prefix = ""
    elif path:
        # User typed "src/ma" - search in src/ for entries starting with "ma"
        if partial.parent != Path("."):
            search_dir = base_dir / partial.parent
        else:
            search_dir = base_dir
        prefix = partial.name
    else:
        # Empty path - list project root
        search_dir = base_dir
        prefix = ""

    # Security: Validate search_dir is within base_dir
    try:
        search_dir = search_dir.resolve()
        base_resolved = base_dir.resolve()
        if not str(search_dir).startswith(str(base_resolved)):
            logger.warning(f"[AUTOCOMPLETE] Path outside project: {search_dir}")
            raise HTTPException(status_code=400, detail="Path outside project directory")
    except Exception:
        return AutocompleteResponse(completions=[])

    # Check directory exists
    if not search_dir.exists() or not search_dir.is_dir():
        return AutocompleteResponse(completions=[])

    # Find matching entries
    completions: List[PathCompletion] = []
    try:
        for entry in search_dir.iterdir():
            # Skip hidden files (dotfiles)
            if entry.name.startswith("."):
                continue

            # Filter by prefix (case-insensitive)
            if prefix and not entry.name.lower().startswith(prefix.lower()):
                continue

            # Build completion path relative to input
            if path.endswith("/"):
                completion_path = path + entry.name
            elif partial.parent != Path(".") and str(partial.parent) != ".":
                completion_path = f"{partial.parent}/{entry.name}"
            else:
                completion_path = entry.name

            # Add trailing slash for directories
            is_dir = entry.is_dir()
            if is_dir:
                completion_path += "/"

            completions.append(PathCompletion(
                path=completion_path,
                isDir=is_dir,
                name=entry.name
            ))

            if len(completions) >= limit:
                break

    except PermissionError:
        logger.warning(f"[AUTOCOMPLETE] Permission denied: {search_dir}")

    # Sort: directories first, then alphabetically by name
    completions.sort(key=lambda x: (not x.isDir, x.name.lower()))

    logger.info(
        f"[AUTOCOMPLETE] team={team}, path={path}, "
        f"results={len(completions)}"
    )

    return AutocompleteResponse(completions=completions)


# ============================================================
# Simple File Search Sprint 1: Content Search API
# ============================================================


class SearchResult(BaseModel):
    """Single search result."""
    path: str
    match_count: int


class SearchResponse(BaseModel):
    """Search API response."""
    results: List[SearchResult]
    total: int
    query: str


@router.get("/{team_id}/search", response_model=SearchResponse)
async def search_file_content(
    team_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    q: str = Query("", description="Search query"),
) -> SearchResponse:
    """Search file content across project.

    Features:
    - In-memory caching with 5-minute TTL
    - Auto-recovery on errors (cache invalidation)
    - .gitignore pattern exclusion
    - Hardcoded exclusions (node_modules, .git, etc.)

    Args:
        team_id: Team identifier
        q: Search query (case-insensitive)

    Returns:
        SearchResponse with matching files and match counts

    Raises:
        HTTPException 404: Team not found
    """
    service = get_file_service()

    # Resolve project root
    project_root = service.resolve_project_root(team_id)
    if project_root is None:
        logger.warning(f"[FILE-SEARCH] Team not found: {team_id}")
        raise HTTPException(status_code=404, detail=f"Team not found: {team_id}")

    # Get or build content index
    try:
        file_contents = service.get_or_build_content_index(team_id, project_root)
    except Exception as e:
        logger.error(f"[FILE-SEARCH] Error building index: {e}")
        # Invalidate cache on error (auto-recovery)
        service.invalidate_content_cache(team_id)
        raise HTTPException(status_code=500, detail=f"Error building search index: {str(e)}")

    # Search across file contents
    results: List[SearchResult] = []
    query_lower = q.lower()

    for file_path, content in file_contents.items():
        # Case-insensitive search
        content_lower = content.lower()
        match_count = content_lower.count(query_lower)

        if match_count > 0:
            results.append(SearchResult(
                path=file_path,
                match_count=match_count
            ))

    # Sort by match count (descending)
    results.sort(key=lambda x: x.match_count, reverse=True)

    logger.info(
        f"[FILE-SEARCH] team={team_id}, query={q}, "
        f"results={len(results)}"
    )

    return SearchResponse(
        results=results,
        total=len(results),
        query=q
    )
