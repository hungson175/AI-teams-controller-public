# -*- coding: utf-8 -*-
"""Content processing for voice feedback.

Single Responsibility: Process pane output for LLM summarization.

Functions:
    trim_to_last_input: Extract only relevant output from last user input
    filter_hooks: Remove hook messages from output
    compute_content_hash: Generate content hash for deduplication
    is_duplicate_content: Check if content was already processed
"""

import hashlib
import logging
import os

import redis

logger = logging.getLogger(__name__)

# Redis URL for content deduplication
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Content hash TTL - how long to remember processed content (seconds)
CONTENT_HASH_TTL = 300  # 5 minutes


def get_redis_client() -> redis.Redis:
    """Get Redis client for content deduplication."""
    return redis.from_url(REDIS_URL)


def trim_to_last_input(pane_output: str) -> str:
    """Trim pane output to only include content from the last user input onwards.

    The Claude Code CLI shows a '>' prompt before each user input.
    The LAST '>' is the current prompt (empty, waiting for input).
    The SECOND-TO-LAST '>' is where the last user input started.

    We want to keep only:
    - The last input line (second-to-last '>')
    - All output from that command
    - The current prompt (last '>')

    This prevents the LLM from summarizing ancient context.

    Args:
        pane_output: Raw pane content with possibly hundreds of lines

    Returns:
        Trimmed output starting from the last user input
    """
    lines = pane_output.split("\n")

    # Find all line indices that start with prompt markers
    # Support both '>' (ASCII) and '❯' (Unicode U+276F) for backwards compatibility
    prompt_indices = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(">") or stripped.startswith("❯"):
            prompt_indices.append(i)

    # Need at least 2 prompts: last input + current prompt
    if len(prompt_indices) < 2:
        logger.info("[CONTENT] Less than 2 prompts found, using full output")
        return pane_output

    # Second-to-last prompt is where the last input started
    last_input_idx = prompt_indices[-2]

    # Keep everything from last input onwards
    trimmed_lines = lines[last_input_idx:]
    trimmed = "\n".join(trimmed_lines)

    logger.info(
        f"[CONTENT] Trimmed output: {len(lines)} -> {len(trimmed_lines)} lines "
        f"(last input at line {last_input_idx})"
    )

    return trimmed


def filter_hooks(pane_output: str) -> str:
    """Filter out hook messages from pane output.

    Detects common hook markers and truncates output at first occurrence.
    This prevents hook messages from overwhelming actual response in narrow panes.

    Args:
        pane_output: Raw pane content

    Returns:
        Filtered output without hook messages
    """
    # Hook markers to detect (case-insensitive)
    hook_markers = [
        "Stop hook",
        "PostToolUse hook",
        "PreToolUse hook",
        "SessionStart hook",
        "<system-reminder>",
        "coder-memory-store",
        "Consider if any valuable patterns",
        "Skill tool",
        "storing patterns",
    ]

    lines = pane_output.split("\n")
    filtered_lines = []

    for line in lines:
        # Check if this line contains any hook marker
        line_lower = line.lower()
        is_hook = any(marker.lower() in line_lower for marker in hook_markers)

        if is_hook:
            # Found hook marker - stop here, don't include this or subsequent lines
            logger.info(f"[CONTENT] Hook detected, truncating at: {line[:50]}...")
            break

        filtered_lines.append(line)

    return "\n".join(filtered_lines)


def compute_content_hash(content: str) -> str:
    """Compute a short hash of content for deduplication.

    Args:
        content: Text content to hash

    Returns:
        16-character MD5 hash prefix
    """
    return hashlib.md5(content.encode()).hexdigest()[:16]


def is_duplicate_content(team_id: str, role_id: str, content_hash: str) -> bool:
    """Check if we already processed this exact content.

    Uses Redis to track last processed content hash per pane.
    Returns True if duplicate (should skip), False if new content.

    On Redis error, returns False (fail-open) to avoid blocking voice feedback.

    Args:
        team_id: tmux session name
        role_id: pane identifier
        content_hash: Hash of content to check

    Returns:
        True if duplicate (should skip), False if new content
    """
    try:
        redis_client = get_redis_client()
        key = f"voice_feedback:last_hash:{team_id}:{role_id}"

        last_hash = redis_client.get(key)
        if last_hash and last_hash.decode() == content_hash:
            logger.info(
                f"[CONTENT] Duplicate content detected: {team_id}/{role_id} "
                f"hash={content_hash} (skipping)"
            )
            return True

        # Store new hash with TTL
        redis_client.setex(key, CONTENT_HASH_TTL, content_hash)
        return False

    except Exception as e:
        logger.warning(f"[CONTENT] Redis error in dedup check, proceeding: {e}")
        return False  # Fail-open: proceed with processing on Redis error
