"""FastAPI application for TMUX Team Controller."""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import router
from app.api.voice_routes import router as voice_router
from app.api.auth_routes import router as auth_router, SESSION_TOKEN
from app.api.settings_routes import router as settings_router
from app.api.health_routes import router as health_router
from app.api.template_routes import router as template_router
from app.api.file_routes import router as file_router
from app.api.system_routes import router as system_router
from app.services.task_done_listener import get_task_done_listener
from app.services.tmux_service import tmux_service

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)


def validate_env_vars():
    """Validate required environment variables at startup.

    Fails fast if critical env vars are missing.
    """
    required_vars = {
        "OPENAI_API_KEY": "Required for voice token generation (GPT Realtime API)",
        "XAI_API_KEY": "Required for voice command correction (grok-4-fast)",
    }

    missing = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing.append(f"  - {var}: {description}")

    if missing:
        msg = (
            "\n" + "=" * 60 + "\n"
            "CRITICAL: Required environment variables not set!\n"
            + "=" * 60 + "\n"
            + "\n".join(missing) + "\n\n"
            "Fix: Create backend/.env file with these variables:\n"
            "  OPENAI_API_KEY=sk-...\n"
            "  XAI_API_KEY=xai-...\n"
            + "=" * 60
        )
        logger.critical(msg)
        print(msg, file=sys.stderr)
        # Don't exit - allow graceful degradation for development
        # Production should use --check-env flag


# Validate env vars at import time
validate_env_vars()


class AuthMiddleware(BaseHTTPMiddleware):
    """Simple auth middleware to protect /api/* endpoints.

    Allows:
    - /health (health check)
    - /api/auth/login (login endpoint)
    - All non-/api/* paths
    - All WebSocket connections (scope type = "websocket")

    Requires Authorization header with valid session token for all other /api/* paths.
    """

    UNPROTECTED_PATHS = {"/health", "/ws"}

    # Path prefixes that don't require auth (internal/webhook/websocket endpoints)
    # Note: Routes with JWT auth via get_current_user_from_token should be here
    # so middleware doesn't double-check with legacy SESSION_TOKEN
    UNPROTECTED_PREFIXES = (
        "/ws",                    # All WebSocket endpoints
        "/api/auth/",             # All auth endpoints (login, register, refresh, logout)
        "/api/settings",          # Settings endpoints (JWT auth via route dependency)
        "/api/voice/",            # All voice endpoints (token, command, task-done, ws)
        "/api/templates",         # Template endpoints (JWT auth via route dependency)
        "/api/system",            # System endpoints (JWT auth via route dependency)
        "/api/teams",             # Team routes (JWT auth via route dependency)
        "/api/send",              # Send message routes (JWT auth via route dependency)
        "/api/state",             # Pane state routes (JWT auth via route dependency)
        "/api/files",             # File routes (JWT auth via route dependency)
    )

    async def dispatch(self, request: Request, call_next):
        # CRITICAL: Skip WebSocket connections entirely
        # BaseHTTPMiddleware doesn't handle WebSocket upgrades properly
        # WebSocket connections don't send Authorization headers anyway
        if request.scope.get("type") == "websocket":
            return await call_next(request)

        # Skip OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path

        # Allow unprotected paths and prefixes
        if path in self.UNPROTECTED_PATHS or not path.startswith("/api/"):
            return await call_next(request)

        # Check unprotected prefixes
        for prefix in self.UNPROTECTED_PREFIXES:
            if path.startswith(prefix):
                return await call_next(request)

        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing Authorization header"},
            )

        # Expect "Bearer <token>" format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid Authorization header format. Use: Bearer <token>"},
            )

        token = parts[1]
        if token != SESSION_TOKEN:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid session token"},
            )

        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - startup and shutdown tasks."""
    # Startup: Start Redis pub/sub listener for Celery voice feedback
    listener = get_task_done_listener()
    try:
        await listener.start_pubsub_listener()
        logger.info("[STARTUP] Redis pub/sub listener started")
    except Exception as e:
        logger.warning(f"[STARTUP] Redis pub/sub failed (Redis may not be running): {e}")

    # Startup: Start background polling for activity detection (Sprint 29)
    try:
        tmux_service.start_background_polling()
        logger.info("[STARTUP] Activity polling started (5s interval)")
    except Exception as e:
        logger.warning(f"[STARTUP] Activity polling failed: {e}")

    yield

    # Shutdown: Stop background polling
    tmux_service.stop_background_polling()
    logger.info("[SHUTDOWN] Activity polling stopped")

    # Shutdown: Stop Redis pub/sub listener
    await listener.stop_pubsub_listener()
    logger.info("[SHUTDOWN] Redis pub/sub listener stopped")


app = FastAPI(
    title="TMUX Team Controller API",
    description="Backend API for controlling tmux-based AI agent teams",
    version="0.1.0",
    lifespan=lifespan,
)

# Auth middleware - protect /api/* endpoints (except /api/auth/login and /health)
app.add_middleware(AuthMiddleware)

# CORS configuration - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Cloudflare tunnel access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Include voice routes (prefix already in router: /api/voice/...)
app.include_router(voice_router)

# Include auth routes (prefix already in router: /api/auth/...)
app.include_router(auth_router)

# Include settings routes (prefix already in router: /api/settings/...)
app.include_router(settings_router)

# Include health routes (prefix: /health)
app.include_router(health_router)

# Include template routes (prefix: /api/templates)
app.include_router(template_router, prefix="/api")

# Include file browser routes (prefix already in router: /api/files)
app.include_router(file_router)

# Include system routes (prefix already in router: /api/system)
app.include_router(system_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=17061)
