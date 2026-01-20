# AI Teams Controller - Backend

FastAPI backend for AI Teams Controller web application.

---

## Database

### SQLite Demo Mode (Default)

Demo mode uses SQLite for zero-configuration setup:

- **Database**: `demo.db` (auto-created)
- **Demo credentials**: test@example.com / test123
- **Initialization**: One command
- **Use case**: Quick demo, development, testing

**Initialize demo database**:
```bash
python scripts/init_sqlite_demo.py
```

Creates demo.db with:
- Demo user (test@example.com / test123)
- Sample teams and configurations
- Default voice settings

### Production Mode (PostgreSQL)

For production deployment with PostgreSQL:

**Configuration**:
```bash
# Set environment variable
export DATABASE_URL=postgresql://user:password@localhost/dbname
```

Backend automatically switches to PostgreSQL when `DATABASE_URL` is set.

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
- `DATABASE_URL` - PostgreSQL connection (default: SQLite demo.db)
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
- Check database initialized: `ls demo.db`

**"Port 8000 in use"**:
```bash
# Use different port
uvicorn app.main:app --port 8001
```

---

**Default Mode**: SQLite demo (no PostgreSQL required)
**Demo Credentials**: test@example.com / test123
