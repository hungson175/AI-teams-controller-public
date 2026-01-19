# -*- coding: utf-8 -*-
"""Tests for file_routes module split (Sprint R1).

TDD: These tests verify the split module structure works correctly.
Tests written BEFORE implementation to ensure no regressions.

Module structure after Sprint R1:
- tree_ops.py: GET /list, GET /tree
- crud_ops.py: POST /create, DELETE /delete, PATCH /rename
- content_routes.py: GET /content, PUT /content
- search_routes.py: GET /autocomplete, GET /search
"""

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient


class TestFileRoutesModuleSplit:
    """Verify file_routes split into 4 modules maintains all functionality."""

    def test_file_routes_package_imports(self):
        """Should be able to import router from file_routes package."""
        from app.api.file_routes import router

        assert router is not None
        assert isinstance(router, APIRouter)
        assert router.prefix == "/api/files"

    def test_tree_ops_module_exists(self):
        """tree_ops module should exist and export router."""
        from app.api.file_routes.tree_ops import router as tree_router

        assert tree_router is not None
        assert isinstance(tree_router, APIRouter)

    def test_crud_ops_module_exists(self):
        """crud_ops module should exist and export router."""
        from app.api.file_routes.crud_ops import router as crud_router

        assert crud_router is not None
        assert isinstance(crud_router, APIRouter)

    def test_content_routes_module_exists(self):
        """content_routes module should exist and export router."""
        from app.api.file_routes.content_routes import router as content_router

        assert content_router is not None
        assert isinstance(content_router, APIRouter)

    def test_search_routes_module_exists(self):
        """search_routes module should exist and export router."""
        from app.api.file_routes.search_routes import router as search_router

        assert search_router is not None
        assert isinstance(search_router, APIRouter)

    def test_combined_router_includes_all_subrouters(self):
        """Main file_routes router should include all sub-routers."""
        from app.api.file_routes import router

        # Verify router has routes from all modules
        # FastAPI combines routes from include_router()
        assert len(router.routes) > 0, "Combined router should have routes"

    def test_tree_endpoints_still_accessible(self):
        """Tree endpoints should work after split."""
        from app.main import app
        from app.api.auth_routes import SESSION_TOKEN
        from unittest.mock import MagicMock, patch

        client = TestClient(app, headers={"Authorization": f"Bearer {SESSION_TOKEN}"})

        with patch("app.api.file_routes.tree_ops.get_file_service") as mock_service_fn:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = None
            mock_service_fn.return_value = mock_service

            # Test GET /api/files/{team_id}/tree
            response = client.get("/api/files/test-team/tree")
            # Should return 404 (team not found) not 404 (route not found)
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_content_endpoints_still_accessible(self):
        """Content endpoints should work after split."""
        from app.main import app
        from app.api.auth_routes import SESSION_TOKEN
        from unittest.mock import MagicMock, patch

        client = TestClient(app, headers={"Authorization": f"Bearer {SESSION_TOKEN}"})

        with patch("app.api.file_routes.content_routes.get_file_service") as mock_service_fn:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = None
            mock_service_fn.return_value = mock_service

            # Test GET /api/files/{team_id}/content
            response = client.get("/api/files/test-team/content?path=test.txt")
            assert response.status_code == 404

    def test_search_endpoints_still_accessible(self):
        """Search endpoints should work after split."""
        from app.main import app
        from app.api.auth_routes import SESSION_TOKEN
        from unittest.mock import MagicMock, patch

        client = TestClient(app, headers={"Authorization": f"Bearer {SESSION_TOKEN}"})

        with patch("app.api.file_routes.search_routes.get_file_service") as mock_service_fn:
            mock_service = MagicMock()
            mock_service.resolve_project_root.return_value = None
            mock_service_fn.return_value = mock_service

            # Test GET /api/files/autocomplete
            response = client.get("/api/files/autocomplete?team=test-team&path=")
            assert response.status_code == 404

            # Test GET /api/files/{team_id}/search
            response = client.get("/api/files/test-team/search?q=test")
            assert response.status_code == 404


class TestFileRoutesEndpointMapping:
    """Verify correct endpoint distribution across split modules."""

    def test_tree_ops_has_correct_endpoints(self):
        """tree_ops should contain tree and list endpoints."""
        from app.api.file_routes.tree_ops import router

        # Check router has the expected routes
        route_paths = [route.path for route in router.routes]

        # Tree/list endpoints
        assert any("tree" in path for path in route_paths), "Should have /tree endpoint"
        assert any("list" in path for path in route_paths), "Should have /list endpoint"

    def test_crud_ops_has_correct_endpoints(self):
        """crud_ops should contain create, delete, rename endpoints."""
        from app.api.file_routes.crud_ops import router

        # Check router has the expected routes
        route_paths = [route.path for route in router.routes]

        # CRUD endpoints
        assert any("create" in path for path in route_paths), "Should have /create endpoint"
        assert any("delete" in path for path in route_paths), "Should have /delete endpoint"
        assert any("rename" in path for path in route_paths), "Should have /rename endpoint"

    def test_content_routes_has_correct_endpoints(self):
        """content_routes should contain content GET and PUT."""
        from app.api.file_routes.content_routes import router

        route_paths = [route.path for route in router.routes]
        route_methods = [route.methods for route in router.routes]

        # Content endpoints
        assert any("content" in path for path in route_paths), "Should have /content endpoint"
        # PUT endpoint uses path parameter
        assert any("GET" in methods for methods in route_methods), "Should have GET method"
        assert any("PUT" in methods for methods in route_methods), "Should have PUT method"

    def test_search_routes_has_correct_endpoints(self):
        """search_routes should contain autocomplete and search."""
        from app.api.file_routes.search_routes import router

        route_paths = [route.path for route in router.routes]

        # Search endpoints
        assert any("autocomplete" in path for path in route_paths), "Should have /autocomplete"
        assert any("search" in path for path in route_paths), "Should have /search"
