# -*- coding: utf-8 -*-
"""File browser API routes (split into modules).

This package combines four sub-routers:
- tree_ops: Directory tree and list operations
- crud_ops: File/folder CRUD operations (create, delete, rename)
- content_routes: File content read/write
- search_routes: Autocomplete and content search

All file routes require authentication (enforced by middleware after removing from UNPROTECTED_PREFIXES).
"""

from fastapi import APIRouter

from .content_routes import router as content_router
from .crud_ops import router as crud_router
from .search_routes import router as search_router
from .tree_ops import router as tree_router

# Combined router with all file operations
# Auth enforced by middleware (SESSION_TOKEN check)
router = APIRouter(prefix="/api/files", tags=["files"])

# Include all sub-routers
router.include_router(tree_router)
router.include_router(crud_router)
router.include_router(content_router)
router.include_router(search_router)

__all__ = ["router"]
