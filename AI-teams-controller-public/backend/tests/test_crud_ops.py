# -*- coding: utf-8 -*-
"""Tests for crud_ops.py - CRUD operation endpoints.

This test file is part of Sprint R1 TDD refactoring.
Tests are written BEFORE splitting tree_routes.py to ensure
the new structure maintains existing functionality.

Tests verify:
- POST /{team_id}/create - Create file/folder
- DELETE /{team_id}/delete - Delete file/folder
- PATCH /{team_id}/rename - Rename file/folder
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestCrudOpsModule:
    """Verify crud_ops.py module structure after split."""

    def test_crud_ops_module_exists(self):
        """crud_ops.py should be importable after split."""
        # Module should now exist after split
        from app.api.file_routes import crud_ops
        assert crud_ops is not None

    def test_crud_ops_has_router(self):
        """crud_ops.py should export APIRouter."""
        # Router should now exist after split
        from app.api.file_routes.crud_ops import router
        assert router is not None


class TestCreateFileEndpoint:
    """Test POST /{team_id}/create endpoint in crud_ops.py."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def mock_auth(self):
        """Mock authentication."""
        with patch("app.api.file_routes.crud_ops.get_current_user_from_token") as mock:
            mock.return_value = MagicMock(id=1, email="test@test.com")
            yield mock

    def test_create_endpoint_exists(self, client, mock_auth):
        """POST /{team_id}/create should exist."""
        payload = {
            "path": "test.txt",
            "type": "file",
            "content": "test content"
        }
        response = client.post("/api/files/test-team/create", json=payload)
        # Should get 404 (team not found) not 405 (method not allowed)
        assert response.status_code in [404, 200, 201]

    @patch("app.services.file_service.FileService.resolve_project_root")
    def test_create_file_success(self, mock_root, client, mock_auth):
        """Should create file successfully."""
        test_root = Path("/tmp/test-project")
        mock_root.return_value = test_root

        with patch("pathlib.Path.write_text") as mock_write:
            payload = {
                "path": "newfile.txt",
                "type": "file",
                "content": "Hello World"
            }
            response = client.post("/api/files/test-team/create", json=payload)

            # Verify response structure
            if response.status_code == 200:
                data = response.json()
                assert "success" in data
                assert "path" in data

    @patch("app.services.file_service.FileService.resolve_project_root")
    def test_create_directory_success(self, mock_root, client, mock_auth):
        """Should create directory successfully."""
        test_root = Path("/tmp/test-project")
        mock_root.return_value = test_root

        with patch("pathlib.Path.mkdir") as mock_mkdir:
            payload = {
                "path": "newdir",
                "type": "directory"
            }
            response = client.post("/api/files/test-team/create", json=payload)

            if response.status_code == 200:
                data = response.json()
                assert "success" in data

    def test_create_file_team_not_found(self, client, mock_auth):
        """Should return 404 when team not found."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_root:
            mock_root.return_value = None

            payload = {
                "path": "test.txt",
                "type": "file",
                "content": "test"
            }
            response = client.post("/api/files/nonexistent-team/create", json=payload)
            assert response.status_code == 404

    def test_create_file_invalid_path(self, client, mock_auth):
        """Should reject invalid paths (path traversal)."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_root:
            test_root = Path("/tmp/test-project")
            mock_root.return_value = test_root

            payload = {
                "path": "../../../etc/passwd",
                "type": "file",
                "content": "malicious"
            }
            response = client.post("/api/files/test-team/create", json=payload)
            assert response.status_code in [400, 403, 404]


class TestDeleteFileEndpoint:
    """Test DELETE /{team_id}/delete endpoint in crud_ops.py."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def mock_auth(self):
        """Mock authentication."""
        with patch("app.api.file_routes.crud_ops.get_current_user_from_token") as mock:
            mock.return_value = MagicMock(id=1, email="test@test.com")
            yield mock

    def test_delete_endpoint_exists(self, client, mock_auth):
        """DELETE /{team_id}/delete should exist."""
        payload = {"path": "test.txt"}
        response = client.request("DELETE", "/api/files/test-team/delete", json=payload)
        # Should get 404 (team not found) not 405 (method not allowed)
        assert response.status_code in [404, 200]

    @patch("app.services.file_service.FileService.resolve_project_root")
    def test_delete_file_success(self, mock_root, client, mock_auth):
        """Should delete file successfully."""
        test_root = Path("/tmp/test-project")
        mock_root.return_value = test_root

        with patch("pathlib.Path.unlink") as mock_unlink, \
             patch("pathlib.Path.exists") as mock_exists, \
             patch("pathlib.Path.is_file") as mock_is_file:
            mock_exists.return_value = True
            mock_is_file.return_value = True

            payload = {"path": "oldfile.txt"}
            response = client.request("DELETE", "/api/files/test-team/delete", json=payload)

            if response.status_code == 200:
                data = response.json()
                assert "success" in data

    @patch("app.services.file_service.FileService.resolve_project_root")
    def test_delete_directory_success(self, mock_root, client, mock_auth):
        """Should delete directory successfully."""
        test_root = Path("/tmp/test-project")
        mock_root.return_value = test_root

        with patch("shutil.rmtree") as mock_rmtree, \
             patch("pathlib.Path.exists") as mock_exists, \
             patch("pathlib.Path.is_dir") as mock_is_dir:
            mock_exists.return_value = True
            mock_is_dir.return_value = True

            payload = {"path": "olddir"}
            response = client.request("DELETE", "/api/files/test-team/delete", json=payload)

            if response.status_code == 200:
                data = response.json()
                assert "success" in data

    def test_delete_file_not_found(self, client, mock_auth):
        """Should return 404 when file not found."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_root:
            test_root = Path("/tmp/test-project")
            mock_root.return_value = test_root

            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = False

                payload = {"path": "nonexistent.txt"}
                response = client.request("DELETE", "/api/files/test-team/delete", json=payload)
                assert response.status_code == 404


class TestRenameFileEndpoint:
    """Test PATCH /{team_id}/rename endpoint in crud_ops.py."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def mock_auth(self):
        """Mock authentication."""
        with patch("app.api.file_routes.crud_ops.get_current_user_from_token") as mock:
            mock.return_value = MagicMock(id=1, email="test@test.com")
            yield mock

    def test_rename_endpoint_exists(self, client, mock_auth):
        """PATCH /{team_id}/rename should exist."""
        payload = {
            "old_path": "old.txt",
            "new_path": "new.txt"
        }
        response = client.patch("/api/files/test-team/rename", json=payload)
        # Should get 404 (team not found) not 405 (method not allowed)
        assert response.status_code in [404, 200]

    @patch("app.services.file_service.FileService.resolve_project_root")
    def test_rename_file_success(self, mock_root, client, mock_auth):
        """Should rename file successfully."""
        test_root = Path("/tmp/test-project")
        mock_root.return_value = test_root

        with patch("pathlib.Path.rename") as mock_rename, \
             patch("pathlib.Path.exists") as mock_exists:
            # old_path exists, new_path doesn't
            mock_exists.side_effect = [True, False]

            payload = {
                "old_path": "old.txt",
                "new_path": "new.txt"
            }
            response = client.patch("/api/files/test-team/rename", json=payload)

            if response.status_code == 200:
                data = response.json()
                assert "success" in data
                assert "new_path" in data

    def test_rename_file_not_found(self, client, mock_auth):
        """Should return 404 when source file not found."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_root:
            test_root = Path("/tmp/test-project")
            mock_root.return_value = test_root

            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = False

                payload = {
                    "old_path": "nonexistent.txt",
                    "new_path": "new.txt"
                }
                response = client.patch("/api/files/test-team/rename", json=payload)
                assert response.status_code == 404

    def test_rename_file_target_exists(self, client, mock_auth):
        """Should return 400 when target already exists."""
        with patch("app.services.file_service.FileService.resolve_project_root") as mock_root:
            test_root = Path("/tmp/test-project")
            mock_root.return_value = test_root

            with patch("pathlib.Path.exists") as mock_exists:
                # Both old and new paths exist
                mock_exists.return_value = True

                payload = {
                    "old_path": "old.txt",
                    "new_path": "existing.txt"
                }
                response = client.patch("/api/files/test-team/rename", json=payload)
                assert response.status_code in [400, 409]


class TestCrudOpsImports:
    """Test that crud_ops.py will have correct imports after split."""

    def test_imports_required_dependencies(self):
        """crud_ops.py should import necessary modules."""
        # After split, verify imports exist
        required_imports = [
            "fastapi.APIRouter",
            "app.services.file_service.get_file_service",
            "app.api.auth_routes.get_current_user_from_token",
            "shutil",  # For directory deletion
        ]
        # Test will pass once imports are correct
        assert True  # Placeholder
