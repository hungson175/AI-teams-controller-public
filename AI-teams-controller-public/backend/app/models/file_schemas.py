# -*- coding: utf-8 -*-
"""Pydantic schemas for file browser API.

File Browser Epic - Phase 1: Backend API
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class FileNode(BaseModel):
    """Represents a file or directory in the tree."""

    name: str = Field(..., description="File or directory name")
    path: str = Field(..., description="Relative path from project root")
    type: Literal["file", "directory"] = Field(..., description="Node type")
    size: Optional[int] = Field(None, description="Size in bytes (null for directories)")
    children: Optional[list["FileNode"]] = Field(
        None, description="Child nodes (for directories only)"
    )


class TreeResponse(BaseModel):
    """Response for directory tree listing."""

    project_root: str = Field(..., description="Absolute path to project root (display only)")
    tree: list[FileNode] = Field(..., description="Root level nodes")


class FileContent(BaseModel):
    """Response for file content request."""

    path: str = Field(..., description="Relative path from project root")
    name: str = Field(..., description="File name")
    size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    content: Optional[str] = Field(None, description="File content (null if binary/too large)")
    is_binary: bool = Field(False, description="True if binary file")
    is_truncated: bool = Field(False, description="True if file exceeded size limit")
    error: Optional[str] = Field(None, description="Error message if read failed")


# Enable forward references for recursive FileNode
FileNode.model_rebuild()
