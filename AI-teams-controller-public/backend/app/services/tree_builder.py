# -*- coding: utf-8 -*-
"""File tree building service.

Sprint 3 Tech Debt - Extracted from FileService to satisfy SRP.
Handles directory tree structure generation.
"""

import logging
from pathlib import Path
from typing import Callable

from app.models.file_schemas import FileNode, TreeResponse

logger = logging.getLogger(__name__)


class TreeBuilder:
    """Builds file tree structures for directory listing.

    Extracted from FileService (Sprint 3) to satisfy Single Responsibility Principle.
    Handles recursive directory traversal and tree structure generation.
    """

    def __init__(self, path_validator: Callable[[Path, str], Path | None]):
        """Initialize TreeBuilder.

        Args:
            path_validator: Function to validate paths (prevents path traversal)
                           Signature: (project_root: Path, relative_path: str) -> Path | None
        """
        self._validate_path = path_validator

    def list_directory(
        self,
        project_root: Path,
        path: str = "/",
        depth: int = 1,
        show_hidden: bool = True,
    ) -> TreeResponse:
        """List directory tree.

        Args:
            project_root: Absolute path to project root
            path: Relative path within project (default: root)
            depth: Levels to expand (1 = immediate children only)
            show_hidden: Include dotfiles

        Returns:
            TreeResponse with file nodes.
        """
        # Validate path
        target_path = self._validate_path(project_root, path)
        if target_path is None:
            return TreeResponse(project_root=str(project_root), tree=[])

        if not target_path.exists():
            return TreeResponse(project_root=str(project_root), tree=[])

        if not target_path.is_dir():
            return TreeResponse(project_root=str(project_root), tree=[])

        # Build tree
        tree = self._build_tree(
            project_root, target_path, depth, show_hidden
        )

        return TreeResponse(project_root=str(project_root), tree=tree)

    def _build_tree(
        self,
        project_root: Path,
        directory: Path,
        depth: int,
        show_hidden: bool,
    ) -> list[FileNode]:
        """Recursively build file tree.

        Args:
            project_root: Project root for relative path calculation
            directory: Current directory to list
            depth: Remaining depth to expand
            show_hidden: Include dotfiles

        Returns:
            List of FileNode objects.
        """
        nodes = []

        try:
            entries = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except (OSError, PermissionError):
            return nodes

        for entry in entries:
            # Skip hidden files if requested
            if not show_hidden and entry.name.startswith("."):
                continue

            # Calculate relative path from project root
            try:
                rel_path = str(entry.relative_to(project_root))
            except ValueError:
                continue

            if entry.is_dir():
                children = None
                if depth > 1:
                    children = self._build_tree(
                        project_root, entry, depth - 1, show_hidden
                    )

                node = FileNode(
                    name=entry.name,
                    path=rel_path,
                    type="directory",
                    size=None,
                    children=children,
                )
            else:
                try:
                    size = entry.stat().st_size
                except OSError:
                    size = 0

                node = FileNode(
                    name=entry.name,
                    path=rel_path,
                    type="file",
                    size=size,
                    children=None,
                )

            nodes.append(node)

        return nodes
