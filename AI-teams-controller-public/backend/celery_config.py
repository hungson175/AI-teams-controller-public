# -*- coding: utf-8 -*-
"""Celery configuration for voice feedback background tasks.

This module configures Celery with Redis as the message broker.
The worker runs independently and processes voice feedback tasks
regardless of which team is active in the UI.

Usage:
    # Start Redis (if not running)
    redis-server

    # Start Celery worker
    cd backend
    uv run celery -A celery_config worker --loglevel=info
"""

import logging
import os
import subprocess
from datetime import datetime

from celery import Celery
from celery.signals import worker_ready
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Version tracking - captured at module load time
WORKER_CODE_VERSION = "unknown"
WORKER_STARTED_AT = None


def _get_git_version() -> str:
    """Get current git commit hash for version tracking."""
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
    except Exception:
        return "unknown"


# Capture version at import time
WORKER_CODE_VERSION = _get_git_version()


@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    """Signal handler when worker is ready - log version info."""
    global WORKER_STARTED_AT
    WORKER_STARTED_AT = datetime.utcnow().isoformat() + "Z"
    logger.info(f"[CELERY] Worker ready. Version: {WORKER_CODE_VERSION}, Started: {WORKER_STARTED_AT}")

# Redis configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "voice_feedback",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.services.celery_tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Result expiration (1 hour)
    result_expires=3600,

    # Task queue expiration: discard tasks waiting >5 minutes (300 seconds)
    # Prevents stale voice feedback from being processed when worker restarts
    task_default_expires=300,

    # Task execution time limit: kill task if running >2 minutes
    task_time_limit=120,
    task_soft_time_limit=90,  # Raise SoftTimeLimitExceeded at 90s

    # Task execution settings
    task_acks_late=True,  # Acknowledge after task completes (reliability)
    task_reject_on_worker_lost=True,  # Requeue if worker dies

    # Concurrency settings
    worker_prefetch_multiplier=1,  # One task at a time per worker

    # Retry settings for broker connection
    broker_connection_retry_on_startup=True,
)
