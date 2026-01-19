# -*- coding: utf-8 -*-
"""File browser service for project file access.

File Browser Epic - Phase 1: Backend API

Security Features:
- Path traversal prevention (validates all paths within project root)
- Sensitive file blacklist (.env, *.pem, credentials, etc.)
- File size limit (1MB max)
- Binary file detection
"""

import fnmatch
import logging
import mimetypes
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from app.models.file_schemas import FileContent, FileNode, TreeResponse
from app.services.content_indexer import ContentIndexer
from app.services.tree_builder import TreeBuilder

logger = logging.getLogger(__name__)

# Configuration
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB
TREE_CACHE_TTL = timedelta(seconds=10)
CONTENT_CACHE_TTL = timedelta(seconds=300)  # 5 minutes

# Simple File Search Sprint 1: Exclusion Configuration
EXCLUDED_DIRS = {"node_modules", ".git", "__pycache__", "venv", ".venv", "dist", "build", ".next"}
EXCLUDED_EXTENSIONS = {".pyc", ".log", ".lock"}

# Blacklisted file patterns (glob-style)
BLACKLISTED_PATTERNS = [
    "*.pem",
    "*.key",
    "*credentials*",
    "*secret*",
    "*.p12",
    "*.pfx",
    "id_rsa",
    "id_ed25519",
    "id_dsa",
    "id_ecdsa",
]

# Exact blacklisted paths
BLACKLISTED_EXACT = [
    ".git/config",
    ".npmrc",
    ".pypirc",
]

# Text MIME types that should be treated as text
TEXT_MIME_TYPES = [
    "application/json",
    "application/javascript",
    "application/xml",
    "application/yaml",
    "application/x-yaml",
    "application/x-sh",
    "application/x-python",
]


class FileService:
    """Service for browsing and reading project files."""

    def __init__(self):
        self._tree_cache: dict[str, tuple[datetime, TreeResponse]] = {}
        # Content indexing (Sprint 2 refactor: extracted to ContentIndexer)
        self._content_indexer = ContentIndexer()
        # Tree building (Sprint 3 refactor: extracted to TreeBuilder)
        self._tree_builder = TreeBuilder(self._validate_path)
        # Calculate project root from this file's location
        # __file__ = backend/app/services/file_service.py
        # parent x4 = project root (AI-teams-controller/)
        self._backend_project_root = Path(__file__).parent.parent.parent.parent.resolve()

    def resolve_project_root(self, team_id: str) -> Optional[Path]:
        """Resolve project root for a team.

        Priority:
        1. UI-created teams: ~/dev/tmux-teams/{team_id}/
        2. Manual teams: {backend_project_root}/docs/tmux/{team_id}/ -> project root
        3. Fallback: Query tmux for pane_current_path of the session

        Returns:
            Path to project root, or None if team not found.
        """
        # Check UI-created teams first
        ui_team_dir = Path.home() / "dev" / "tmux-teams" / team_id
        if ui_team_dir.exists():
            return ui_team_dir

        # Check manual teams (relative to this project's root, not cwd)
        manual_team_dir = self._backend_project_root / "docs" / "tmux" / team_id
        if manual_team_dir.exists():
            # Project root is the backend's project root
            return self._backend_project_root

        # Fallback: Query tmux for pane_current_path
        tmux_path = self._query_tmux_pane_path(team_id)
        if tmux_path:
            return tmux_path

        return None

    def get_or_build_content_index(self, team_id: str, project_root: Path) -> dict[str, str]:
        """Get content index from cache or build new one.

        Implements Story 1: File Indexing with 5-minute TTL cache.

        Args:
            team_id: Team identifier for cache key
            project_root: Project root directory

        Returns:
            Dict mapping relative file paths to file contents
        """
        # Delegate to ContentIndexer (Sprint 2 refactor)
        return self._content_indexer.get_or_build_index(team_id, project_root)

    def invalidate_content_cache(self, team_id: str) -> None:
        """Invalidate content cache for a team (auto-recovery on errors).

        Implements Story 1: Auto-recovery mechanism.

        Args:
            team_id: Team identifier
        """
        # Delegate to ContentIndexer (Sprint 2 refactor)
        self._content_indexer.invalidate_cache(team_id)

    def _query_tmux_pane_path(self, session_name: str) -> Optional[Path]:
        """Query tmux for the current working directory of a session's first pane.

        Args:
            session_name: Name of the tmux session

        Returns:
            Path to the pane's current working directory, or None if unavailable.
        """
        try:
            result = subprocess.run(
                ["tmux", "display-message", "-t", f"{session_name}:0.0", "-p", "#{pane_current_path}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                path = Path(result.stdout.strip())
                if path.exists():
                    return path
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
            logger.debug(f"[FILE] Failed to query tmux for {session_name}: {e}")
        return None

    def _validate_path(
        self, project_root: Path, relative_path: str
    ) -> Optional[Path]:
        """Validate and resolve path safely.

        Security: Prevents path traversal attacks.

        Args:
            project_root: Absolute path to project root
            relative_path: User-provided relative path

        Returns:
            Absolute path if valid, None if path traversal detected.
        """
        # Handle root path
        if relative_path in ("/", ""):
            return project_root.resolve()

        # Block absolute paths (paths starting with /)
        # Exception: "/" alone means project root (handled above)
        if relative_path.startswith("/"):
            # Check if it's trying to access a path outside project
            # e.g., /etc/passwd should be blocked
            clean_path = relative_path.lstrip("/")
            if clean_path and Path(relative_path).is_absolute():
                # This is an absolute path like /etc/passwd
                logger.warning(
                    f"[FILE] Absolute path blocked: {relative_path}"
                )
                return None

        # Remove leading slash if present
        clean_path = relative_path.lstrip("/")

        # Normalize and resolve the path
        try:
            requested = (project_root / clean_path).resolve()
        except (OSError, ValueError):
            return None

        # Security check: must be within project root
        try:
            requested.relative_to(project_root.resolve())
            return requested
        except ValueError:
            # Path is outside project root (traversal attempt)
            logger.warning(
                f"[FILE] Path traversal blocked: {relative_path} -> {requested}"
            )
            return None

    def _is_blacklisted(self, path: Path) -> bool:
        """Check if file is blacklisted (sensitive).

        Args:
            path: Path to check

        Returns:
            True if file should not have its content exposed.
        """
        name = path.name
        relative_path = str(path)

        # Check exact matches
        for exact in BLACKLISTED_EXACT:
            if relative_path.endswith(exact):
                return True

        # Check patterns
        for pattern in BLACKLISTED_PATTERNS:
            if fnmatch.fnmatch(name, pattern):
                return True
            if fnmatch.fnmatch(name.lower(), pattern.lower()):
                return True

        return False

    def _is_binary(self, path: Path) -> bool:
        """Detect if file is binary.

        Args:
            path: Path to file

        Returns:
            True if file appears to be binary.
        """
        # Check MIME type first
        mime, _ = mimetypes.guess_type(str(path))

        if mime:
            # Text types
            if mime.startswith("text/") or mime in TEXT_MIME_TYPES:
                return False

            # Known binary types
            if mime.startswith(("image/", "audio/", "video/", "application/octet")):
                return True

        # Fallback: check for null bytes in first 8KB
        try:
            with open(path, "rb") as f:
                chunk = f.read(8192)
                return b"\x00" in chunk
        except (OSError, IOError):
            return True

    def _get_mime_type(self, path: Path) -> str:
        """Get MIME type for a file.

        Args:
            path: Path to file

        Returns:
            MIME type string.
        """
        mime, _ = mimetypes.guess_type(str(path))
        return mime or "application/octet-stream"

    def list_directory(
        self,
        project_root: Path,
        path: str = "/",
        depth: int = 1,
        show_hidden: bool = True,
    ) -> TreeResponse:
        """List directory tree.

        Sprint 3: Facade - delegates to TreeBuilder.
        """
        return self._tree_builder.list_directory(project_root, path, depth, show_hidden)

    def read_file_content(
        self, project_root: Path, relative_path: str
    ) -> FileContent:
        """Read file content with security checks.

        Args:
            project_root: Absolute path to project root
            relative_path: Relative path to file

        Returns:
            FileContent with content or error.
        """
        # Validate path
        file_path = self._validate_path(project_root, relative_path)
        if file_path is None:
            return FileContent(
                path=relative_path,
                name=Path(relative_path).name,
                size=0,
                mime_type="application/octet-stream",
                content=None,
                is_binary=False,
                is_truncated=False,
                error="Invalid path or access denied",
            )

        # Check file exists
        if not file_path.exists():
            return FileContent(
                path=relative_path,
                name=file_path.name,
                size=0,
                mime_type="application/octet-stream",
                content=None,
                is_binary=False,
                is_truncated=False,
                error="File not found",
            )

        if not file_path.is_file():
            return FileContent(
                path=relative_path,
                name=file_path.name,
                size=0,
                mime_type="application/octet-stream",
                content=None,
                is_binary=False,
                is_truncated=False,
                error="Not a file",
            )

        # Get file info
        try:
            stat = file_path.stat()
            size = stat.st_size
        except OSError as e:
            return FileContent(
                path=relative_path,
                name=file_path.name,
                size=0,
                mime_type="application/octet-stream",
                content=None,
                is_binary=False,
                is_truncated=False,
                error=f"Cannot read file: {e}",
            )

        mime_type = self._get_mime_type(file_path)

        # Check blacklist
        if self._is_blacklisted(file_path):
            return FileContent(
                path=relative_path,
                name=file_path.name,
                size=size,
                mime_type=mime_type,
                content=None,
                is_binary=False,
                is_truncated=False,
                error="Sensitive file - content blocked for security",
            )

        # Check size limit
        if size > MAX_FILE_SIZE:
            return FileContent(
                path=relative_path,
                name=file_path.name,
                size=size,
                mime_type=mime_type,
                content=None,
                is_binary=False,
                is_truncated=True,
                error=f"File too large ({size:,} bytes). Maximum: 1MB",
            )

        # Check if binary
        if self._is_binary(file_path):
            return FileContent(
                path=relative_path,
                name=file_path.name,
                size=size,
                mime_type=mime_type,
                content=None,
                is_binary=True,
                is_truncated=False,
                error="Binary files cannot be displayed",
            )

        # Read content
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try with fallback encoding
            try:
                content = file_path.read_text(encoding="latin-1")
            except Exception:
                return FileContent(
                    path=relative_path,
                    name=file_path.name,
                    size=size,
                    mime_type=mime_type,
                    content=None,
                    is_binary=True,
                    is_truncated=False,
                    error="Cannot decode file content",
                )
        except Exception as e:
            return FileContent(
                path=relative_path,
                name=file_path.name,
                size=size,
                mime_type=mime_type,
                content=None,
                is_binary=False,
                is_truncated=False,
                error=f"Error reading file: {e}",
            )

        return FileContent(
            path=relative_path,
            name=file_path.name,
            size=size,
            mime_type=mime_type,
            content=content,
            is_binary=False,
            is_truncated=False,
            error=None,
        )


# Singleton instance
_file_service: Optional[FileService] = None


def get_file_service() -> FileService:
    """Get or create FileService singleton."""
    global _file_service
    if _file_service is None:
        _file_service = FileService()
    return _file_service
