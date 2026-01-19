# Backend Tests

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures and pytest configuration
├── README.md                # This file
│
├── test_*.py                # Unit tests (root level)
│   ├── test_celery_tasks.py     # Celery task processing tests
│   ├── test_skip_logic.py       # Skip logic tests (fail-closed)
│   ├── test_task_done_listener.py # Pub/sub listener tests
│   ├── test_tmux_service.py     # Tmux service tests
│   └── test_voice_routes.py     # Voice API endpoint tests
│
└── integration/             # Integration tests (real services)
    ├── __init__.py
    └── test_voice_feedback.py   # Voice feedback E2E tests
```

## Test Categories

### Unit Tests (Default)

**Location:** `tests/test_*.py`

**Characteristics:**
- All external dependencies are mocked
- Fast execution (< 5 seconds total)
- No network calls, no Redis, no Celery worker
- Safe to run in CI/CD

**Run command:**
```bash
uv run pytest tests/ -m "not integration" -v
```

### Integration Tests

**Location:** `tests/integration/`

**Characteristics:**
- Require real external services (Redis, Celery, tmux)
- Slower execution
- Verify real service communication
- Manual verification after code changes

**Run command:**
```bash
uv run pytest tests/integration/ -m integration -v
```

**Prerequisites:**
- Redis server running: `redis-server`
- Celery worker (optional): `./scripts/restart-all.sh`
- tmux installed

## pytest Markers

Defined in `conftest.py`:

| Marker | Description |
|--------|-------------|
| `@pytest.mark.integration` | Integration tests (real services) |
| `@pytest.mark.llm` | Tests that call LLM APIs (costly, need approval) |
| `@pytest.mark.slow` | Tests that take > 1 second |

## Running Tests

### All Unit Tests (Safe, Free)
```bash
uv run pytest tests/ -m "not integration and not llm" -v
```

### Specific Test File
```bash
uv run pytest tests/test_skip_logic.py -v
```

### Specific Test Class
```bash
uv run pytest tests/test_skip_logic.py::TestShouldSkipRole -v
```

### Specific Test Function
```bash
uv run pytest tests/test_skip_logic.py::TestShouldSkipRole::test_fail_closed_empty_title -v
```

### With Coverage
```bash
uv run pytest tests/ --cov=app --cov-report=html
```

## Test Hierarchy

Following the project testing strategy:

1. **Syntax Check** - `python -m py_compile`
2. **Unit Tests** - All external deps mocked (free, fast)
3. **Integration Tests** - Real Celery, Redis (manual)
4. **LLM Tests** - Require approval (costly)

## Key Test Files

### test_skip_logic.py

Tests the fail-closed skip logic pattern:

```python
# CRITICAL: Validates fail-closed behavior
def test_fail_closed_empty_title(self):
    """When pane title unknown, SKIP (don't process)."""
    # Old buggy test asserted False (process = SPAM)
    # New correct test asserts True (skip = SAFE)
    assert should_skip_role("team", "unknown-pane") is True
```

### test_celery_tasks.py

Tests Celery task processing:
- Content trimming
- Duplicate detection
- TTS generation
- Redis pub/sub broadcast

### test_voice_routes.py

Tests FastAPI endpoints:
- Token generation
- Voice command processing
- Stop hook handling
- Skip logic integration

## Adding New Tests

1. **Unit tests**: Add to `tests/test_<module>.py`
2. **Integration tests**: Add to `tests/integration/test_<feature>.py`
3. **Mark appropriately**: Use `@pytest.mark.<marker>` decorators
4. **Mock external deps**: Use fixtures from `conftest.py`

## Fixtures (conftest.py)

| Fixture | Description |
|---------|-------------|
| `mock_env_vars` | Mock environment variables |
| `mock_redis_client` | Mock Redis client |
| `mock_llm` | Mock LangChain LLM |
| `mock_celery_task` | Mock Celery task |
| `task_done_listener` | Fresh TaskDoneListener instance |
| `test_client` | FastAPI TestClient |
