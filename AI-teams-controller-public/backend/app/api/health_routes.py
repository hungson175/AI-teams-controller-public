# -*- coding: utf-8 -*-
"""Health check endpoints for observability (Story 6).

Provides comprehensive health monitoring for all voice feedback components:
- FastAPI server
- Celery workers (background processing)
- Redis pub/sub listener
- Redis connection

Version tracking uses git commit hash for code version mismatch detection
between FastAPI and Celery workers.
"""

import logging
import os
import subprocess
from functools import lru_cache
from typing import Any, Dict

import redis
from fastapi import APIRouter

from app.services.task_done_listener import get_task_done_listener

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])

# Redis configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


@lru_cache(maxsize=1)
def get_git_version() -> str:
    """Get current git commit hash for version tracking.

    Returns short (7 char) commit hash or 'unknown' if git unavailable.
    Cached since version doesn't change during runtime.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=7", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "unknown"
    except Exception as e:
        logger.warning(f"Failed to get git version: {e}")
        return "unknown"


def check_redis_connection() -> Dict[str, Any]:
    """Check Redis connection status.

    Returns dict with status, connected flag, and optional error.
    """
    try:
        r = redis.from_url(REDIS_URL)
        r.ping()
        return {"status": "healthy", "connected": True}
    except redis.ConnectionError as e:
        return {"status": "unhealthy", "connected": False, "error": str(e)[:100]}
    except Exception as e:
        return {"status": "unhealthy", "connected": False, "error": str(e)[:100]}


def check_redis_status() -> Dict[str, Any]:
    """Check Redis status for overall health endpoint.

    Returns simplified status for component overview.
    """
    result = check_redis_connection()
    return {"status": result["status"], "error": result.get("error")}


def get_celery_stats() -> Dict[str, Any]:
    """Get Celery worker statistics.

    Uses Celery's inspect API to get worker info.
    Returns worker count, status, code version, and tasks processed.
    """
    try:
        from celery_config import celery_app

        # Get active workers via ping
        inspector = celery_app.control.inspect(timeout=2)
        ping_response = inspector.ping()

        if not ping_response:
            return {
                "status": "unhealthy",
                "worker_count": 0,
                "code_version": "unknown",
                "tasks_processed": 0,
                "error": "No workers responding",
            }

        worker_count = len(ping_response)

        # Get task stats from first worker
        stats = inspector.stats() or {}
        tasks_processed = 0
        code_version = "unknown"

        for worker_name, worker_stats in stats.items():
            # Sum up tasks from all workers
            total = worker_stats.get("total", {})
            if isinstance(total, dict):
                for task_name, count in total.items():
                    tasks_processed += count

            # Get code version from worker (if set via signal)
            code_version = worker_stats.get("code_version", get_git_version())
            break  # Just use first worker for version

        return {
            "status": "healthy",
            "worker_count": worker_count,
            "code_version": code_version,
            "tasks_processed": tasks_processed,
        }

    except Exception as e:
        logger.warning(f"Failed to get Celery stats: {e}")
        return {
            "status": "unhealthy",
            "worker_count": 0,
            "code_version": "unknown",
            "tasks_processed": 0,
            "error": str(e)[:100],
        }


def check_celery_status() -> Dict[str, Any]:
    """Check Celery status for overall health endpoint.

    Returns simplified status for component overview.
    """
    stats = get_celery_stats()
    return {"status": stats["status"], "error": stats.get("error")}


def check_pubsub_status() -> Dict[str, Any]:
    """Check Redis pub/sub listener status.

    Returns status, listener running flag, and connected client count.
    """
    try:
        listener = get_task_done_listener()

        # Check if listener task exists and is running
        if listener._pubsub_task is None:
            listener_running = False
            status = "unhealthy"
        elif listener._pubsub_task.done():
            # Task crashed or completed unexpectedly
            listener_running = False
            status = "unhealthy"
        else:
            listener_running = True
            status = "healthy"

        # Get connected WebSocket clients
        connected_clients = listener.ws_manager.get_client_count()

        return {
            "status": status,
            "listener_running": listener_running,
            "connected_clients": connected_clients,
        }

    except Exception as e:
        logger.warning(f"Failed to check pub/sub status: {e}")
        return {
            "status": "unhealthy",
            "listener_running": False,
            "connected_clients": 0,
            "error": str(e)[:100],
        }


@router.get("")
async def health_overall() -> Dict[str, Any]:
    """Overall health check - aggregates all component statuses.

    Returns:
        - status: healthy | degraded | unhealthy
        - components: individual component statuses
        - version: current code version (git hash)
    """
    # Check all components
    celery = check_celery_status()
    redis_status = check_redis_status()
    pubsub = check_pubsub_status()

    components = {
        "fastapi": "healthy",  # If we're responding, FastAPI is healthy
        "celery": celery["status"],
        "pubsub": pubsub["status"],
        "redis": redis_status["status"],
    }

    # Determine overall status
    unhealthy_count = sum(1 for s in components.values() if s == "unhealthy")

    if unhealthy_count == 0:
        overall_status = "healthy"
    elif unhealthy_count <= 1:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    return {
        "status": overall_status,
        "components": components,
        "version": get_git_version(),
    }


@router.get("/celery")
async def health_celery() -> Dict[str, Any]:
    """Celery worker health check.

    Returns:
        - status: healthy | unhealthy
        - worker_count: number of active workers
        - code_version: git hash of worker code
        - tasks_processed: total tasks processed
        - skip_roles: roles configured to skip voice feedback
    """
    stats = get_celery_stats()

    # Get skip roles from config
    try:
        from app.config.voice_constants import SKIP_VOICE_FEEDBACK_ROLES
        skip_roles = list(SKIP_VOICE_FEEDBACK_ROLES)
    except ImportError:
        skip_roles = []

    return {
        "status": stats["status"],
        "worker_count": stats.get("worker_count", 0),
        "code_version": stats.get("code_version", "unknown"),
        "tasks_processed": stats.get("tasks_processed", 0),
        "skip_roles": skip_roles,
        **({"error": stats["error"]} if "error" in stats else {}),
    }


@router.get("/pubsub")
async def health_pubsub() -> Dict[str, Any]:
    """Redis pub/sub listener health check.

    Returns:
        - status: healthy | unhealthy
        - listener_running: whether the listener task is active
        - connected_clients: number of WebSocket clients
    """
    return check_pubsub_status()


@router.get("/redis")
async def health_redis() -> Dict[str, Any]:
    """Redis connection health check.

    Returns:
        - status: healthy | unhealthy
        - connected: whether Redis is reachable
        - error: error message if unhealthy
    """
    return check_redis_connection()
