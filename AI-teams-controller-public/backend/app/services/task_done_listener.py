# -*- coding: utf-8 -*-
"""TaskDoneListener service for voice feedback integration.

Architecture: Celery-based (v4)
- Stop hook fires → queue Celery task → return immediately
- Celery worker processes: LLM summary + TTS
- Redis pub/sub broadcasts to ALL WebSocket clients
- Works regardless of which team is active in UI

Story 7: Content deduplication consolidated to this layer (FastAPI entry point).
"""

import asyncio
import hashlib
import json
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import redis
import redis.asyncio as aioredis

from app.config.voice_constants import (
    CONTENT_DEDUP_TTL,
    DEDUP_KEY_PREFIX,
    TASK_DONE_DEBOUNCE_MS,
)

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
VOICE_FEEDBACK_CHANNEL = "voice_feedback"


# === Content Deduplication Functions (Story 7) ===


def get_dedup_redis_client() -> redis.Redis:
    """Get synchronous Redis client for content deduplication."""
    return redis.from_url(REDIS_URL)


def trim_to_last_input(pane_output: str) -> str:
    """Trim pane output to only include content from the last user input onwards.

    The Claude Code CLI shows a '>' prompt before each user input.
    We keep only content from the second-to-last '>' (last user input) onwards.
    """
    lines = pane_output.split("\n")

    # Find all line indices that start with '>' (prompt markers)
    prompt_indices = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(">"):
            prompt_indices.append(i)

    # Need at least 2 prompts: last input + current prompt
    if len(prompt_indices) < 2:
        return pane_output

    # Second-to-last prompt is where the last input started
    last_input_idx = prompt_indices[-2]

    # Keep everything from last input onwards
    return "\n".join(lines[last_input_idx:])


def compute_content_hash(content: str) -> str:
    """Compute a short hash of content for deduplication.

    Returns 16-character MD5 hash prefix.
    """
    return hashlib.md5(content.encode()).hexdigest()[:16]


def is_duplicate_content(team_id: str, role_id: str, content_hash: str) -> bool:
    """Check if we already processed this exact content.

    Uses Redis with consolidated key format: voice_feedback:dedup:{team}:{role}:{hash}
    Returns True if duplicate (should skip), False if new content.
    Fails open on Redis error (returns False).
    """
    try:
        redis_client = get_dedup_redis_client()
        key = f"{DEDUP_KEY_PREFIX}:{team_id}:{role_id}:{content_hash}"

        # Check if key exists
        if redis_client.get(key):
            logger.info(f"[DEDUP] Duplicate content: {team_id}/{role_id} hash={content_hash}")
            return True

        # Store key with TTL
        redis_client.setex(key, CONTENT_DEDUP_TTL, "1")
        return False

    except Exception as e:
        logger.warning(f"[DEDUP] Redis error, proceeding: {e}")
        return False  # Fail-open


@dataclass
class PendingCommand:
    """Last voice command sent to a pane, waiting for Stop hook."""

    command_id: str
    team_id: str
    role_id: str
    raw_command: str
    corrected_command: str
    timestamp: datetime
    speed: float = 1.0  # TTS speech speed (0.5-2.0, default 1.0 = normal)


class GlobalWebSocketManager:
    """Manages WebSocket connections for ALL clients.

    Unlike the old per-pane registry, this broadcasts to ALL connected
    clients regardless of which team they're viewing. Clients filter
    messages by team_id/role_id on their end.
    """

    def __init__(self):
        self._websockets: Set[Any] = set()
        self._lock = asyncio.Lock()

    async def register(self, websocket: Any):
        """Register a WebSocket for global broadcast."""
        async with self._lock:
            self._websockets.add(websocket)
            logger.info(f"[WS] Registered global WebSocket. Total: {len(self._websockets)}")

    async def unregister(self, websocket: Any):
        """Remove WebSocket from registry."""
        async with self._lock:
            self._websockets.discard(websocket)
            logger.info(f"[WS] Unregistered global WebSocket. Total: {len(self._websockets)}")

    async def broadcast(self, message: dict):
        """Broadcast message to ALL connected WebSockets."""
        async with self._lock:
            if not self._websockets:
                logger.debug("[WS] No WebSockets connected for broadcast")
                return

            # Send to all, handle failures gracefully
            failed = []
            for ws in self._websockets:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    logger.warning(f"[WS] Send failed: {e}")
                    failed.append(ws)

            # Clean up failed connections
            for ws in failed:
                self._websockets.discard(ws)

            logger.info(f"[WS] Broadcast sent to {len(self._websockets)} clients")

    def get_client_count(self) -> int:
        """Return number of connected WebSocket clients."""
        return len(self._websockets)


class TaskDoneListener:
    """
    Service to queue voice feedback tasks when Claude Code Stop events fire.

    v4 Architecture: Celery-based with global broadcast.
    - Stop hook → queue Celery task → immediate response
    - Celery worker does LLM + TTS in background
    - Redis pub/sub notifies all WebSocket clients
    """

    def __init__(self):
        # Last command per pane: {pane_key: PendingCommand}
        self._last_commands: Dict[str, PendingCommand] = {}

        # Global WebSocket manager (broadcasts to ALL clients)
        self.ws_manager = GlobalWebSocketManager()

        # Redis pub/sub listener task
        self._pubsub_task: Optional[asyncio.Task] = None

        # Track last task-done timestamp per pane for debouncing
        self._last_task_done: Dict[str, datetime] = {}

    def _pane_key(self, team_id: str, role_id: str) -> str:
        """Generate stable key for pane identification."""
        return f"{team_id}:{role_id}"

    # === Voice Command Flow ===

    def command_sent(
        self,
        team_id: str,
        role_id: str,
        raw_command: str,
        corrected_command: str,
        command_id: Optional[str] = None,
        speed: float = 1.0,
    ) -> str:
        """
        Called when voice command sent to tmux pane.
        Stores as last command for this pane (overwrites previous).

        Returns:
            command_id for correlation
        """
        key = self._pane_key(team_id, role_id)
        cmd_id = command_id or str(uuid.uuid4())

        self._last_commands[key] = PendingCommand(
            command_id=cmd_id,
            team_id=team_id,
            role_id=role_id,
            raw_command=raw_command,
            corrected_command=corrected_command,
            timestamp=datetime.now(),
            speed=speed,
        )

        logger.info(
            f"[VOICE] Command stored: {key} | "
            f"'{corrected_command[:50]}{'...' if len(corrected_command) > 50 else ''}' | "
            f"speed={speed}"
        )
        return cmd_id

    def get_pending_command(self, team_id: str, role_id: str) -> Optional[PendingCommand]:
        """Get pending command without consuming it."""
        key = self._pane_key(team_id, role_id)
        return self._last_commands.get(key)

    # === Stop Hook Flow (Celery-based) ===

    async def stop_hook_fired(
        self,
        team_id: str,
        role_id: str,
        pane_output: str,
        request_id: str = "",
    ) -> Dict:
        """
        Called when Claude Code Stop hook fires.
        Queues Celery task for background processing.

        Args:
            team_id: tmux session name
            role_id: pane index
            pane_output: captured output from pane

        Returns:
            Dict with success status and task_id
        """
        # Process voice feedback for ALL panes (removed pane-0 restriction)
        # Debounce logic below prevents duplicate feedback
        key = self._pane_key(team_id, role_id)
        log_prefix = f"[VOICE:{request_id}]" if request_id else "[VOICE]"

        # DEBOUNCE: Skip if task-done fired too recently for this pane
        now = datetime.now()
        last_fired = self._last_task_done.get(key)
        if last_fired:
            elapsed_ms = (now - last_fired).total_seconds() * 1000
            if elapsed_ms < TASK_DONE_DEBOUNCE_MS:
                logger.info(
                    f"{log_prefix} DEBOUNCE-SKIP: {key} | "
                    f"elapsed={int(elapsed_ms)}ms < threshold={TASK_DONE_DEBOUNCE_MS}ms"
                )
                return {"success": True, "skipped": True, "reason": "debounced"}
        logger.info(f"{log_prefix} DEBOUNCE-PASS: {key}")

        # Update last fired timestamp
        self._last_task_done[key] = now

        # CONTENT DEDUP (Story 7): Check if same content was processed recently
        trimmed = trim_to_last_input(pane_output)
        content_hash = compute_content_hash(trimmed)
        logger.info(f"{log_prefix} DEDUP-CHECK: {key} hash={content_hash} trimmed={len(trimmed)} chars")

        if is_duplicate_content(team_id, role_id, content_hash):
            logger.info(f"{log_prefix} DEDUP-SKIP: {key} hash={content_hash} (duplicate content)")
            return {"success": True, "skipped": True, "reason": "duplicate_content"}
        logger.info(f"{log_prefix} DEDUP-PASS: {key} (new content)")

        # Get last command if available (optional enrichment)
        command = self._last_commands.pop(key, None)
        original_command = command.corrected_command if command else "task"
        command_id = command.command_id if command else str(uuid.uuid4())
        speed = command.speed if command else 1.0  # Get speed from command or use default (1.0 = normal)

        logger.info(f"{log_prefix} QUEUE-START: {key} | has_command={'yes' if command else 'no'} | speed={speed}")

        try:
            # Queue Celery task for background processing
            from app.services.celery_tasks import process_voice_feedback

            task = process_voice_feedback.delay(
                team_id=team_id,
                role_id=role_id,
                pane_output=pane_output,
                original_command=original_command,
                request_id=request_id,  # Pass for tracing
                speed=speed,  # Pass speed to Celery task
            )

            logger.info(f"{log_prefix} QUEUE-SUCCESS: {key} | celery_task_id={task.id}")

            return {
                "success": True,
                "command_id": command_id,
                "task_id": task.id,
                "message": "Processing in background",
            }

        except Exception as e:
            logger.error(f"{log_prefix} QUEUE-FAILED: {key} | error={e}")
            return {"success": False, "error": str(e)[:200]}

    # === Redis Pub/Sub Listener ===

    async def start_pubsub_listener(self):
        """Start listening for Redis pub/sub messages from Celery workers.

        Includes liveness check: if previous task crashed (done() == True),
        it will be automatically restarted instead of silently failing.
        """
        logger.info("[PUBSUB-STARTUP] start_pubsub_listener() called")

        # Check if task exists AND is still running
        if self._pubsub_task is not None and not self._pubsub_task.done():
            logger.warning("[PUBSUB-STARTUP] Listener already running, skipping")
            return

        # Restart dead task if needed
        if self._pubsub_task is not None:
            logger.info("[PUBSUB-STARTUP] Previous task was dead, restarting")

        self._pubsub_task = asyncio.create_task(self._pubsub_loop())
        logger.info("[PUBSUB-STARTUP] Created asyncio task for _pubsub_loop")

    async def stop_pubsub_listener(self):
        """Stop the Redis pub/sub listener."""
        if self._pubsub_task:
            self._pubsub_task.cancel()
            try:
                await self._pubsub_task
            except asyncio.CancelledError:
                pass
            self._pubsub_task = None
            logger.info("[VOICE] Stopped Redis pub/sub listener")

    async def _pubsub_loop(self):
        """Main loop for receiving Redis pub/sub messages."""
        logger.info("[PUBSUB-LOOP] _pubsub_loop() started")
        try:
            r = aioredis.from_url(REDIS_URL)
            pubsub = r.pubsub()
            await pubsub.subscribe(VOICE_FEEDBACK_CHANNEL)
            logger.info(f"[PUBSUB] Subscribed to {VOICE_FEEDBACK_CHANNEL}")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        ws_count = self.ws_manager.get_client_count()
                        logger.info(
                            f"[PUBSUB] RECEIVED: {data.get('team_id')}/{data.get('role_id')} | "
                            f"ws_clients={ws_count} | audio_len={len(data.get('audio', ''))}"
                        )

                        # Broadcast to ALL connected WebSocket clients
                        await self.ws_manager.broadcast(data)
                        logger.info(f"[PUBSUB] BROADCAST-COMPLETE: sent to {ws_count} clients")

                    except json.JSONDecodeError as e:
                        logger.error(f"[PUBSUB] Invalid JSON: {e}")
                    except Exception as e:
                        logger.error(f"[PUBSUB] Handler error: {e}")

        except asyncio.CancelledError:
            logger.info("[PUBSUB] Loop cancelled")
            raise
        except Exception as e:
            logger.error(f"[PUBSUB] Loop error: {e}")
            # Don't restart automatically - let supervisor handle it

    # === Legacy WebSocket Registry (kept for backward compatibility) ===

    def register_websocket(self, team_id: str, role_id: str, websocket: Any):
        """Register WebSocket for voice feedback (legacy - use ws_manager.register instead)."""
        # Delegate to global manager
        asyncio.create_task(self.ws_manager.register(websocket))
        logger.info(f"[VOICE] Legacy WebSocket registered: {team_id}/{role_id}")

    def unregister_websocket(self, team_id: str, role_id: str):
        """Remove WebSocket from registry (legacy)."""
        # Note: Can't unregister specific WS without reference
        # This is a limitation of the legacy API
        logger.info(f"[VOICE] Legacy WebSocket unregistered: {team_id}/{role_id}")


# Module-level singleton (safe: state is in per-pane dicts)
_listener: Optional[TaskDoneListener] = None


def get_task_done_listener() -> TaskDoneListener:
    """Get or create the TaskDoneListener singleton."""
    global _listener
    if _listener is None:
        _listener = TaskDoneListener()
    return _listener
