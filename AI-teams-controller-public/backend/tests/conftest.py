# -*- coding: utf-8 -*-
"""Pytest configuration and shared fixtures for backend tests.

Test Hierarchy (CRITICAL):
1. Syntax Check - python -m py_compile
2. Mock Tests - All external APIs mocked (free)
3. Non-LLM Tests - Local logic only (free)
4. LLM Tests - REQUIRE BOSS APPROVAL (costly) - marked with @pytest.mark.llm

Run tests:
    pytest tests/ -m "not llm"     # All except LLM (safe, free)
    pytest tests/ -m "llm"          # LLM only (BOSS APPROVAL REQUIRED)
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


# ============================================================
# Pytest Configuration
# ============================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "llm: tests that call LLM APIs (require Boss approval)")
    config.addinivalue_line("markers", "slow: tests that take >1s to run")
    config.addinivalue_line("markers", "integration: integration tests")


# ============================================================
# Environment Fixtures
# ============================================================

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "OPENAI_API_KEY": "test-openai-key",
        "XAI_API_KEY": "test-xai-key",
        "SONIOX_API_KEY": "test-soniox-key",
        "REDIS_URL": "redis://localhost:6379/0",
        "AUTH_EMAIL": "test@example.com",
        "AUTH_PASSWORD": "testpassword",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def clean_env():
    """Clean environment (no API keys set)."""
    env_vars = {
        "OPENAI_API_KEY": "",
        "XAI_API_KEY": "",
        "SONIOX_API_KEY": "",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield


# ============================================================
# Mock Factories
# ============================================================

@pytest.fixture
def mock_subprocess_success():
    """Mock subprocess.run that always succeeds."""
    mock = MagicMock()
    mock.return_value = MagicMock(
        returncode=0,
        stdout="mock output",
        stderr="",
    )
    return mock


@pytest.fixture
def mock_subprocess_failure():
    """Mock subprocess.run that always fails."""
    mock = MagicMock()
    mock.return_value = MagicMock(
        returncode=1,
        stdout="",
        stderr="mock error",
    )
    return mock


@pytest.fixture
def mock_tmux_sessions():
    """Mock tmux list-sessions output."""
    return "session1\nsession2\nsession3"


@pytest.fixture
def mock_tmux_panes():
    """Mock tmux list-panes output."""
    return "0|%17|PM\n1|%18|SA\n2|%19|BE"


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for pub/sub."""
    mock = MagicMock()
    mock.publish = MagicMock(return_value=1)
    mock.subscribe = MagicMock()
    mock.get_message = MagicMock(return_value=None)
    return mock


@pytest.fixture
def mock_aioredis_client():
    """Mock async Redis client."""
    mock = AsyncMock()
    mock.publish = AsyncMock(return_value=1)
    mock.pubsub = MagicMock(return_value=AsyncMock())
    return mock


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for TTS."""
    mock = MagicMock()
    mock.audio.speech.create = MagicMock(
        return_value=MagicMock(content=b"fake_audio_bytes")
    )
    return mock


@pytest.fixture
def mock_llm():
    """Mock LangChain LLM."""
    mock = MagicMock()
    mock.invoke = MagicMock(
        return_value=MagicMock(content="Done. Task completed successfully.")
    )
    mock.with_structured_output = MagicMock(return_value=mock)
    return mock


@pytest.fixture
def mock_celery_task():
    """Mock Celery task.delay()."""
    mock = MagicMock()
    mock.id = "test-task-id"
    return mock


# ============================================================
# Service Fixtures
# ============================================================

@pytest.fixture
def tmux_service():
    """Get fresh TmuxService instance for testing."""
    from app.services.tmux_service import TmuxService
    return TmuxService()


@pytest.fixture
def task_done_listener():
    """Get fresh TaskDoneListener instance for testing."""
    from app.services.task_done_listener import TaskDoneListener
    return TaskDoneListener()


@pytest.fixture
def mock_team_service():
    """Mock TeamService for route testing."""
    mock = MagicMock()
    mock.get_teams.return_value = [
        {"id": "team1", "name": "team1"},
        {"id": "team2", "name": "team2"},
    ]
    mock.get_roles.return_value = [
        {"id": "pane-0", "name": "PM", "order": 1},
        {"id": "pane-1", "name": "SA", "order": 2},
    ]
    mock.send_message.return_value = {
        "success": True,
        "message": "Message sent",
        "sentAt": "2024-01-01T00:00:00",
    }
    mock.get_pane_state.return_value = {
        "output": "mock pane output",
        "lastUpdated": "00:00:00",
        "highlightText": None,
    }
    return mock


# ============================================================
# FastAPI Test Client
# ============================================================

@pytest.fixture
def test_client():
    """FastAPI test client with mocked dependencies."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


@pytest.fixture
def test_client_with_auth():
    """FastAPI test client with auth header."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    # Add auth header to all requests
    client.headers["Authorization"] = "Bearer simple-session-token"
    return client
