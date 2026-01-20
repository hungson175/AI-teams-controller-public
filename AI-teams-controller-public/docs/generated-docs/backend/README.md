# Backend - FastAPI Application

**Port**: 17061 | **Framework**: FastAPI + Pydantic + SQLAlchemy 2.0

## Quick Start

```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 17061 --reload

# Background workers (for voice feedback)
redis-server
uv run celery -A celery_config worker --loglevel=info
```

## Directory Structure

```
backend/app/
├── main.py              # Application entry, CORS, lifespan
├── database.py          # Async SQLAlchemy + SQLite
├── api/                 # Route handlers
├── services/            # Business logic
└── models/              # Pydantic schemas + SQLAlchemy
```

## API Endpoints

| Category | Description | Details |
|----------|-------------|---------|
| **Team Management** | List sessions, send messages, get output | [teams.md](./api/teams.md) |
| **File Browser** | Directory tree, file content | [files.md](./api/files.md) |
| **Voice Commands** | STT tokens, command processing | [voice.md](./api/voice.md) |
| **Authentication** | JWT login, register, refresh | [auth.md](./api/auth.md) |
| **Health Checks** | System status, Redis, Celery | [health.md](./api/health.md) |

## Services

| Service | Purpose | Details |
|---------|---------|---------|
| **TmuxService** | Real tmux subprocess commands | [tmux-service.md](./services/tmux-service.md) |
| **TTSProviders** | Switchable TTS (Google/HD-TTS) | [tts-providers.md](./services/tts-providers.md) |
| **VoiceFeedback** | Stop hook → LLM → TTS pipeline | [voice-feedback.md](./services/voice-feedback.md) |
| **AuthService** | JWT + bcrypt authentication | [auth-service.md](./services/auth-service.md) |

## Database

Async SQLAlchemy 2.0 with SQLite:

```python
DATABASE_URL = "sqlite+aiosqlite://user:pass@localhost:5432/ai_teams"
```

**Models:**
- `User` - Authentication (email, username, hashed_password)
- `UserSettings` - Voice/theme preferences (one-to-one with User)

## Testing

```bash
# Unit tests (mocked, fast)
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=app --cov-report=term-missing
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | SQLite connection |
| `JWT_SECRET_KEY` | Yes | Token signing secret |
| `SONIOX_API_KEY` | Yes | Speech-to-text |
| `XAI_API_KEY` | Yes | LLM correction |
| `TTS_PROVIDER` | No | `google` (default) or `hdtts` |
| `REDIS_URL` | No | Celery broker (default: `redis://localhost:6379`) |

## Further Reading

- [Architecture Overview](../ARCHITECTURE.md) - System design
- [Frontend Guide](../frontend/README.md) - UI components
