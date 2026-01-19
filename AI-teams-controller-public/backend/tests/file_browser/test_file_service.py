# -*- coding: utf-8 -*-
"""Tests for FileService - file browser backend.

TDD: Security and functional tests for file browsing API.
"""

import tempfile
from pathlib import Path

import pytest


class TestPathValidation:
    """Security tests for path traversal prevention."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure for testing."""
        # Create directory structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "README.md").write_text("# Docs")
        (tmp_path / ".env").write_text("SECRET=value")
        (tmp_path / "credentials.json").write_text("{}")
        return tmp_path

    def test_block_path_traversal_parent(self, temp_project):
        """Should block ../../../etc/passwd traversal."""
        from app.services.file_service import FileService

        service = FileService()
        result = service._validate_path(temp_project, "../../../etc/passwd")
        assert result is None

    def test_block_path_traversal_nested(self, temp_project):
        """Should block foo/../../.. traversal."""
        from app.services.file_service import FileService

        service = FileService()
        result = service._validate_path(temp_project, "foo/../../..")
        assert result is None

    def test_block_absolute_path(self, temp_project):
        """Should block absolute paths like /etc/passwd."""
        from app.services.file_service import FileService

        service = FileService()
        result = service._validate_path(temp_project, "/etc/passwd")
        assert result is None

    def test_allow_valid_path(self, temp_project):
        """Should allow valid relative paths within project."""
        from app.services.file_service import FileService

        service = FileService()
        result = service._validate_path(temp_project, "src/main.py")
        assert result is not None
        assert result == temp_project / "src" / "main.py"

    def test_allow_dotfiles(self, temp_project):
        """Should allow dotfiles within project."""
        from app.services.file_service import FileService

        service = FileService()
        # .env is allowed as path, but content is blacklisted
        result = service._validate_path(temp_project, ".env")
        assert result is not None


class TestBlacklist:
    """Tests for sensitive file blacklist."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create project with sensitive files."""
        (tmp_path / ".env").write_text("SECRET=value")
        (tmp_path / ".env.local").write_text("LOCAL_SECRET=value")
        (tmp_path / "server.pem").write_text("-----BEGIN CERTIFICATE-----")
        (tmp_path / "private.key").write_text("-----BEGIN PRIVATE KEY-----")
        (tmp_path / "credentials.json").write_text('{"api_key": "secret"}')
        (tmp_path / "secrets.yaml").write_text("password: secret")
        (tmp_path / "id_rsa").write_text("-----BEGIN RSA PRIVATE KEY-----")
        (tmp_path / "safe.txt").write_text("This is safe")
        return tmp_path

    def test_blacklist_env_file(self, temp_project):
        """Should blacklist .env files."""
        from app.services.file_service import FileService

        service = FileService()
        assert service._is_blacklisted(temp_project / ".env") is True

    def test_blacklist_env_local(self, temp_project):
        """Should blacklist .env.* files."""
        from app.services.file_service import FileService

        service = FileService()
        assert service._is_blacklisted(temp_project / ".env.local") is True

    def test_blacklist_pem_files(self, temp_project):
        """Should blacklist *.pem files."""
        from app.services.file_service import FileService

        service = FileService()
        assert service._is_blacklisted(temp_project / "server.pem") is True

    def test_blacklist_key_files(self, temp_project):
        """Should blacklist *.key files."""
        from app.services.file_service import FileService

        service = FileService()
        assert service._is_blacklisted(temp_project / "private.key") is True

    def test_blacklist_credentials(self, temp_project):
        """Should blacklist *credentials* files."""
        from app.services.file_service import FileService

        service = FileService()
        assert service._is_blacklisted(temp_project / "credentials.json") is True

    def test_blacklist_secrets(self, temp_project):
        """Should blacklist *secret* files."""
        from app.services.file_service import FileService

        service = FileService()
        assert service._is_blacklisted(temp_project / "secrets.yaml") is True

    def test_blacklist_ssh_keys(self, temp_project):
        """Should blacklist SSH key files."""
        from app.services.file_service import FileService

        service = FileService()
        assert service._is_blacklisted(temp_project / "id_rsa") is True

    def test_allow_safe_files(self, temp_project):
        """Should allow safe files."""
        from app.services.file_service import FileService

        service = FileService()
        assert service._is_blacklisted(temp_project / "safe.txt") is False


class TestFileSizeLimit:
    """Tests for file size limit enforcement."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create project with various file sizes."""
        (tmp_path / "small.txt").write_text("small content")
        (tmp_path / "large.txt").write_bytes(b"x" * (2 * 1024 * 1024))  # 2MB
        return tmp_path

    def test_read_small_file(self, temp_project):
        """Should read files under size limit."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.read_file_content(temp_project, "small.txt")

        assert result.content == "small content"
        assert result.is_truncated is False
        assert result.error is None

    def test_reject_large_file(self, temp_project):
        """Should reject files over 1MB limit."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.read_file_content(temp_project, "large.txt")

        assert result.content is None
        assert result.is_truncated is True
        assert "too large" in result.error.lower()


class TestListDirectory:
    """Tests for directory listing functionality."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create project with various files and directories."""
        (tmp_path / "README.md").write_text("# Project")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")
        (tmp_path / "src" / "utils.py").write_text("# utils")
        (tmp_path / ".hidden").mkdir()
        (tmp_path / ".hidden" / "config.json").write_text("{}")
        (tmp_path / ".gitignore").write_text("*.pyc")
        (tmp_path / "empty_dir").mkdir()
        return tmp_path

    def test_list_root_directory(self, temp_project):
        """Should list root directory contents."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.list_directory(temp_project, "/", depth=1, show_hidden=True)

        assert result.project_root == str(temp_project)
        names = [node.name for node in result.tree]
        assert "README.md" in names
        assert "src" in names

    def test_list_with_hidden_files(self, temp_project):
        """Should include hidden files when show_hidden=True."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.list_directory(temp_project, "/", depth=1, show_hidden=True)

        names = [node.name for node in result.tree]
        assert ".gitignore" in names
        assert ".hidden" in names

    def test_list_without_hidden_files(self, temp_project):
        """Should exclude hidden files when show_hidden=False."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.list_directory(temp_project, "/", depth=1, show_hidden=False)

        names = [node.name for node in result.tree]
        assert ".gitignore" not in names
        assert ".hidden" not in names

    def test_list_subdirectory(self, temp_project):
        """Should list subdirectory contents."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.list_directory(temp_project, "src", depth=1, show_hidden=True)

        names = [node.name for node in result.tree]
        assert "main.py" in names
        assert "utils.py" in names

    def test_list_with_depth(self, temp_project):
        """Should expand directories to specified depth."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.list_directory(temp_project, "/", depth=2, show_hidden=True)

        # Find src directory
        src_node = next(n for n in result.tree if n.name == "src")
        assert src_node.children is not None
        child_names = [c.name for c in src_node.children]
        assert "main.py" in child_names

    def test_list_empty_directory(self, temp_project):
        """Should handle empty directories."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.list_directory(temp_project, "empty_dir", depth=1, show_hidden=True)

        assert result.tree == []

    def test_file_node_has_size(self, temp_project):
        """Files should have size attribute."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.list_directory(temp_project, "/", depth=1, show_hidden=True)

        readme = next(n for n in result.tree if n.name == "README.md")
        assert readme.size is not None
        assert readme.size > 0

    def test_directory_node_no_size(self, temp_project):
        """Directories should have null size."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.list_directory(temp_project, "/", depth=1, show_hidden=True)

        src = next(n for n in result.tree if n.name == "src")
        assert src.size is None


class TestReadFile:
    """Tests for file content reading."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create project with various file types."""
        (tmp_path / "text.txt").write_text("Hello, World!")
        (tmp_path / "script.py").write_text("print('hello')")
        (tmp_path / "data.json").write_text('{"key": "value"}')
        (tmp_path / "binary.bin").write_bytes(b"\x00\x01\x02\x03")
        (tmp_path / ".env").write_text("SECRET=value")
        return tmp_path

    def test_read_text_file(self, temp_project):
        """Should read text file content."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.read_file_content(temp_project, "text.txt")

        assert result.content == "Hello, World!"
        assert result.is_binary is False
        assert result.mime_type == "text/plain"

    def test_read_python_file(self, temp_project):
        """Should read Python file with correct MIME type."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.read_file_content(temp_project, "script.py")

        assert result.content == "print('hello')"
        assert "python" in result.mime_type.lower() or result.mime_type == "text/x-python"

    def test_read_json_file(self, temp_project):
        """Should read JSON file."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.read_file_content(temp_project, "data.json")

        assert result.content == '{"key": "value"}'
        assert "json" in result.mime_type.lower()

    def test_detect_binary_file(self, temp_project):
        """Should detect binary files."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.read_file_content(temp_project, "binary.bin")

        assert result.is_binary is True
        assert result.content is None
        assert "binary" in result.error.lower()

    def test_blacklisted_file_error(self, temp_project):
        """Should return error for blacklisted files."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.read_file_content(temp_project, ".env")

        assert result.content is None
        assert result.error is not None
        assert "sensitive" in result.error.lower() or "blacklist" in result.error.lower()

    def test_nonexistent_file(self, temp_project):
        """Should handle non-existent files."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.read_file_content(temp_project, "nonexistent.txt")

        assert result.content is None
        assert result.error is not None


class TestProjectRootResolution:
    """Tests for project root resolution."""

    def test_resolve_manual_team(self, tmp_path):
        """Should resolve manual team (docs/tmux/{team_id} structure)."""
        from app.services.file_service import FileService

        # Create manual team structure
        team_dir = tmp_path / "docs" / "tmux" / "test_team"
        team_dir.mkdir(parents=True)

        service = FileService()
        # Override _backend_project_root to tmp_path (simulating project root)
        service._backend_project_root = tmp_path

        result = service.resolve_project_root("test_team")
        assert result == tmp_path

    def test_resolve_nonexistent_team(self, tmp_path):
        """Should return None for non-existent team."""
        from app.services.file_service import FileService

        service = FileService()
        result = service.resolve_project_root("nonexistent_team_xyz")
        assert result is None


class TestTmuxFallback:
    """Tests for tmux pane_current_path fallback when team not in known locations."""

    def test_fallback_to_tmux_pane_current_path(self, tmp_path):
        """Should query tmux for pane_current_path when team not in known locations."""
        from unittest.mock import patch, MagicMock
        from app.services.file_service import FileService

        service = FileService()
        # Override _backend_project_root to tmp_path (no docs/tmux/other_project)
        service._backend_project_root = tmp_path

        # Create a real directory to return as the mock path (must exist)
        mock_project_dir = tmp_path / "other_project_root"
        mock_project_dir.mkdir()

        # Mock tmux command to return the existing path
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = str(mock_project_dir) + "\n"

        with patch("app.services.file_service.subprocess.run", return_value=mock_result) as mock_run:
            result = service.resolve_project_root("other_project")

            # Should have called tmux display-message
            mock_run.assert_called()
            call_args = mock_run.call_args[0][0]
            assert "tmux" in call_args
            assert "display-message" in call_args
            assert "pane_current_path" in str(call_args)

            # Should return the path from tmux
            assert result == mock_project_dir

    def test_fallback_returns_none_when_tmux_fails(self, tmp_path):
        """Should return None when tmux query fails."""
        from unittest.mock import patch, MagicMock
        from app.services.file_service import FileService

        service = FileService()
        service._backend_project_root = tmp_path

        # Mock tmux command to fail
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("app.services.file_service.subprocess.run", return_value=mock_result):
            result = service.resolve_project_root("nonexistent_session")
            assert result is None

    def test_fallback_returns_none_when_path_doesnt_exist(self, tmp_path):
        """Should return None when tmux returns a non-existent path."""
        from unittest.mock import patch, MagicMock
        from app.services.file_service import FileService

        service = FileService()
        service._backend_project_root = tmp_path

        # Mock tmux to return a non-existent path
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/nonexistent/path/that/doesnt/exist\n"

        with patch("app.services.file_service.subprocess.run", return_value=mock_result):
            result = service.resolve_project_root("some_session")
            assert result is None

    def test_known_locations_checked_before_tmux(self, tmp_path):
        """Should check known locations before falling back to tmux."""
        from unittest.mock import patch
        from app.services.file_service import FileService

        # Create manual team structure
        team_dir = tmp_path / "docs" / "tmux" / "known_team"
        team_dir.mkdir(parents=True)

        service = FileService()
        service._backend_project_root = tmp_path

        # Mock tmux - should NOT be called
        with patch("app.services.file_service.subprocess.run") as mock_run:
            result = service.resolve_project_root("known_team")

            # Should return known location without calling tmux
            assert result == tmp_path
            mock_run.assert_not_called()
