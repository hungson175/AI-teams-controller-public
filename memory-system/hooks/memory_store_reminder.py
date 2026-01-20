#!/usr/bin/env python3
"""
Stop hook to remind Claude to store learnings after completing tasks.
Includes robust infinite loop prevention mechanisms.
Executes only 33% of the time randomly.
"""
import json
import sys
import os
import random
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
MAX_REMINDERS_PER_SESSION = float('inf')  # No session limit
COOLDOWN_MINUTES = -1  # Disabled for tmux multi-session workflow
EXECUTION_PROBABILITY = 1/3  # Execute only 33% of the time
STATE_FILE = Path.home() / ".claude" / "memory_store_hook_state.json"


def load_state():
    """Load hook state from file."""
    if not STATE_FILE.exists():
        return {"invocations": []}

    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {"invocations": []}


def save_state(state):
    """Save hook state to file."""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save state: {e}", file=sys.stderr)


def is_within_cooldown(state):
    """Check if we're within the cooldown period."""
    if COOLDOWN_MINUTES < 0:
        return False  # Cooldown disabled, always allow reminder
    if not state.get("invocations"):
        return False

    last_invocation = state["invocations"][-1]
    last_time = datetime.fromisoformat(last_invocation["timestamp"])
    cooldown_end = last_time + timedelta(minutes=COOLDOWN_MINUTES)

    return datetime.now() < cooldown_end


def count_session_invocations(state, session_id):
    """Count how many times hook was invoked for this session."""
    return sum(1 for inv in state.get("invocations", [])
               if inv.get("session_id") == session_id)


def should_remind(input_data, state):
    """Determine if we should remind Claude to store memory."""

    # Probability check: Only execute 33% of the time
    if random.random() >= EXECUTION_PROBABILITY:
        return False, "Random probability check failed (only execute 33% of the time)"

    # Safety check 1: Don't remind if stop hook is already active (prevents infinite loop)
    if input_data.get("stop_hook_active"):
        return False, "Stop hook already active"

    # # Safety check 2: Limit reminders per session
    # session_id = input_data.get("session_id")
    # if count_session_invocations(state, session_id) >= MAX_REMINDERS_PER_SESSION:
    #     return False, f"Already reminded {MAX_REMINDERS_PER_SESSION} time(s) this session"

    # Safety check 3: Cooldown period across sessions
    if is_within_cooldown(state):
        return False, f"Within {COOLDOWN_MINUTES}-minute cooldown period"

    # Safety check 4: DISABLED - was blocking hook from firing multiple times per session
    # transcript_path = input_data.get("transcript_path")
    # if transcript_path and os.path.exists(transcript_path):
    #     try:
    #         with open(transcript_path, 'r') as f:
    #             transcript = f.read()
    #             if '"skill">project-memory-store' in transcript:
    #                 return False, "Memory-store already invoked in this session"
    #     except Exception:
    #         pass

    # All checks passed - we should remind
    return True, "Reminder needed"


def main():
    try:
        # Load input from stdin
        input_data = json.load(sys.stdin)

        # Load hook state
        state = load_state()

        # Determine if we should remind
        should_remind_claude, reason = should_remind(input_data, state)

        if should_remind_claude:
            # Record this invocation
            invocation = {
                "timestamp": datetime.now().isoformat(),
                "session_id": input_data.get("session_id"),
                "reminded": True
            }
            state.setdefault("invocations", []).append(invocation)
            save_state(state)

            # Block Claude from stopping and provide the reminder
            output = {
                "decision": "block",
                "reason": "Check if any hard-earned lessons or failure patterns warrant storage (project-memory-store). Be EXTREMELY selective. If storing: store and report in 1 line. If not: say 'Nothing worth storing.' and move on. NO explanations or analysis."
            }
            print(json.dumps(output))
            sys.exit(0)

    except Exception as e:
        # On any error, don't block Claude from stopping
        print(f"Error in memory store hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
