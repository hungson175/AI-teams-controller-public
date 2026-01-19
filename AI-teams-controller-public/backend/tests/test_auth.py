# -*- coding: utf-8 -*-
"""Tests for auth routes and middleware.

Sprint 25: Database-backed JWT auth tests
Tests both new JWT auth and legacy simple auth endpoints.
"""

from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.auth_routes import SESSION_TOKEN


@pytest.fixture
def client():
    """Test client without auth headers."""
    return TestClient(app)


# ============================================================
# JWT-based Auth Endpoints Tests (New in Sprint 25)
# ============================================================


class TestRegisterEndpoint:
    """Test POST /api/auth/register endpoint."""

    def test_register_success(self, client):
        """Should create user and return tokens."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "new@example.com"
        mock_user.username = "newuser"
        mock_user.is_active = True
        mock_user.created_at = "2025-01-01T00:00:00"

        with patch("app.api.auth_routes.get_auth_service") as mock_get_service, \
             patch("app.api.auth_routes.get_db"):
            mock_service = AsyncMock()
            mock_service.register_user = AsyncMock(
                return_value=(mock_user, "access-token", "refresh-token")
            )
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/auth/register",
                json={
                    "email": "new@example.com",
                    "username": "newuser",
                    "password": "password123"
                }
            )

            assert response.status_code == 201
            data = response.json()
            assert data["user"]["email"] == "new@example.com"
            assert data["user"]["username"] == "newuser"
            assert data["tokens"]["access_token"] == "access-token"
            assert data["tokens"]["refresh_token"] == "refresh-token"
            assert data["tokens"]["token_type"] == "bearer"

    def test_register_duplicate_email(self, client):
        """Should return 400 for duplicate email."""
        with patch("app.api.auth_routes.get_auth_service") as mock_get_service, \
             patch("app.api.auth_routes.get_db"):
            mock_service = AsyncMock()
            mock_service.register_user = AsyncMock(
                side_effect=ValueError("Email already registered")
            )
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/auth/register",
                json={
                    "email": "existing@example.com",
                    "username": "newuser",
                    "password": "password123"
                }
            )

            assert response.status_code == 400
            assert "Email already registered" in response.json()["detail"]

    def test_register_duplicate_username(self, client):
        """Should return 400 for duplicate username."""
        with patch("app.api.auth_routes.get_auth_service") as mock_get_service, \
             patch("app.api.auth_routes.get_db"):
            mock_service = AsyncMock()
            mock_service.register_user = AsyncMock(
                side_effect=ValueError("Username already taken")
            )
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/auth/register",
                json={
                    "email": "new@example.com",
                    "username": "existinguser",
                    "password": "password123"
                }
            )

            assert response.status_code == 400
            assert "Username already taken" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        """Should return 422 for invalid email format."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "username": "newuser",
                "password": "password123"
            }
        )

        assert response.status_code == 422

    def test_register_password_too_short(self, client):
        """Should return 422 for password less than 8 chars."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "short"
            }
        )

        assert response.status_code == 422

    def test_register_username_too_short(self, client):
        """Should return 422 for username less than 3 chars."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "username": "ab",
                "password": "password123"
            }
        )

        assert response.status_code == 422


class TestJWTLoginEndpoint:
    """Test POST /api/auth/login endpoint (JWT-based)."""

    def test_login_success(self, client):
        """Should return user and tokens on valid credentials."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.is_active = True
        mock_user.created_at = "2025-01-01T00:00:00"

        with patch("app.api.auth_routes.get_auth_service") as mock_get_service, \
             patch("app.api.auth_routes.get_db"):
            mock_service = AsyncMock()
            mock_service.authenticate_user = AsyncMock(
                return_value=(mock_user, "access-token", "refresh-token")
            )
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/auth/login",
                json={"email": "test@example.com", "password": "password123"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["user"]["email"] == "test@example.com"
            assert data["tokens"]["access_token"] == "access-token"
            assert data["tokens"]["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Should return 401 for invalid credentials."""
        with patch("app.api.auth_routes.get_auth_service") as mock_get_service, \
             patch("app.api.auth_routes.get_db"):
            mock_service = AsyncMock()
            mock_service.authenticate_user = AsyncMock(return_value=None)
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/auth/login",
                json={"email": "test@example.com", "password": "wrong"}
            )

            assert response.status_code == 401
            assert "Invalid" in response.json()["detail"]

    def test_login_missing_fields(self, client):
        """Should return 422 for missing fields."""
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com"}  # Missing password
        )

        assert response.status_code == 422


class TestRefreshEndpoint:
    """Test POST /api/auth/refresh endpoint."""

    def test_refresh_success(self, client):
        """Should return new tokens for valid refresh token."""
        with patch("app.api.auth_routes.get_auth_service") as mock_get_service, \
             patch("app.api.auth_routes.get_db"):
            mock_service = AsyncMock()
            mock_service.refresh_tokens = AsyncMock(
                return_value=("new-access-token", "new-refresh-token")
            )
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/auth/refresh",
                json={"refresh_token": "valid-refresh-token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["tokens"]["access_token"] == "new-access-token"
            assert data["tokens"]["refresh_token"] == "new-refresh-token"

    def test_refresh_invalid_token(self, client):
        """Should return 401 for invalid refresh token."""
        with patch("app.api.auth_routes.get_auth_service") as mock_get_service, \
             patch("app.api.auth_routes.get_db"):
            mock_service = AsyncMock()
            mock_service.refresh_tokens = AsyncMock(return_value=None)
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/auth/refresh",
                json={"refresh_token": "invalid-token"}
            )

            assert response.status_code == 401


class TestLogoutEndpoint:
    """Test POST /api/auth/logout endpoint."""

    def test_logout_success(self, client):
        """Should return success message."""
        response = client.post("/api/auth/logout")

        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"


class TestMeEndpoint:
    """Test GET /api/auth/me endpoint."""

    def test_me_success(self, client):
        """Should return current user for valid token."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.is_active = True
        mock_user.created_at = "2025-01-01T00:00:00"

        with patch("app.api.auth_routes.get_auth_service") as mock_get_service, \
             patch("app.api.auth_routes.get_db"):
            mock_service = AsyncMock()
            mock_service.get_current_user = AsyncMock(return_value=mock_user)
            mock_get_service.return_value = mock_service

            response = client.get(
                "/api/auth/me",
                headers={"Authorization": "Bearer valid-access-token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["user"]["email"] == "test@example.com"
            assert data["user"]["username"] == "testuser"

    def test_me_missing_token(self, client):
        """Should return 401 for missing token."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401
        assert "Missing" in response.json()["detail"]

    def test_me_invalid_token(self, client):
        """Should return 401 for invalid token."""
        with patch("app.api.auth_routes.get_auth_service") as mock_get_service, \
             patch("app.api.auth_routes.get_db"):
            mock_service = AsyncMock()
            mock_service.get_current_user = AsyncMock(return_value=None)
            mock_get_service.return_value = mock_service

            response = client.get(
                "/api/auth/me",
                headers={"Authorization": "Bearer invalid-token"}
            )

            assert response.status_code == 401
            assert "Invalid" in response.json()["detail"]


# ============================================================
# Legacy Simple Auth Tests (backwards compatibility)
# ============================================================


class TestLegacySimpleLogin:
    """Test POST /api/auth/login/simple endpoint (legacy)."""

    def test_simple_login_success(self, client):
        """Should return token on valid credentials."""
        with patch.dict("os.environ", {
            "AUTH_EMAIL": "test@example.com",
            "AUTH_PASSWORD": "secret123",
        }):
            response = client.post(
                "/api/auth/login/simple",
                json={"email": "test@example.com", "password": "secret123"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["token"] == SESSION_TOKEN

    def test_simple_login_invalid_email(self, client):
        """Should return 401 for invalid email."""
        with patch.dict("os.environ", {
            "AUTH_EMAIL": "test@example.com",
            "AUTH_PASSWORD": "secret123",
        }):
            response = client.post(
                "/api/auth/login/simple",
                json={"email": "wrong@example.com", "password": "secret123"}
            )

            assert response.status_code == 401

    def test_simple_login_invalid_password(self, client):
        """Should return 401 for invalid password."""
        with patch.dict("os.environ", {
            "AUTH_EMAIL": "test@example.com",
            "AUTH_PASSWORD": "secret123",
        }):
            response = client.post(
                "/api/auth/login/simple",
                json={"email": "test@example.com", "password": "wrong"}
            )

            assert response.status_code == 401

    def test_simple_login_missing_env_vars(self, client):
        """Should return 500 when env vars not configured."""
        with patch.dict("os.environ", {"AUTH_EMAIL": "", "AUTH_PASSWORD": ""}, clear=False):
            response = client.post(
                "/api/auth/login/simple",
                json={"email": "test@example.com", "password": "test"}
            )

            assert response.status_code == 500


# ============================================================
# Auth Middleware Tests
# ============================================================


class TestAuthMiddleware:
    """Test AuthMiddleware protection."""

    def test_health_endpoint_no_auth(self, client):
        """Health endpoint should not require auth."""
        response = client.get("/health")

        assert response.status_code == 200

    def test_api_endpoint_requires_auth(self, client):
        """API endpoints should require auth."""
        response = client.get("/api/teams")

        assert response.status_code == 401

    def test_api_endpoint_with_valid_jwt_token(self, client):
        """API endpoints should allow valid JWT token."""
        from datetime import datetime
        from app.api.auth_routes import get_current_user_from_token
        from app.models.auth_schemas import UserResponse
        from app.services.factory import get_team_service
        from unittest.mock import MagicMock

        mock_user = UserResponse(
            id=1,
            email="test@example.com",
            username="testuser",
            is_active=True,
            created_at=datetime(2025, 1, 1),
        )
        mock_service = MagicMock()
        mock_service.get_teams.return_value = []

        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_team_service] = lambda: mock_service
        try:
            response = client.get(
                "/api/teams",
                headers={"Authorization": "Bearer valid-jwt-token"}
            )
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_api_endpoint_with_invalid_token(self, client):
        """API endpoints should reject invalid token."""
        response = client.get(
            "/api/teams",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401

    def test_api_endpoint_invalid_auth_format(self, client):
        """Should reject invalid Authorization header format."""
        response = client.get(
            "/api/teams",
            headers={"Authorization": "InvalidFormat"}
        )

        assert response.status_code == 401

    def test_auth_register_no_auth_required(self, client):
        """Register endpoint should not require auth."""
        with patch("app.api.auth_routes.get_auth_service") as mock_get_service, \
             patch("app.api.auth_routes.get_db"):
            mock_service = AsyncMock()
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.email = "new@example.com"
            mock_user.username = "newuser"
            mock_user.is_active = True
            mock_user.created_at = "2025-01-01T00:00:00"
            mock_service.register_user = AsyncMock(
                return_value=(mock_user, "at", "rt")
            )
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/auth/register",
                json={
                    "email": "new@example.com",
                    "username": "newuser",
                    "password": "password123"
                }
            )

            # Should not return 401
            assert response.status_code == 201

    def test_auth_login_no_auth_required(self, client):
        """Login endpoint should not require auth."""
        with patch("app.api.auth_routes.get_auth_service") as mock_get_service, \
             patch("app.api.auth_routes.get_db"):
            mock_service = AsyncMock()
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.email = "test@example.com"
            mock_user.username = "testuser"
            mock_user.is_active = True
            mock_user.created_at = "2025-01-01T00:00:00"
            mock_service.authenticate_user = AsyncMock(
                return_value=(mock_user, "at", "rt")
            )
            mock_get_service.return_value = mock_service

            response = client.post(
                "/api/auth/login",
                json={"email": "test@example.com", "password": "password123"}
            )

            # Should not return 401
            assert response.status_code == 200

    def test_voice_task_done_no_auth(self, client):
        """Voice task-done endpoint should not require auth (internal webhook)."""
        with patch("app.api.voice_routes.get_tmux_pane_content", return_value=""):
            with patch("app.api.voice_routes.get_task_done_listener") as mock_listener:
                mock_listener.return_value.stop_hook_fired = AsyncMock(
                    return_value={"success": True}
                )

                response = client.post(
                    "/api/voice/task-done/team1/pane-0",
                    json={
                        "session_id": "s1",
                        "transcript_path": "/tmp/t",
                        "team_id": "team1",
                        "role_id": "pane-0",
                    }
                )

                # Should not return 401
                assert response.status_code == 200

    def test_options_request_no_auth(self, client):
        """OPTIONS requests should bypass auth (CORS preflight)."""
        response = client.options("/api/teams")

        # Should not return 401
        assert response.status_code != 401
