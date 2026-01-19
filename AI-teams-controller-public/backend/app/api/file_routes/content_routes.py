# -*- coding: utf-8 -*-
"""File content read/write operations routes.

Contains endpoints for:
- GET /{team_id}/content - Read file content
- PUT /{team_id}/{path:path} - Save file content (edit mode)
"""

import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.auth_routes import get_current_user_from_token
from app.models.auth_schemas import UserResponse
from app.models.file_schemas import FileContent
from app.services.file_service import get_file_service

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================
# File Content Read API
# ============================================================


@router.get("/{team_id}/content", response_model=FileContent)
async def get_content(
    team_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    path: str = Query(..., description="File path relative to project root"),
) -> FileContent:
    """Read file content from a team's project.

    Security:
    - Path traversal is blocked
    - Sensitive files (.env, *.pem, etc.) return error
    - Files over 1MB are rejected
    - Binary files are detected and marked

    Args:
        team_id: Team identifier
        path: Relative path to file

    Returns:
        FileContent with content or error

    Raises:
        HTTPException 404: Team not found
    """
    service = get_file_service()

    # Resolve project root
    project_root = service.resolve_project_root(team_id)
    if project_root is None:
        logger.warning(f"[FILE-API] Team not found: {team_id}")
        raise HTTPException(status_code=404, detail=f"Team not found: {team_id}")

    # Read file content
    result = service.read_file_content(project_root, path)

    if result.error:
        logger.info(
            f"[FILE-API] Content request: team={team_id}, path={path}, "
            f"error={result.error}"
        )
    else:
        logger.info(
            f"[FILE-API] Content request: team={team_id}, path={path}, "
            f"size={result.size}, mime={result.mime_type}"
        )

    return result


# ============================================================
# Sprint 12: Save File Content API (Edit Mode)
# ============================================================

# File size limit: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# Protected paths that cannot be edited
PROTECTED_PATHS = {".git", "node_modules", "__pycache__", ".venv"}


class SaveFileResponse(BaseModel):
    """Response from file save operation."""
    success: bool
    message: str
    path: str
    size: int


@router.put("/{team_id}/{path:path}", response_model=SaveFileResponse)
async def save_file_content(
    team_id: str,
    path: str,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    content: str = Body(..., media_type="text/plain"),
) -> SaveFileResponse:
    """Save file content to disk.

    Security:
    - Path traversal is blocked (400)
    - Protected paths cannot be edited (403)
    - File size limit enforced (10MB max, 413)
    - Team validation (404)

    Args:
        team_id: Team identifier
        path: File path relative to project root
        content: File content as plain text

    Returns:
        SaveFileResponse with success status, path, and size

    Raises:
        HTTPException 400: Path traversal detected
        HTTPException 403: Protected path
        HTTPException 404: Team not found
        HTTPException 413: File too large
    """
    service = get_file_service()

    # Resolve project root
    project_root = service.resolve_project_root(team_id)
    if project_root is None:
        logger.warning(f"[FILE-SAVE] Team not found: {team_id}")
        raise HTTPException(status_code=404, detail=f"Team not found: {team_id}")

    # Security: Reject path traversal
    if ".." in path:
        logger.warning(f"[FILE-SAVE] Path traversal blocked: {path}")
        raise HTTPException(status_code=400, detail="Path traversal detected")

    # Security: Block absolute paths
    if path.startswith("/"):
        logger.warning(f"[FILE-SAVE] Absolute path blocked: {path}")
        raise HTTPException(status_code=400, detail="Absolute paths not allowed")

    # Security: Check protected paths
    clean_path = path.strip().strip("/")
    if not clean_path:
        logger.warning(f"[FILE-SAVE] Cannot save to project root")
        raise HTTPException(status_code=400, detail="Invalid path")

    path_parts = clean_path.split("/")
    if path_parts[0] in PROTECTED_PATHS:
        logger.warning(f"[FILE-SAVE] Protected path: {path_parts[0]}")
        raise HTTPException(
            status_code=403,
            detail=f"Cannot edit protected path: {path_parts[0]}"
        )

    # Security: Check file size limit
    content_size = len(content.encode('utf-8'))
    if content_size > MAX_FILE_SIZE:
        logger.warning(f"[FILE-SAVE] File too large: {content_size} bytes")
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {MAX_FILE_SIZE // (1024 * 1024)}MB)"
        )

    # Build full path
    target_path = project_root / clean_path

    # Ensure parent directory exists
    parent_dir = target_path.parent
    if not parent_dir.exists():
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"[FILE-SAVE] Created parent directories: {parent_dir}")
        except (PermissionError, OSError) as e:
            logger.error(f"[FILE-SAVE] Failed to create parent: {e}")
            raise HTTPException(status_code=400, detail=f"Cannot create parent directory: {str(e)}")

    # Write file
    try:
        target_path.write_text(content, encoding='utf-8')
        logger.info(f"[FILE-SAVE] Saved file: {target_path} ({content_size} bytes)")

        return SaveFileResponse(
            success=True,
            message="File saved successfully",
            path=clean_path,
            size=content_size
        )
    except PermissionError:
        logger.error(f"[FILE-SAVE] Permission denied: {path}")
        raise HTTPException(status_code=403, detail=f"Permission denied: {path}")
    except OSError as e:
        logger.error(f"[FILE-SAVE] Failed to save: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to save file: {str(e)}")
