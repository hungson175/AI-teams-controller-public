# AI Teams Controller

Web application for managing tmux-based AI agent teams with voice command integration.

## What It Does

| Feature | Description |
|---------|-------------|
| **Team Management** | List, monitor, and control multiple AI agent teams in tmux sessions |
| **Voice Commands** | Speak commands via Soniox STT, auto-corrected by LLM |
| **Real-time Monitoring** | WebSocket streaming of terminal output with activity indicators |
| **File Browser** | Browse and view project files with syntax highlighting |
| **Team Creator** | Visual drag-drop editor for designing team configurations |

## Quick Start

```bash
# Backend (port 17061)
cd backend && uv sync && uv run uvicorn app.main:app --port 17061

# Frontend (port 3334)
cd frontend && pnpm install && PORT=3334 pnpm dev

# Background workers (voice feedback)
redis-server
cd backend && uv run celery -A celery_config worker --loglevel=info
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS v4 |
| Backend | FastAPI, Python 3.11+, Pydantic, SQLAlchemy 2.0 |
| Database | PostgreSQL (async) |
| Voice STT | Soniox API (WebSocket streaming) |
| Voice TTS | Google Cloud TTS (default) or OpenAI TTS |
| Background | Celery + Redis |
| Integration | tmux (real subprocess commands) |

## Ports

| Service | Port |
|---------|------|
| Frontend | 3334 |
| Backend | 17061 |
| Terminal Service | 17071 |

## Documentation

| Document | Purpose |
|----------|---------|
| [Architecture Overview](./ARCHITECTURE.md) | System design, data flow, key patterns |
| [Backend Guide](./backend/README.md) | API endpoints, services, models |
| [Frontend Guide](./frontend/README.md) | Components, hooks, contexts |

## Project Structure

```
AI-teams-controller/
├── frontend/          # Next.js application
├── backend/           # FastAPI server
├── data/templates/    # Team configuration templates
└── docs/              # Documentation
```

For detailed structure, see [Architecture Overview](./ARCHITECTURE.md).
