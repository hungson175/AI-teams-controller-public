# -*- coding: utf-8 -*-
"""Tests for file browser API routes.

TDD: API endpoint tests for file browsing.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.models.file_schemas import FileContent, FileNode, TreeResponse


@pytest.fixture
def client():
    """Create test client with SESSION_TOKEN auth (file routes require auth)."""
    from app.main import app
    from app.api.auth_routes import SESSION_TOKEN

    return TestClient(app, headers={"Authorization": f"Bearer {SESSION_TOKEN}"})


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    (tmp_path / "README.md").write_text("# Test Project")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / ".env").write_text("SECRET=value")
    return tmp_path


class TestGetTreeEndpoint:
    """Tests for GET /api/files/{team_id}/tree endpoint."""

    def test_tree_success(self, client, temp_project):
        """Should return directory tree for valid team."""
        with patch(
            "app.api.file_routes.tree_ops.get_file_service"
        ) as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = temp_project
            mock_service.list_directory.return_value = TreeResponse(
                project_root=str(temp_project),
                tree=[
                    FileNode(
                        name="README.md",
                        path="README.md",
                        type="file",
                        size=14,
                        children=None,
                    )
                ],
            )
            mock_get_service.return_value = mock_service

            response = client.get("/api/files/test_team/tree")

            assert response.status_code == 200
            data = response.json()
            assert "project_root" in data
            assert "tree" in data

    def test_tree_team_not_found(self, client):
        """Should return 404 for non-existent team."""
        with patch(
            "app.api.file_routes.tree_ops.get_file_service"
        ) as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = None
            mock_get_service.return_value = mock_service

            response = client.get("/api/files/nonexistent_team/tree")

            assert response.status_code == 404

    def test_tree_with_depth(self, client, temp_project):
        """Should accept depth parameter."""
        with patch(
            "app.api.file_routes.tree_routes.get_file_service"
        ) as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = temp_project
            mock_service.list_directory.return_value = TreeResponse(
                project_root=str(temp_project),
                tree=[],
            )
            mock_get_service.return_value = mock_service

            response = client.get("/api/files/test_team/tree?depth=3")

            assert response.status_code == 200
            mock_service.list_directory.assert_called_once()
            call_args = mock_service.list_directory.call_args
            assert call_args.kwargs.get("depth") == 3 or call_args[1].get("depth") == 3

    def test_tree_show_hidden_false(self, client, temp_project):
        """Should accept show_hidden=false parameter."""
        with patch(
            "app.api.file_routes.tree_routes.get_file_service"
        ) as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = temp_project
            mock_service.list_directory.return_value = TreeResponse(
                project_root=str(temp_project),
                tree=[],
            )
            mock_get_service.return_value = mock_service

            response = client.get("/api/files/test_team/tree?show_hidden=false")

            assert response.status_code == 200


class TestGetContentEndpoint:
    """Tests for GET /api/files/{team_id}/content endpoint."""

    def test_content_success(self, client, temp_project):
        """Should return file content for valid path."""
        with patch(
            "app.api.file_routes.content_routes.get_file_service"
        ) as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = temp_project
            mock_service.read_file_content.return_value = FileContent(
                path="README.md",
                name="README.md",
                size=14,
                mime_type="text/markdown",
                content="# Test Project",
                is_binary=False,
                is_truncated=False,
                error=None,
            )
            mock_get_service.return_value = mock_service

            response = client.get("/api/files/test_team/content?path=README.md")

            assert response.status_code == 200
            data = response.json()
            assert data["content"] == "# Test Project"
            assert data["is_binary"] is False

    def test_content_team_not_found(self, client):
        """Should return 404 for non-existent team."""
        with patch(
            "app.api.file_routes.content_routes.get_file_service"
        ) as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = None
            mock_get_service.return_value = mock_service

            response = client.get("/api/files/nonexistent_team/content?path=README.md")

            assert response.status_code == 404

    def test_content_missing_path(self, client, temp_project):
        """Should return 422 when path parameter is missing."""
        with patch(
            "app.api.file_routes.content_routes.get_file_service"
        ) as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = temp_project
            mock_get_service.return_value = mock_service

            response = client.get("/api/files/test_team/content")

            # FastAPI returns 422 for missing required query params
            assert response.status_code == 422

    def test_content_path_traversal_blocked(self, client, temp_project):
        """Should block path traversal attempts."""
        with patch(
            "app.api.file_routes.content_routes.get_file_service"
        ) as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = temp_project
            mock_service.read_file_content.return_value = FileContent(
                path="../../../etc/passwd",
                name="passwd",
                size=0,
                mime_type="application/octet-stream",
                content=None,
                is_binary=False,
                is_truncated=False,
                error="Invalid path or access denied",
            )
            mock_get_service.return_value = mock_service

            response = client.get(
                "/api/files/test_team/content?path=../../../etc/passwd"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["content"] is None
            assert data["error"] is not None

    def test_content_blacklisted_file(self, client, temp_project):
        """Should return error for blacklisted files."""
        with patch(
            "app.api.file_routes.content_routes.get_file_service"
        ) as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = temp_project
            mock_service.read_file_content.return_value = FileContent(
                path=".env",
                name=".env",
                size=12,
                mime_type="text/plain",
                content=None,
                is_binary=False,
                is_truncated=False,
                error="Sensitive file - content blocked for security",
            )
            mock_get_service.return_value = mock_service

            response = client.get("/api/files/test_team/content?path=.env")

            assert response.status_code == 200
            data = response.json()
            assert data["content"] is None
            assert "sensitive" in data["error"].lower() or "security" in data["error"].lower()


# ============================================================
# Sprint 2 Story 2: Path Autocomplete Tests
# ============================================================


class TestAutocompleteEndpoint:
    """Tests for GET /api/files/autocomplete endpoint (Sprint 2 Story 2)."""

    @pytest.fixture
    def mock_project_root(self, tmp_path):
        """Create a mock project structure for testing."""
        # Create directories
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "components").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "docs").mkdir()

        # Create files
        (tmp_path / "main.py").write_text("# main")
        (tmp_path / "setup.py").write_text("# setup")
        (tmp_path / "README.md").write_text("# README")
        (tmp_path / "src" / "app.py").write_text("# app")
        (tmp_path / "src" / "utils.py").write_text("# utils")

        # Create hidden files (should be filtered)
        (tmp_path / ".git").mkdir()
        (tmp_path / ".env").write_text("SECRET=xxx")
        (tmp_path / ".gitignore").write_text("*.pyc")

        return tmp_path

    def test_returns_directory_completions(self, client, mock_project_root):
        """Should return list of items in directory when path ends with /."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_resolve:
            mock_resolve.return_value = mock_project_root

            response = client.get(
                "/api/files/autocomplete",
                params={"path": "src/", "team": "test-team"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "completions" in data
            # src/ contains app.py, utils.py, and components/
            names = [c["name"] for c in data["completions"]]
            assert "app.py" in names or "components" in names

    def test_returns_file_completions_with_prefix(self, client, mock_project_root):
        """Should return files/dirs matching prefix."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_resolve:
            mock_resolve.return_value = mock_project_root

            response = client.get(
                "/api/files/autocomplete",
                params={"path": "src/a", "team": "test-team"}
            )

            assert response.status_code == 200
            data = response.json()
            # Should match "app.py" which starts with "a"
            names = [c["name"] for c in data["completions"]]
            assert "app.py" in names

    def test_adds_trailing_slash_to_directories(self, client, mock_project_root):
        """Should add trailing slash to directory completions."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_resolve:
            mock_resolve.return_value = mock_project_root

            response = client.get(
                "/api/files/autocomplete",
                params={"path": "sr", "team": "test-team"}
            )

            assert response.status_code == 200
            data = response.json()
            # Find "src" completion
            src_completion = next(
                (c for c in data["completions"] if c["name"] == "src"),
                None
            )
            assert src_completion is not None
            assert src_completion["path"].endswith("/")
            assert src_completion["isDir"] is True

    def test_rejects_path_traversal(self, client, mock_project_root):
        """Should return 400 for path traversal attempts."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_resolve:
            mock_resolve.return_value = mock_project_root

            response = client.get(
                "/api/files/autocomplete",
                params={"path": "../../../etc/passwd", "team": "test-team"}
            )

            assert response.status_code == 400
            assert "traversal" in response.json()["detail"].lower()

    def test_returns_empty_for_nonexistent_path(self, client, mock_project_root):
        """Should return empty completions for nonexistent directory."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_resolve:
            mock_resolve.return_value = mock_project_root

            response = client.get(
                "/api/files/autocomplete",
                params={"path": "nonexistent/", "team": "test-team"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["completions"] == []

    def test_respects_limit_parameter(self, client, mock_project_root):
        """Should respect limit parameter."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_resolve:
            mock_resolve.return_value = mock_project_root

            response = client.get(
                "/api/files/autocomplete",
                params={"path": "", "team": "test-team", "limit": 2}
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["completions"]) <= 2

    def test_hides_hidden_files(self, client, mock_project_root):
        """Should not return dotfiles (hidden files)."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_resolve:
            mock_resolve.return_value = mock_project_root

            response = client.get(
                "/api/files/autocomplete",
                params={"path": "", "team": "test-team"}
            )

            assert response.status_code == 200
            data = response.json()
            names = [c["name"] for c in data["completions"]]
            # Should NOT contain hidden files
            assert ".git" not in names
            assert ".env" not in names
            assert ".gitignore" not in names

    def test_sorts_directories_before_files(self, client, mock_project_root):
        """Should sort directories before files."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_resolve:
            mock_resolve.return_value = mock_project_root

            response = client.get(
                "/api/files/autocomplete",
                params={"path": "", "team": "test-team", "limit": 20}
            )

            assert response.status_code == 200
            data = response.json()
            completions = data["completions"]

            # Find first file and first directory indices
            first_dir_idx = None
            first_file_idx = None

            for i, c in enumerate(completions):
                if c["isDir"] and first_dir_idx is None:
                    first_dir_idx = i
                if not c["isDir"] and first_file_idx is None:
                    first_file_idx = i

            # If both exist, directories should come first
            if first_dir_idx is not None and first_file_idx is not None:
                assert first_dir_idx < first_file_idx

    def test_returns_404_for_unknown_team(self, client):
        """Should return 404 if team not found."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_resolve:
            mock_resolve.return_value = None

            response = client.get(
                "/api/files/autocomplete",
                params={"path": "", "team": "nonexistent-team"}
            )

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_case_insensitive_prefix_matching(self, client, mock_project_root):
        """Should match prefix case-insensitively."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_resolve:
            mock_resolve.return_value = mock_project_root

            response = client.get(
                "/api/files/autocomplete",
                params={"path": "READ", "team": "test-team"}
            )

            assert response.status_code == 200
            data = response.json()
            names = [c["name"] for c in data["completions"]]
            # Should match "README.md" even with uppercase query
            assert "README.md" in names


# ============================================================
# Sprint 9: DELETE and PATCH Endpoints (TDD)
# ============================================================


class TestDeleteEndpoint:
    """Tests for DELETE /api/files/{team_id}/delete endpoint (Sprint 9)."""

    @pytest.fixture
    def delete_project(self, tmp_path):
        """Create test project with files and folders."""
        # Create files
        (tmp_path / "file1.txt").write_text("content")
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "readme.md").write_text("# Docs")

        # Create protected paths
        (tmp_path / ".git").mkdir()
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "__pycache__").mkdir()

        return tmp_path

    def test_delete_existing_file(self, client, delete_project):
        """DELETE existing file should return 200."""
        with patch("app.api.file_routes.tree_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = delete_project
            mock_get_service.return_value = mock_service

            response = client.request(
                "DELETE",
                "/api/files/test_team/delete",
                json={"path": "file1.txt"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["type"] == "file"
            assert "file1.txt" in data["path"]

    def test_delete_existing_folder(self, client, delete_project):
        """DELETE existing folder should return 200."""
        with patch("app.api.file_routes.tree_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = delete_project
            mock_get_service.return_value = mock_service

            response = client.request(
                "DELETE",
                "/api/files/test_team/delete",
                json={"path": "docs"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["type"] == "folder"

    def test_delete_not_found(self, client, delete_project):
        """DELETE non-existent path should return 404."""
        with patch("app.api.file_routes.tree_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = delete_project
            mock_get_service.return_value = mock_service

            response = client.request(
                "DELETE",
                "/api/files/test_team/delete",
                json={"path": "nonexistent.txt"}
            )

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_delete_path_traversal_blocked(self, client, delete_project):
        """DELETE with path traversal should return 400."""
        with patch("app.api.file_routes.tree_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = delete_project
            mock_get_service.return_value = mock_service

            response = client.request(
                "DELETE",
                "/api/files/test_team/delete",
                json={"path": "../../../etc/passwd"}
            )

            assert response.status_code == 400
            assert "traversal" in response.json()["detail"].lower()

    def test_delete_protected_path_git(self, client, delete_project):
        """DELETE .git should return 400."""
        with patch("app.api.file_routes.tree_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = delete_project
            mock_get_service.return_value = mock_service

            response = client.request(
                "DELETE",
                "/api/files/test_team/delete",
                json={"path": ".git"}
            )

            assert response.status_code == 400
            assert "protected" in response.json()["detail"].lower()


class TestRenameEndpoint:
    """Tests for PATCH /api/files/{team_id}/rename endpoint (Sprint 9)."""

    @pytest.fixture
    def rename_project(self, tmp_path):
        """Create test project for rename tests."""
        # Create files
        (tmp_path / "old_file.txt").write_text("content")
        (tmp_path / "existing.txt").write_text("exists")
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "readme.md").write_text("# Docs")

        return tmp_path

    def test_rename_file_success(self, client, rename_project):
        """PATCH rename file should return 200."""
        with patch("app.api.file_routes.tree_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = rename_project
            mock_get_service.return_value = mock_service

            response = client.request(
                "PATCH",
                "/api/files/test_team/rename",
                json={"old_path": "old_file.txt", "new_name": "new_file.txt"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["old_path"] == "old_file.txt"
            assert "new_file.txt" in data["new_path"]
            assert data["type"] == "file"

    def test_rename_folder_success(self, client, rename_project):
        """PATCH rename folder should return 200."""
        with patch("app.api.file_routes.tree_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = rename_project
            mock_get_service.return_value = mock_service

            response = client.request(
                "PATCH",
                "/api/files/test_team/rename",
                json={"old_path": "docs", "new_name": "documentation"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["type"] == "folder"

    def test_rename_not_found(self, client, rename_project):
        """PATCH rename non-existent path should return 404."""
        with patch("app.api.file_routes.tree_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = rename_project
            mock_get_service.return_value = mock_service

            response = client.request(
                "PATCH",
                "/api/files/test_team/rename",
                json={"old_path": "nonexistent.txt", "new_name": "new.txt"}
            )

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_rename_path_traversal_blocked(self, client, rename_project):
        """PATCH with path traversal should return 400."""
        with patch("app.api.file_routes.tree_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = rename_project
            mock_get_service.return_value = mock_service

            response = client.request(
                "PATCH",
                "/api/files/test_team/rename",
                json={"old_path": "../../../etc/passwd", "new_name": "hacked.txt"}
            )

            assert response.status_code == 400
            assert "traversal" in response.json()["detail"].lower()

    def test_rename_invalid_characters(self, client, rename_project):
        """PATCH with invalid characters in new_name should return 400."""
        with patch("app.api.file_routes.tree_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = rename_project
            mock_get_service.return_value = mock_service

            # Test various invalid characters
            invalid_names = ["file/name.txt", "file\\name.txt", "file:name.txt", "file*name.txt"]

            for invalid_name in invalid_names:
                response = client.request(
                    "PATCH",
                    "/api/files/test_team/rename",
                    json={"old_path": "old_file.txt", "new_name": invalid_name}
                )

                assert response.status_code == 400
                assert "invalid" in response.json()["detail"].lower()

    def test_rename_already_exists(self, client, rename_project):
        """PATCH rename to existing name should return 400."""
        with patch("app.api.file_routes.tree_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = rename_project
            mock_get_service.return_value = mock_service

            response = client.request(
                "PATCH",
                "/api/files/test_team/rename",
                json={"old_path": "old_file.txt", "new_name": "existing.txt"}
            )

            assert response.status_code == 400
            assert "exists" in response.json()["detail"].lower()


# ============================================================
# Sprint 12: PUT Endpoint for File Editing (TDD)
# ============================================================


class TestPutEndpoint:
    """Tests for PUT /api/files/{team}/{path} endpoint (Sprint 12)."""

    @pytest.fixture
    def edit_project(self, tmp_path):
        """Create test project for file editing tests."""
        # Create existing files
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "test.md").write_text("# Original Content")
        (tmp_path / "config.txt").write_text("original config")

        # Create protected paths
        (tmp_path / ".git").mkdir()
        (tmp_path / "node_modules").mkdir()

        return tmp_path

    def test_save_valid_file(self, client, edit_project):
        """PUT valid file should save content and return 200."""
        with patch("app.api.file_routes.content_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = edit_project
            mock_get_service.return_value = mock_service

            new_content = "This is the new file content.\nMultiple lines supported."

            response = client.put(
                "/api/files/test_team/docs/test.md",
                content=new_content,
                headers={"Content-Type": "text/plain"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "saved successfully" in data["message"].lower()
            assert data["path"] == "docs/test.md"
            assert data["size"] == len(new_content)

            # Verify file was actually written
            saved_file = edit_project / "docs" / "test.md"
            assert saved_file.read_text() == new_content

    def test_path_traversal_blocked(self, client, edit_project):
        """PUT with path traversal should return 400."""
        with patch("app.api.file_routes.content_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = edit_project
            mock_get_service.return_value = mock_service

            # Path traversal - URL encode dots to bypass client normalization
            # %2E%2E = ..
            response = client.put(
                "/api/files/test_team/docs/%2E%2E/sensitive.txt",
                content="malicious content",
                headers={"Content-Type": "text/plain"}
            )

            assert response.status_code == 400
            data = response.json()
            assert "traversal" in data["detail"].lower()

    def test_protected_path_blocked(self, client, edit_project):
        """PUT to protected path should return 403."""
        with patch("app.api.file_routes.content_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = edit_project
            mock_get_service.return_value = mock_service

            # Test .git directory (protected)
            response = client.put(
                "/api/files/test_team/.git/config",
                content="malicious content",
                headers={"Content-Type": "text/plain"}
            )

            assert response.status_code == 403
            data = response.json()
            assert "protected" in data["detail"].lower() or "forbidden" in data["detail"].lower()

    def test_file_too_large(self, client, edit_project):
        """PUT file larger than 10MB should return 413."""
        with patch("app.api.file_routes.content_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = edit_project
            mock_get_service.return_value = mock_service

            # Create content larger than 10MB (10 * 1024 * 1024 bytes)
            large_content = "x" * (10 * 1024 * 1024 + 1)

            response = client.put(
                "/api/files/test_team/large_file.txt",
                content=large_content,
                headers={"Content-Type": "text/plain"}
            )

            assert response.status_code == 413
            data = response.json()
            assert "too large" in data["detail"].lower() or "size" in data["detail"].lower()

    def test_invalid_team(self, client):
        """PUT with invalid team should return 404."""
        with patch("app.api.file_routes.content_routes.get_file_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = None  # Team not found
            mock_get_service.return_value = mock_service

            response = client.put(
                "/api/files/nonexistent_team/test.md",
                content="some content",
                headers={"Content-Type": "text/plain"}
            )

            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"].lower()
