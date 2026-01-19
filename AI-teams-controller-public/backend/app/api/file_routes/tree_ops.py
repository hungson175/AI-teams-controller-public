# -*- coding: utf-8 -*-
"""File tree operations routes.

Contains endpoints for:
- GET /{team_id}/list - Flat file list
- GET /{team_id}/tree - Directory tree
"""

import logging
from pathlib import Path
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.auth_routes import get_current_user_from_token
from app.models.auth_schemas import UserResponse
from app.models.file_schemas import TreeResponse
from app.services.file_service import get_file_service

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================
# Sprint 3 Story 3: Flat File List API (for Cmd+P search)
# ============================================================

MAX_FILE_LIST_RESULTS = 10000


class FileListItem(BaseModel):
    """Single file in flat list."""
    path: str
    isDir: bool


class FileListResponse(BaseModel):
    """Flat file list API response."""
    files: List[FileListItem]
    total: int
    truncated: bool
    project_root: str


@router.get("/{team_id}/list", response_model=FileListResponse)
async def list_files_flat(
    team_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    limit: int = Query(MAX_FILE_LIST_RESULTS, le=MAX_FILE_LIST_RESULTS, description="Max files to return"),
    show_hidden: bool = Query(False, description="Include hidden files (dotfiles)"),
) -> FileListResponse:
    """
    List all files in a team's project as a flat list.

    Used for file search (Cmd+P) - returns all file paths for client-side fuzzy search.

    Args:
        team_id: Team identifier
        limit: Maximum files to return (default: 10000)
        show_hidden: Include hidden files (default: False)

    Returns:
        FileListResponse with flat list of all files

    Raises:
        HTTPException 404: Team not found
    """
    service = get_file_service()

    # Resolve project root
    project_root = service.resolve_project_root(team_id)
    if project_root is None:
        logger.warning(f"[FILE-LIST] Team not found: {team_id}")
        raise HTTPException(status_code=404, detail=f"Team not found: {team_id}")

    # Recursively collect all files
    files: List[FileListItem] = []
    truncated = False
    base_path = project_root.resolve()

    def collect_files(directory: Path, depth: int = 0) -> bool:
        """Recursively collect files. Returns False if limit reached."""
        nonlocal truncated

        if depth > 20:  # Safety: max depth
            return True

        try:
            entries = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except (PermissionError, OSError):
            return True

        for entry in entries:
            # Skip hidden files unless requested
            if not show_hidden and entry.name.startswith("."):
                continue

            # Skip common large directories
            if entry.name in ("node_modules", "__pycache__", ".git", "venv", ".venv", "dist", "build"):
                continue

            # Check limit
            if len(files) >= limit:
                truncated = True
                return False

            # Get relative path
            try:
                rel_path = str(entry.relative_to(base_path))
            except ValueError:
                continue

            is_dir = entry.is_dir()
            files.append(FileListItem(
                path=rel_path + ("/" if is_dir else ""),
                isDir=is_dir
            ))

            # Recurse into directories
            if is_dir:
                if not collect_files(entry, depth + 1):
                    return False

        return True

    collect_files(base_path)

    logger.info(
        f"[FILE-LIST] team={team_id}, files={len(files)}, "
        f"truncated={truncated}, show_hidden={show_hidden}"
    )

    return FileListResponse(
        files=files,
        total=len(files),
        truncated=truncated,
        project_root=str(project_root)
    )


@router.get("/{team_id}/tree", response_model=TreeResponse)
async def get_tree(
    team_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    path: str = Query("/", description="Directory path relative to project root"),
    depth: int = Query(1, ge=1, le=5, description="Levels to expand (1-5)"),
    show_hidden: bool = Query(True, description="Include hidden files (dotfiles)"),
) -> TreeResponse:
    """List directory tree for a team's project.

    Args:
        team_id: Team identifier
        path: Relative path within project (default: root)
        depth: Number of levels to expand (1-5)
        show_hidden: Whether to include hidden files

    Returns:
        TreeResponse with project root and file nodes

    Raises:
        HTTPException 404: Team not found
    """
    service = get_file_service()

    # Resolve project root
    project_root = service.resolve_project_root(team_id)
    if project_root is None:
        logger.warning(f"[FILE-API] Team not found: {team_id}")
        raise HTTPException(status_code=404, detail=f"Team not found: {team_id}")

    # List directory
    result = service.list_directory(
        project_root=project_root,
        path=path,
        depth=depth,
        show_hidden=show_hidden,
    )

    logger.info(
        f"[FILE-API] Tree request: team={team_id}, path={path}, "
        f"depth={depth}, nodes={len(result.tree)}"
    )

    return result
