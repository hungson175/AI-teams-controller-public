# -*- coding: utf-8 -*-
"""Tests for settings routes.

Sprint 25: TDD - Settings API tests
Tests GET/PUT /api/settings endpoints with mocked database.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.auth_routes import get_current_user_from_token
from app.api.settings_routes import get_user_settings, update_user_settings
from app.database import get_db
from app.main import app
from app.models.auth_schemas import UserResponse


# === Fixtures ===


@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    return UserResponse(
        id=1,
        email="test@example.com",
        username="testuser",
        is_active=True,
        created_at=datetime(2025, 1, 1, 0, 0, 0),
    )


@pytest.fixture
def mock_settings():
    """Create a mock settings object."""
    settings = MagicMock()
    settings.detection_mode = "silence"
    settings.stop_word = "go go go"
    settings.noise_filter_level = "medium"
    settings.silence_duration_ms = 5000
    settings.theme = "dark"
    settings.updated_at = datetime(2025, 1, 1, 0, 0, 0)
    return settings


@pytest.fixture
def authenticated_client(mock_user):
    """Test client with mocked authentication."""
    app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: MagicMock()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Test client without auth (for unauthorized tests)."""
    # Clear any leftover overrides
    app.dependency_overrides.clear()
    return TestClient(app)


# ============================================================
# GET /api/settings Tests
# ============================================================


class TestGetSettings:
    """Test GET /api/settings endpoint."""

    def test_get_settings_success(self, mock_user, mock_settings):
        """Should return user settings for authenticated user."""
        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()

        with patch("app.api.settings_routes.get_user_settings") as mock_get:
            mock_get.return_value = mock_settings
            client = TestClient(app)

            response = client.get(
                "/api/settings",
                headers={"Authorization": "Bearer valid-token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["detection_mode"] == "silence"
            assert data["stop_word"] == "go go go"
            assert data["noise_filter_level"] == "medium"
            assert data["silence_duration_ms"] == 5000
            assert data["theme"] == "dark"

        app.dependency_overrides.clear()

    def test_get_settings_creates_default_if_none(self, mock_user):
        """Should create default settings if user has none."""
        default_settings = MagicMock()
        default_settings.detection_mode = "silence"
        default_settings.stop_word = "go go go"
        default_settings.noise_filter_level = "medium"
        default_settings.silence_duration_ms = 5000
        default_settings.theme = "system"
        default_settings.updated_at = datetime(2025, 1, 1, 0, 0, 0)

        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()

        with patch("app.api.settings_routes.get_user_settings") as mock_get, \
             patch("app.api.settings_routes.create_default_settings") as mock_create:
            mock_get.return_value = None
            mock_create.return_value = default_settings
            client = TestClient(app)

            response = client.get(
                "/api/settings",
                headers={"Authorization": "Bearer valid-token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["theme"] == "system"

        app.dependency_overrides.clear()

    def test_get_settings_unauthorized(self, client):
        """Should return 401 for missing auth token."""
        response = client.get("/api/settings")
        assert response.status_code == 401

    def test_get_settings_invalid_token(self, client):
        """Should return 401 for invalid auth token."""
        from fastapi import HTTPException

        def raise_401():
            raise HTTPException(status_code=401, detail="Invalid token")

        app.dependency_overrides[get_current_user_from_token] = raise_401
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get(
            "/api/settings",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401
        app.dependency_overrides.clear()


# ============================================================
# PUT /api/settings Tests
# ============================================================


class TestUpdateSettings:
    """Test PUT /api/settings endpoint."""

    def test_update_settings_success(self, mock_user):
        """Should update and return user settings."""
        updated_settings = MagicMock()
        updated_settings.detection_mode = "stopword"
        updated_settings.stop_word = "send it"
        updated_settings.noise_filter_level = "high"
        updated_settings.silence_duration_ms = 3000
        updated_settings.theme = "light"
        updated_settings.updated_at = datetime(2025, 1, 1, 0, 0, 0)

        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()

        with patch("app.api.settings_routes.update_user_settings") as mock_update:
            mock_update.return_value = updated_settings
            client = TestClient(app)

            response = client.put(
                "/api/settings",
                headers={"Authorization": "Bearer valid-token"},
                json={
                    "detection_mode": "stopword",
                    "stop_word": "send it",
                    "noise_filter_level": "high",
                    "silence_duration_ms": 3000,
                    "theme": "light"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["detection_mode"] == "stopword"
            assert data["stop_word"] == "send it"
            assert data["noise_filter_level"] == "high"
            assert data["silence_duration_ms"] == 3000
            assert data["theme"] == "light"

        app.dependency_overrides.clear()

    def test_update_settings_partial(self, mock_user):
        """Should support partial updates."""
        partial_settings = MagicMock()
        partial_settings.detection_mode = "silence"
        partial_settings.stop_word = "go go go"
        partial_settings.noise_filter_level = "medium"
        partial_settings.silence_duration_ms = 5000
        partial_settings.theme = "dark"
        partial_settings.updated_at = datetime(2025, 1, 1, 0, 0, 0)

        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()

        with patch("app.api.settings_routes.update_user_settings") as mock_update:
            mock_update.return_value = partial_settings
            client = TestClient(app)

            response = client.put(
                "/api/settings",
                headers={"Authorization": "Bearer valid-token"},
                json={"theme": "dark"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["theme"] == "dark"

        app.dependency_overrides.clear()

    def test_update_settings_unauthorized(self, client):
        """Should return 401 for missing auth token."""
        response = client.put(
            "/api/settings",
            json={"theme": "dark"}
        )
        assert response.status_code == 401

    def test_update_settings_invalid_detection_mode(self, mock_user):
        """Should return 422 for invalid detection_mode value."""
        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()
        client = TestClient(app)

        response = client.put(
            "/api/settings",
            headers={"Authorization": "Bearer valid-token"},
            json={"detection_mode": "invalid_mode"}
        )

        assert response.status_code == 422
        app.dependency_overrides.clear()

    def test_update_settings_invalid_noise_filter(self, mock_user):
        """Should return 422 for invalid noise_filter_level value."""
        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()
        client = TestClient(app)

        response = client.put(
            "/api/settings",
            headers={"Authorization": "Bearer valid-token"},
            json={"noise_filter_level": "extreme"}
        )

        assert response.status_code == 422
        app.dependency_overrides.clear()

    def test_update_settings_invalid_theme(self, mock_user):
        """Should return 422 for invalid theme value."""
        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()
        client = TestClient(app)

        response = client.put(
            "/api/settings",
            headers={"Authorization": "Bearer valid-token"},
            json={"theme": "neon"}
        )

        assert response.status_code == 422
        app.dependency_overrides.clear()

    def test_update_settings_invalid_silence_duration(self, mock_user):
        """Should return 422 for negative silence_duration_ms."""
        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()
        client = TestClient(app)

        response = client.put(
            "/api/settings",
            headers={"Authorization": "Bearer valid-token"},
            json={"silence_duration_ms": -1000}
        )

        assert response.status_code == 422
        app.dependency_overrides.clear()


# ============================================================
# Settings Schema Validation Tests
# ============================================================


class TestSettingsSchemas:
    """Test settings request/response schemas."""

    def test_valid_detection_modes(self, mock_user):
        """Should accept valid detection mode values."""
        settings = MagicMock()
        settings.detection_mode = "stopword"
        settings.stop_word = "go go go"
        settings.noise_filter_level = "medium"
        settings.silence_duration_ms = 5000
        settings.theme = "system"
        settings.updated_at = datetime(2025, 1, 1, 0, 0, 0)

        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()

        with patch("app.api.settings_routes.update_user_settings") as mock_update:
            mock_update.return_value = settings
            client = TestClient(app)

            for mode in ["silence", "stopword"]:
                settings.detection_mode = mode
                response = client.put(
                    "/api/settings",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"detection_mode": mode}
                )
                assert response.status_code == 200

        app.dependency_overrides.clear()

    def test_valid_noise_filter_levels(self, mock_user):
        """Should accept valid noise filter level values."""
        settings = MagicMock()
        settings.detection_mode = "silence"
        settings.stop_word = "go go go"
        settings.noise_filter_level = "medium"
        settings.silence_duration_ms = 5000
        settings.theme = "system"
        settings.updated_at = datetime(2025, 1, 1, 0, 0, 0)

        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()

        with patch("app.api.settings_routes.update_user_settings") as mock_update:
            mock_update.return_value = settings
            client = TestClient(app)

            for level in ["very-low", "low", "medium", "high", "very-high"]:
                settings.noise_filter_level = level
                response = client.put(
                    "/api/settings",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"noise_filter_level": level}
                )
                assert response.status_code == 200

        app.dependency_overrides.clear()

    def test_valid_themes(self, mock_user):
        """Should accept valid theme values."""
        settings = MagicMock()
        settings.detection_mode = "silence"
        settings.stop_word = "go go go"
        settings.noise_filter_level = "medium"
        settings.silence_duration_ms = 5000
        settings.theme = "system"
        settings.updated_at = datetime(2025, 1, 1, 0, 0, 0)

        app.dependency_overrides[get_current_user_from_token] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: MagicMock()

        with patch("app.api.settings_routes.update_user_settings") as mock_update:
            mock_update.return_value = settings
            client = TestClient(app)

            for theme in ["light", "dark", "system"]:
                settings.theme = theme
                response = client.put(
                    "/api/settings",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"theme": theme}
                )
                assert response.status_code == 200

        app.dependency_overrides.clear()


# ============================================================
# Settings Middleware Tests
# ============================================================


class TestSettingsMiddleware:
    """Test that settings endpoints are protected by auth middleware."""

    def test_settings_requires_auth(self, client):
        """GET /api/settings should require auth."""
        response = client.get("/api/settings")
        assert response.status_code == 401

    def test_settings_update_requires_auth(self, client):
        """PUT /api/settings should require auth."""
        response = client.put(
            "/api/settings",
            json={"theme": "dark"}
        )
        assert response.status_code == 401
