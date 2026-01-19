# -*- coding: utf-8 -*-
"""JWT Auth Migration Tests (Sprint Tech Debt 1 - Task 3).

TDD: Verify that previously unprotected endpoints now require JWT.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Test client without auth headers."""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def authed_client():
    """Test client with JWT auth dependency mocked."""
    from datetime import datetime
    from app.main import app
    from app.api.auth_routes import get_current_user_from_token
    from app.models.auth_schemas import UserResponse

    # Mock JWT auth to return a valid user
    mock_user = UserResponse(
        id=1,
        email="test@example.com",
        username="testuser",
        is_active=True,
        created_at=datetime(2025, 1, 1, 0, 0, 0),
    )
    app.dependency_overrides[get_current_user_from_token] = lambda: mock_user

    yield TestClient(app, headers={"Authorization": "Bearer mock-jwt-token"})

    # Clean up
    app.dependency_overrides.clear()


class TestJWTAuthRequired:
    """Test that all migrated endpoints require authentication."""

    def test_files_tree_requires_auth(self, client):
        """GET /api/files/{team_id}/tree returns 401 without auth."""
        response = client.get("/api/files/test-team/tree")
        assert response.status_code == 401

    def test_files_content_requires_auth(self, client):
        """GET /api/files/{team_id}/content returns 401 without auth."""
        response = client.get("/api/files/test-team/content?path=test.txt")
        assert response.status_code == 401

    def test_files_autocomplete_requires_auth(self, client):
        """GET /api/files/autocomplete returns 401 without auth."""
        response = client.get("/api/files/autocomplete?team=test-team&path=")
        assert response.status_code == 401

    def test_teams_requires_auth(self, client):
        """GET /api/teams returns 401 without auth."""
        response = client.get("/api/teams")
        assert response.status_code == 401

    def test_send_requires_auth(self, client):
        """POST /api/send/{team_id}/{role_id} returns 401 without auth."""
        response = client.post("/api/send/test-team/pane-0", json={"message": "test"})
        assert response.status_code == 401

    def test_state_requires_auth(self, client):
        """GET /api/state/{team_id}/{role_id} returns 401 without auth."""
        response = client.get("/api/state/test-team/pane-0")
        assert response.status_code == 401


class TestFileRoutesWithAuth:
    """Test file routes work with SESSION_TOKEN (middleware-level auth)."""

    def test_files_tree_works_with_token(self, authed_client):
        """GET /api/files/{team_id}/tree works with SESSION_TOKEN."""
        response = authed_client.get("/api/files/test-team/tree")
        # 404 (team not found) or 200 (success) - both OK
        assert response.status_code in [200, 404]

    def test_files_content_works_with_token(self, authed_client):
        """GET /api/files/{team_id}/content works with SESSION_TOKEN."""
        response = authed_client.get("/api/files/test-team/content?path=test.txt")
        assert response.status_code in [200, 404]
