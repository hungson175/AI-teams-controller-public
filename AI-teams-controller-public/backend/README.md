# AI Teams Controller - Backend

FastAPI backend for AI Teams Controller web application.

---

## Database

Uses SQLite for zero-configuration setup:

- **Database**: `aicontroller.db` (auto-created)
- **Demo credentials**: test@example.com / test123
- **Initialization**: One command
- **No external database required**

**Initialize demo database**:
```bash
python scripts/init_sqlite_demo.py
```

Creates aicontroller.db with:
- Demo user (test@example.com / test123)
- Default voice settings

---

## Default Settings

Demo initialization configures:

**Voice Detection**:
- Detection mode: `silence`
- Wake word: `go go go`
- Sensitivity: `medium`
- Silence duration: `5000ms`
- Theme: `system`

---

## Installation

**Prerequisites**: Python 3.11+, pip

**Install dependencies**:
```bash
pip install -r requirements.txt
```

**Initialize database** (SQLite demo):
```bash
python scripts/init_sqlite_demo.py
```

**Run backend**:
```bash
uvicorn app.main:app --reload
```

Backend runs on: http://localhost:8000

---

## API Documentation

**Swagger UI**: http://localhost:8000/docs
**ReDoc**: http://localhost:8000/redoc

---

## Environment Variables

**Optional**:
- `DATABASE_URL` - SQLite database path (default: sqlite+aiosqlite:///./aicontroller.db)
- `SECRET_KEY` - JWT secret (auto-generated for demo)
- `CORS_ORIGINS` - Allowed origins (default: http://localhost:3000)

---

## Troubleshooting

**"Database not found"**:
```bash
# Run initialization
python scripts/init_sqlite_demo.py
```

**"Login failed"**:
- Verify demo credentials: test@example.com / test123
- Check database initialized: `ls aicontroller.db`

**"Port 8000 in use"**:
```bash
# Use different port
uvicorn app.main:app --port 8001
```

---

**Database**: SQLite (zero configuration)
**Demo Credentials**: test@example.com / test123
