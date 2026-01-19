# -*- coding: utf-8 -*-
"""File CRUD operations routes.

Contains endpoints for:
- POST /{team_id}/create - Create file/folder
- DELETE /{team_id}/delete - Delete file/folder
- PATCH /{team_id}/rename - Rename file/folder
"""

import logging
import re
import shutil
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.auth_routes import get_current_user_from_token
from app.models.auth_schemas import UserResponse
from app.services.file_service import get_file_service

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================
# File/Folder Creation API
# ============================================================


class CreateFileRequest(BaseModel):
    """Request to create a file or folder."""
    path: str = Field(..., description="Path relative to project root")
    type: Literal["file", "folder"] = Field(..., description="Type of item to create")


class CreateFileResponse(BaseModel):
    """Response from file/folder creation."""
    success: bool
    path: str
    type: str
    message: str


@router.post("/{team_id}/create", response_model=CreateFileResponse)
async def create_file_or_folder(
    team_id: str,
    request: CreateFileRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
) -> CreateFileResponse:
    """Create a file or folder in a team's project.

    Security:
    - Path traversal is blocked
    - Cannot overwrite existing files/folders

    Args:
        team_id: Team identifier
        request: CreateFileRequest with path and type

    Returns:
        CreateFileResponse with success status

    Raises:
        HTTPException 404: Team not found
        HTTPException 400: Invalid path or already exists
    """
    service = get_file_service()

    # Resolve project root
    project_root = service.resolve_project_root(team_id)
    if project_root is None:
        logger.warning(f"[FILE-CREATE] Team not found: {team_id}")
        raise HTTPException(status_code=404, detail=f"Team not found: {team_id}")

    # Security: Reject path traversal attempts
    if ".." in request.path:
        logger.warning(f"[FILE-CREATE] Path traversal blocked: {request.path}")
        raise HTTPException(status_code=400, detail="Path traversal not allowed")

    # Build full path
    target_path = project_root / request.path.lstrip("/")

    # Check if already exists
    if target_path.exists():
        logger.warning(f"[FILE-CREATE] Already exists: {target_path}")
        raise HTTPException(status_code=400, detail=f"Path already exists: {request.path}")

    # Ensure parent directory exists
    parent_dir = target_path.parent
    if not parent_dir.exists():
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"[FILE-CREATE] Created parent directories: {parent_dir}")
        except (PermissionError, OSError) as e:
            logger.error(f"[FILE-CREATE] Failed to create parent: {e}")
            raise HTTPException(status_code=400, detail=f"Cannot create parent directory: {str(e)}")

    # Create file or folder
    try:
        if request.type == "folder":
            target_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"[FILE-CREATE] Created folder: {target_path}")
        else:
            target_path.touch()
            logger.info(f"[FILE-CREATE] Created file: {target_path}")

        return CreateFileResponse(
            success=True,
            path=request.path,
            type=request.type,
            message=f"Successfully created {request.type}: {request.path}"
        )
    except (PermissionError, OSError) as e:
        logger.error(f"[FILE-CREATE] Failed to create: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create {request.type}: {str(e)}")


# ============================================================
# Sprint 9: Delete File/Folder API
# ============================================================

# Protected paths that cannot be deleted
PROTECTED_PATHS = {".git", "node_modules", "__pycache__", ".venv"}


class DeleteFileRequest(BaseModel):
    """Request to delete a file or folder."""
    path: str = Field(..., description="Path relative to project root")


class DeleteFileResponse(BaseModel):
    """Response from file/folder deletion."""
    success: bool
    path: str
    type: str
    message: str


@router.delete("/{team_id}/delete", response_model=DeleteFileResponse)
async def delete_file_or_folder(
    team_id: str,
    request: DeleteFileRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
) -> DeleteFileResponse:
    """Delete a file or folder in a team's project.

    Security:
    - Path traversal is blocked
    - Protected paths cannot be deleted
    - Project root cannot be deleted

    Args:
        team_id: Team identifier
        request: DeleteFileRequest with path

    Returns:
        DeleteFileResponse with success status

    Raises:
        HTTPException 404: Team or file not found
        HTTPException 400: Invalid path, traversal, or protected
    """
    service = get_file_service()

    # Resolve project root
    project_root = service.resolve_project_root(team_id)
    if project_root is None:
        logger.warning(f"[FILE-DELETE] Team not found: {team_id}")
        raise HTTPException(status_code=404, detail=f"Team not found: {team_id}")

    # Security: Reject path traversal
    if ".." in request.path:
        logger.warning(f"[FILE-DELETE] Path traversal blocked: {request.path}")
        raise HTTPException(status_code=400, detail="Path traversal not allowed")

    # Security: Reject empty path (project root)
    clean_path = request.path.strip().strip("/")
    if not clean_path:
        logger.warning(f"[FILE-DELETE] Cannot delete project root")
        raise HTTPException(status_code=400, detail="Cannot delete project root")

    # Security: Check protected paths
    path_parts = clean_path.split("/")
    if path_parts[0] in PROTECTED_PATHS:
        logger.warning(f"[FILE-DELETE] Protected path: {path_parts[0]}")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete protected path: {path_parts[0]}"
        )

    # Build full path
    target_path = project_root / clean_path

    # Check exists
    if not target_path.exists():
        logger.warning(f"[FILE-DELETE] Path not found: {request.path}")
        raise HTTPException(status_code=404, detail=f"Path not found: {request.path}")

    # Determine type
    is_dir = target_path.is_dir()
    item_type = "folder" if is_dir else "file"

    # Delete
    try:
        if is_dir:
            shutil.rmtree(target_path)
            logger.info(f"[FILE-DELETE] Deleted folder: {target_path}")
        else:
            target_path.unlink()
            logger.info(f"[FILE-DELETE] Deleted file: {target_path}")

        return DeleteFileResponse(
            success=True,
            path=request.path,
            type=item_type,
            message=f"Successfully deleted {item_type}: {request.path}"
        )
    except PermissionError:
        logger.error(f"[FILE-DELETE] Permission denied: {request.path}")
        raise HTTPException(status_code=400, detail=f"Permission denied: {request.path}")
    except OSError as e:
        logger.error(f"[FILE-DELETE] Failed to delete: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to delete: {str(e)}")


# ============================================================
# Sprint 9: Rename File/Folder API
# ============================================================

# Invalid characters in file names
INVALID_NAME_PATTERN = re.compile(r'[/\\<>:"|?*\x00-\x1f]')


class RenameFileRequest(BaseModel):
    """Request to rename a file or folder."""
    old_path: str = Field(..., description="Current path relative to project root")
    new_name: str = Field(..., description="New name (just the name, not full path)")


class RenameFileResponse(BaseModel):
    """Response from file/folder rename."""
    success: bool
    old_path: str
    new_path: str
    type: str
    message: str


@router.patch("/{team_id}/rename", response_model=RenameFileResponse)
async def rename_file_or_folder(
    team_id: str,
    request: RenameFileRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
) -> RenameFileResponse:
    """Rename a file or folder in a team's project.

    Security:
    - Path traversal is blocked
    - Invalid characters in name are blocked
    - Cannot overwrite existing files

    Args:
        team_id: Team identifier
        request: RenameFileRequest with old_path and new_name

    Returns:
        RenameFileResponse with success status

    Raises:
        HTTPException 404: Team or file not found
        HTTPException 400: Invalid path, name, or already exists
    """
    service = get_file_service()

    # Resolve project root
    project_root = service.resolve_project_root(team_id)
    if project_root is None:
        logger.warning(f"[FILE-RENAME] Team not found: {team_id}")
        raise HTTPException(status_code=404, detail=f"Team not found: {team_id}")

    # Security: Reject path traversal in old_path
    if ".." in request.old_path:
        logger.warning(f"[FILE-RENAME] Path traversal blocked: {request.old_path}")
        raise HTTPException(status_code=400, detail="Path traversal not allowed")

    # Security: Validate new_name
    if ".." in request.new_name or "/" in request.new_name or "\\" in request.new_name:
        logger.warning(f"[FILE-RENAME] Invalid characters in name: {request.new_name}")
        raise HTTPException(status_code=400, detail="Invalid characters in name")

    if INVALID_NAME_PATTERN.search(request.new_name):
        logger.warning(f"[FILE-RENAME] Invalid characters in name: {request.new_name}")
        raise HTTPException(status_code=400, detail="Invalid characters in name")

    if not request.new_name.strip():
        logger.warning(f"[FILE-RENAME] Empty name")
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    # Build old path
    clean_old_path = request.old_path.strip().strip("/")
    if not clean_old_path:
        logger.warning(f"[FILE-RENAME] Cannot rename project root")
        raise HTTPException(status_code=400, detail="Cannot rename project root")

    old_full_path = project_root / clean_old_path

    # Check old path exists
    if not old_full_path.exists():
        logger.warning(f"[FILE-RENAME] Path not found: {request.old_path}")
        raise HTTPException(status_code=404, detail=f"Path not found: {request.old_path}")

    # Compute new path (same directory, new name)
    new_full_path = old_full_path.parent / request.new_name.strip()

    # Check new path doesn't exist
    if new_full_path.exists():
        logger.warning(f"[FILE-RENAME] File/folder already exists: {request.new_name}")
        raise HTTPException(
            status_code=400,
            detail=f"A file/folder with that name already exists"
        )

    # Determine type
    is_dir = old_full_path.is_dir()
    item_type = "folder" if is_dir else "file"

    # Rename
    try:
        old_full_path.rename(new_full_path)
        logger.info(f"[FILE-RENAME] Renamed {old_full_path} to {new_full_path}")

        # Compute relative new path
        new_rel_path = str(new_full_path.relative_to(project_root))

        return RenameFileResponse(
            success=True,
            old_path=request.old_path,
            new_path=new_rel_path,
            type=item_type,
            message=f"Successfully renamed to: {new_rel_path}"
        )
    except PermissionError:
        logger.error(f"[FILE-RENAME] Permission denied: {request.old_path}")
        raise HTTPException(status_code=400, detail=f"Permission denied")
    except OSError as e:
        logger.error(f"[FILE-RENAME] Failed to rename: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to rename: {str(e)}")
