# -*- coding: utf-8 -*-
"""Tests for health check endpoints (Story 6: Observability).

TDD: Tests written first for health_routes.py
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestHealthOverall:
    """Tests for GET /health endpoint."""

    def test_health_returns_status(self, client):
        """Should return overall health status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    def test_health_returns_components(self, client):
        """Should return component status breakdown."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "components" in data
        assert "fastapi" in data["components"]
        assert "celery" in data["components"]
        assert "pubsub" in data["components"]
        assert "redis" in data["components"]

    def test_health_returns_version(self, client):
        """Should return current version (git commit hash)."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        # Version should be a string (git hash or fallback)
        assert isinstance(data["version"], str)

    def test_health_degraded_when_celery_down(self, client):
        """Should return degraded when Celery worker is not running."""
        with patch(
            "app.api.health_routes.check_celery_status",
            return_value={"status": "unhealthy", "error": "No workers"}
        ):
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["degraded", "unhealthy"]
            assert data["components"]["celery"] == "unhealthy"

    def test_health_degraded_when_redis_down(self, client):
        """Should return degraded when Redis is not available."""
        with patch(
            "app.api.health_routes.check_redis_status",
            return_value={"status": "unhealthy", "error": "Connection refused"}
        ):
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["degraded", "unhealthy"]
            assert data["components"]["redis"] == "unhealthy"


class TestHealthCelery:
    """Tests for GET /health/celery endpoint."""

    def test_celery_returns_status(self, client):
        """Should return Celery worker status."""
        response = client.get("/health/celery")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]

    def test_celery_returns_worker_count(self, client):
        """Should return number of active workers."""
        with patch(
            "app.api.health_routes.get_celery_stats",
            return_value={"worker_count": 2, "status": "healthy"}
        ):
            response = client.get("/health/celery")

            assert response.status_code == 200
            data = response.json()
            assert "worker_count" in data
            assert isinstance(data["worker_count"], int)

    def test_celery_returns_code_version(self, client):
        """Should return Celery worker's code version (git hash)."""
        with patch(
            "app.api.health_routes.get_celery_stats",
            return_value={"code_version": "abc1234", "status": "healthy", "worker_count": 1}
        ):
            response = client.get("/health/celery")

            assert response.status_code == 200
            data = response.json()
            assert "code_version" in data
            assert isinstance(data["code_version"], str)

    def test_celery_returns_tasks_processed(self, client):
        """Should return count of tasks processed."""
        with patch(
            "app.api.health_routes.get_celery_stats",
            return_value={
                "status": "healthy",
                "worker_count": 1,
                "tasks_processed": 150
            }
        ):
            response = client.get("/health/celery")

            assert response.status_code == 200
            data = response.json()
            assert "tasks_processed" in data
            assert isinstance(data["tasks_processed"], int)

    def test_celery_unhealthy_when_no_workers(self, client):
        """Should return unhealthy when no Celery workers are running."""
        with patch(
            "app.api.health_routes.get_celery_stats",
            return_value={"status": "unhealthy", "worker_count": 0, "error": "No workers found"}
        ):
            response = client.get("/health/celery")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["worker_count"] == 0


class TestHealthPubsub:
    """Tests for GET /health/pubsub endpoint."""

    def test_pubsub_returns_status(self, client):
        """Should return pub/sub listener status."""
        response = client.get("/health/pubsub")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]

    def test_pubsub_returns_listener_running(self, client):
        """Should indicate if listener task is running."""
        response = client.get("/health/pubsub")

        assert response.status_code == 200
        data = response.json()
        assert "listener_running" in data
        assert isinstance(data["listener_running"], bool)

    def test_pubsub_returns_connected_clients(self, client):
        """Should return count of connected WebSocket clients."""
        response = client.get("/health/pubsub")

        assert response.status_code == 200
        data = response.json()
        assert "connected_clients" in data
        assert isinstance(data["connected_clients"], int)

    def test_pubsub_unhealthy_when_listener_crashed(self, client):
        """Should return unhealthy when listener task has crashed."""
        # Mock the task_done_listener to have a crashed task
        mock_listener = MagicMock()
        mock_listener._pubsub_task = MagicMock()
        mock_listener._pubsub_task.done.return_value = True  # Task crashed
        mock_listener.ws_manager.get_client_count.return_value = 0

        with patch(
            "app.api.health_routes.get_task_done_listener",
            return_value=mock_listener
        ):
            response = client.get("/health/pubsub")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["listener_running"] is False


class TestHealthRedis:
    """Tests for GET /health/redis endpoint."""

    def test_redis_returns_status(self, client):
        """Should return Redis connection status."""
        response = client.get("/health/redis")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]

    def test_redis_returns_connected(self, client):
        """Should indicate Redis connection state."""
        response = client.get("/health/redis")

        assert response.status_code == 200
        data = response.json()
        assert "connected" in data
        assert isinstance(data["connected"], bool)

    def test_redis_unhealthy_on_connection_error(self, client):
        """Should return unhealthy when Redis is not available."""
        with patch(
            "app.api.health_routes.check_redis_connection",
            return_value={"status": "unhealthy", "connected": False, "error": "Connection refused"}
        ):
            response = client.get("/health/redis")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["connected"] is False
            assert "error" in data


class TestVersionTracking:
    """Tests for version tracking functionality."""

    def test_get_git_version_returns_hash(self):
        """Should return git commit hash."""
        from app.api.health_routes import get_git_version

        version = get_git_version()

        assert isinstance(version, str)
        assert len(version) > 0

    def test_get_git_version_fallback(self):
        """Should return fallback when git is not available."""
        from app.api.health_routes import get_git_version

        # Clear the lru_cache before testing fallback
        get_git_version.cache_clear()

        with patch("app.api.health_routes.subprocess.run", side_effect=Exception("git not found")):
            version = get_git_version()
            assert version == "unknown"

        # Restore cache for other tests
        get_git_version.cache_clear()


# Fixtures
@pytest.fixture
def client():
    """Create test client with mocked dependencies."""
    # Import here to avoid circular imports during test collection
    from app.main import app

    # Mock the dependencies that might not be available in test environment
    with patch("app.api.health_routes.check_celery_status", return_value={"status": "healthy"}):
        with patch("app.api.health_routes.check_redis_status", return_value={"status": "healthy"}):
            with patch("app.api.health_routes.get_celery_stats", return_value={
                "status": "healthy",
                "worker_count": 1,
                "code_version": "test123",
                "tasks_processed": 0
            }):
                with patch("app.api.health_routes.check_redis_connection", return_value={
                    "status": "healthy",
                    "connected": True
                }):
                    with TestClient(app) as test_client:
                        yield test_client
