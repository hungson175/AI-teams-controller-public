# -*- coding: utf-8 -*-
"""Content indexing for file search (Sprint 2 Tech Debt).

Extracted from FileService to reduce complexity.
Handles file content indexing with .gitignore support and caching.
"""

import fnmatch
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

# Configuration
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB
CONTENT_CACHE_TTL = timedelta(seconds=300)  # 5 minutes

# Exclusion Configuration
EXCLUDED_DIRS = {"node_modules", ".git", "__pycache__", "venv", ".venv", "dist", "build", ".next"}
EXCLUDED_EXTENSIONS = {".pyc", ".log", ".lock"}


class ContentIndexer:
    """Indexes file contents for search functionality.

    Features:
    - Recursive file content indexing
    - .gitignore pattern support
    - Hardcoded exclusions (node_modules, etc.)
    - In-memory caching with TTL (5 minutes)
    - Binary/large file filtering
    - Auto-recovery via cache invalidation

    Simple File Search Sprint 1:
    - Story 1: File Indexing with caching
    - Story 3: Exclusion patterns (.gitignore + hardcoded)
    """

    def __init__(self):
        """Initialize ContentIndexer."""
        # Cache: team_id -> (timestamp, file_contents)
        self._content_cache: dict[str, tuple[datetime, dict[str, str]]] = {}

    def get_or_build_index(self, team_id: str, project_root: Path) -> dict[str, str]:
        """Get content index from cache or build new one.

        Implements Story 1: File Indexing with 5-minute TTL cache.

        Args:
            team_id: Team identifier for cache key
            project_root: Project root directory

        Returns:
            Dict mapping relative file paths to file contents
        """
        # Check cache
        if team_id in self._content_cache:
            timestamp, cached_files = self._content_cache[team_id]
            age = datetime.now() - timestamp
            if age < CONTENT_CACHE_TTL:
                logger.debug(f"[CONTENT-INDEX] Cache hit for {team_id}, age={age.total_seconds()}s")
                return cached_files

        # Cache miss or expired - rebuild index
        logger.info(f"[CONTENT-INDEX] Building index for {team_id}")
        file_contents = self._build_index(project_root)

        # Store in cache
        self._content_cache[team_id] = (datetime.now(), file_contents)

        return file_contents

    def invalidate_cache(self, team_id: str) -> None:
        """Invalidate content cache for a team (auto-recovery on errors).

        Implements Story 1: Auto-recovery mechanism.

        Args:
            team_id: Team identifier
        """
        if team_id in self._content_cache:
            del self._content_cache[team_id]
            logger.info(f"[CONTENT-INDEX] Cache invalidated for {team_id}")

    def _build_index(self, project_root: Path) -> dict[str, str]:
        """Build content index by reading all files in project.

        Implements Story 3: Exclusion patterns (.gitignore + hardcoded).

        Args:
            project_root: Project root directory

        Returns:
            Dict mapping relative file paths to file contents
        """
        file_contents: dict[str, str] = {}

        # Parse .gitignore patterns
        gitignore_patterns = self._parse_gitignore(project_root)

        # Recursively index files
        def index_directory(directory: Path, depth: int = 0) -> None:
            if depth > 20:  # Safety: max depth
                return

            try:
                entries = sorted(directory.iterdir(), key=lambda x: x.name.lower())
            except (PermissionError, OSError):
                return

            for entry in entries:
                # Skip hidden files
                if entry.name.startswith(".") and entry.name not in [".gitignore"]:
                    continue

                # Check hardcoded directory exclusions
                if entry.is_dir() and entry.name in EXCLUDED_DIRS:
                    continue

                # Check hardcoded extension exclusions
                if entry.is_file() and entry.suffix in EXCLUDED_EXTENSIONS:
                    continue

                # Get relative path
                try:
                    rel_path = str(entry.relative_to(project_root))
                except ValueError:
                    continue

                # Check .gitignore patterns
                if self._matches_gitignore(rel_path, gitignore_patterns):
                    continue

                # Read file content
                if entry.is_file():
                    try:
                        # Skip binary files and large files
                        if entry.stat().st_size > MAX_FILE_SIZE:
                            continue

                        content = entry.read_text(encoding='utf-8', errors='ignore')
                        file_contents[rel_path] = content
                    except (PermissionError, OSError, UnicodeDecodeError):
                        pass  # Skip unreadable files

                # Recurse into directories
                elif entry.is_dir():
                    index_directory(entry, depth + 1)

        index_directory(project_root)

        logger.info(f"[CONTENT-INDEX] Indexed {len(file_contents)} files")
        return file_contents

    def _parse_gitignore(self, project_root: Path) -> list[str]:
        """Parse .gitignore file for exclusion patterns.

        Implements Story 3: .gitignore parser.

        Args:
            project_root: Project root directory

        Returns:
            List of glob patterns from .gitignore
        """
        gitignore_path = project_root / ".gitignore"
        if not gitignore_path.exists():
            return []

        patterns: list[str] = []
        try:
            for line in gitignore_path.read_text().splitlines():
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Skip negation patterns (not implemented yet)
                if line.startswith("!"):
                    continue
                patterns.append(line)
        except (PermissionError, OSError):
            pass

        logger.debug(f"[GITIGNORE] Loaded {len(patterns)} patterns")
        return patterns

    def _matches_gitignore(self, rel_path: str, patterns: list[str]) -> bool:
        """Check if path matches any .gitignore pattern.

        Implements Story 3: Pattern matching logic.

        Args:
            rel_path: Relative file path
            patterns: List of glob patterns from .gitignore

        Returns:
            True if path should be excluded, False otherwise
        """
        for pattern in patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith("/"):
                # Match directory and all contents
                if rel_path.startswith(pattern.rstrip("/")):
                    return True
            # Handle glob patterns
            elif fnmatch.fnmatch(rel_path, pattern):
                return True
            # Handle patterns without wildcards
            elif "/" not in pattern:
                # Match filename in any directory
                if fnmatch.fnmatch(Path(rel_path).name, pattern):
                    return True

        return False
