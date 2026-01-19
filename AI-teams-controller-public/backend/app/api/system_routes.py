# -*- coding: utf-8 -*-
"""System routes for system-level operations.

Endpoints:
- GET /api/system/directories - List directories for directory picker
"""

import os
from pathlib import Path
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.api.auth_routes import get_current_user_from_token
from app.models.auth_schemas import UserResponse

router = APIRouter(prefix="/api/system", tags=["system"])


class DirectoryNode(BaseModel):
    """Directory node for tree display."""

    name: str
    path: str
    type: str  # "directory" or "file"
    size: Optional[int] = None
    children: Optional[List["DirectoryNode"]] = None


class DirectoriesResponse(BaseModel):
    """Response for directory listing."""

    tree: List[DirectoryNode]


@router.get("/directories", response_model=DirectoriesResponse)
async def list_directories(
    current_user: Annotated[UserResponse, Depends(get_current_user_from_token)],
    path: str = Query("~", description="Directory path to list (~ for home)"),
    show_hidden: bool = Query(False, description="Include hidden files/folders"),
) -> DirectoriesResponse:
    """List directories in the specified path.

    Used by DirectoryPicker component for terminal creation.

    Args:
        path: Directory path to list. Use ~ for home directory.
        show_hidden: Whether to include hidden files/folders (starting with .)

    Returns:
        DirectoriesResponse with tree of directory nodes.
    """
    # Expand home directory
    expanded_path = os.path.expanduser(path)

    # Validate path exists and is a directory
    if not os.path.isdir(expanded_path):
        return DirectoriesResponse(tree=[])

    # List directory contents
    nodes: List[DirectoryNode] = []

    try:
        for entry in sorted(os.listdir(expanded_path)):
            # Skip hidden files/directories unless show_hidden is True
            if not show_hidden and entry.startswith("."):
                continue

            full_path = os.path.join(expanded_path, entry)

            # Only include directories
            if os.path.isdir(full_path):
                nodes.append(
                    DirectoryNode(
                        name=entry,
                        path=full_path,
                        type="directory",
                        size=None,
                    )
                )
    except PermissionError:
        # Return empty if no permission
        pass

    return DirectoriesResponse(tree=nodes)
