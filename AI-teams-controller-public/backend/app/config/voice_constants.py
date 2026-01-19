# -*- coding: utf-8 -*-
"""Voice feedback system constants.

Centralized configuration for voice feedback timing, debouncing, and output handling.
Extracted from task_done_listener.py and celery_tasks.py (Wave 1 Refactoring).
"""

# Debounce window for task completion events (milliseconds)
# Prevents duplicate voice feedback when Stop hook fires multiple times
TASK_DONE_DEBOUNCE_MS = 10000  # 10 seconds

# Delay before processing stop hook (milliseconds)
# Allows pane output to stabilize before capture
STOP_HOOK_DELAY_MS = 300  # 300ms

# Timeout for tmux pane capture operations (seconds)
# Maximum time to wait for tmux capture-pane command
TMUX_CAPTURE_TIMEOUT = 5  # 5 seconds

# Number of output lines to include in LLM summary
# Truncates long pane output to last N lines for context
OUTPUT_TRUNCATE_LINES = 100  # Last 100 lines

# === Content Deduplication (Story 7) ===
# Consolidated dedup at FastAPI layer only

# Content deduplication TTL (seconds)
# Same content within this window is deduplicated
CONTENT_DEDUP_TTL = 30  # 30 seconds

# Redis key prefix for content deduplication
# Key format: {prefix}:{team_id}:{role_id}:{content_hash}
DEDUP_KEY_PREFIX = "voice_feedback:dedup"
