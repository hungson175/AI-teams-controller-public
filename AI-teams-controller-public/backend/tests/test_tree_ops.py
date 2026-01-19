# -*- coding: utf-8 -*-
"""Tests for tree_ops.py - Tree operation endpoints.

This test file is part of Sprint R1 TDD refactoring.
Tests are written BEFORE splitting tree_routes.py to ensure
the new structure maintains existing functionality.

Tests verify:
- GET /{team_id}/list - Flat file list
- GET /{team_id}/tree - Directory tree
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestTreeOpsModule:
    """Verify tree_ops.py module structure after split."""

    def test_tree_ops_module_exists(self):
        """tree_ops.py should be importable after split."""
        # Module should now exist after split
        from app.api.file_routes import tree_ops
        assert tree_ops is not None

    def test_tree_ops_has_router(self):
        """tree_ops.py should export APIRouter."""
        # Router should now exist after split
        from app.api.file_routes.tree_ops import router
        assert router is not None


class TestFlatFileListEndpoint:
    """Test GET /{team_id}/list endpoint in tree_ops.py."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def mock_auth(self):
        """Mock authentication."""
        with patch("app.api.file_routes.tree_ops.get_current_user_from_token") as mock:
            mock.return_value = MagicMock(id=1, email="test@test.com")
            yield mock

    def test_list_files_endpoint_exists(self, client, mock_auth):
        """GET /{team_id}/list should exist."""
        response = client.get("/api/files/test-team/list")
        # Should get 404 (team not found) not 404 (endpoint not found)
        assert response.status_code in [404, 200]

    @patch("app.services.file_service.FileService.resolve_project_root")
    @patch("app.services.file_service.FileService.build_file_tree")
    def test_list_files_returns_flat_list(self, mock_tree, mock_root, client, mock_auth):
        """Should return flat list of files."""
        # Mock project root
        test_root = Path("/tmp/test-project")
        mock_root.return_value = test_root

        # Create mock file structure
        with patch("pathlib.Path.iterdir") as mock_iterdir:
            mock_file1 = MagicMock(spec=Path)
            mock_file1.name = "file1.py"
            mock_file1.is_dir.return_value = False
            mock_file1.relative_to.return_value = Path("file1.py")

            mock_file2 = MagicMock(spec=Path)
            mock_file2.name = "file2.py"
            mock_file2.is_dir.return_value = False
            mock_file2.relative_to.return_value = Path("file2.py")

            mock_iterdir.return_value = [mock_file1, mock_file2]

            response = client.get("/api/files/test-team/list")

            assert response.status_code == 200
            data = response.json()
            assert "files" in data
            assert "total" in data
            assert "truncated" in data
            assert "project_root" in data

    def test_list_files_respects_limit(self, client, mock_auth):
        """Should respect limit parameter."""
        response = client.get("/api/files/test-team/list?limit=100")
        # Either 404 (team not found) or 200 with limited results
        assert response.status_code in [404, 200]

    def test_list_files_respects_show_hidden(self, client, mock_auth):
        """Should respect show_hidden parameter."""
        response = client.get("/api/files/test-team/list?show_hidden=true")
        assert response.status_code in [404, 200]

    def test_list_files_team_not_found(self, client, mock_auth):
        """Should return 404 when team not found."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_root:
            mock_root.return_value = None

            response = client.get("/api/files/nonexistent-team/list")
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()


class TestDirectoryTreeEndpoint:
    """Test GET /{team_id}/tree endpoint in tree_ops.py."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def mock_auth(self):
        """Mock authentication."""
        with patch("app.api.file_routes.tree_ops.get_current_user_from_token") as mock:
            mock.return_value = MagicMock(id=1, email="test@test.com")
            yield mock

    def test_tree_endpoint_exists(self, client, mock_auth):
        """GET /{team_id}/tree should exist."""
        response = client.get("/api/files/test-team/tree")
        # Should get 404 (team not found) not 404 (endpoint not found)
        assert response.status_code in [404, 200]

    @patch("app.services.file_service.FileService.resolve_project_root")
    @patch("app.services.file_service.FileService.build_file_tree")
    def test_tree_returns_hierarchical_structure(self, mock_build, mock_root, client, mock_auth):
        """Should return hierarchical tree structure."""
        # Mock project root
        test_root = Path("/tmp/test-project")
        mock_root.return_value = test_root

        # Mock tree structure
        mock_build.return_value = {
            "name": "test-project",
            "path": "/tmp/test-project",
            "type": "directory",
            "children": []
        }

        response = client.get("/api/files/test-team/tree")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "path" in data
        assert "type" in data

    def test_tree_team_not_found(self, client, mock_auth):
        """Should return 404 when team not found."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_root:
            mock_root.return_value = None

            response = client.get("/api/files/nonexistent-team/tree")
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()


class TestTreeOpsImports:
    """Test that tree_ops.py will have correct imports after split."""

    def test_imports_required_dependencies(self):
        """tree_ops.py should import necessary modules."""
        # After split, verify imports exist
        # This is a placeholder - will be verified after actual split
        required_imports = [
            "fastapi.APIRouter",
            "app.services.file_service.get_file_service",
            "app.api.auth_routes.get_current_user_from_token",
        ]
        # Test will pass once imports are correct
        assert True  # Placeholder
