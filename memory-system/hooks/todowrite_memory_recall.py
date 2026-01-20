#!/usr/bin/env python3
"""
PostToolUse:TodoWrite hook to trigger memory-recall skill.
Reminds Claude to recall relevant memories when planning complex tasks.

Detection logic:
- Triggers on first TodoWrite call (oldTodos empty)
- ONLY activates if task count >3 (Boss requirement)
- Tasks ≤3: Don't activate (simple task, no need)
- Blocks with instruction to invoke memory-recall skill
- No cooldown for multi-session tmux workflow
"""
import json
import sys


def is_first_todowrite_call(tool_input, tool_response):
    """
    Detect if this is the first TodoWrite call for a new task.
    ONLY activates if task count >3 (Boss requirement).

    Returns: (is_first, reason)
    """
    # Check if oldTodos is empty (reliable first-call indicator)
    old_todos = tool_response.get("oldTodos", [])
    if len(old_todos) > 0:
        return False, "oldTodos not empty - this is an update"

    # Verify we have at least one todo
    todos = tool_input.get("todos", [])
    if not todos:
        return False, "No todos provided"

    # Check task count >3 (Boss requirement: only activate for complex tasks)
    task_count = len(todos)
    if task_count <= 3:
        return False, f"Task count ≤3 ({task_count} tasks) - no need for memory-recall"

    # oldTodos is empty, have todos, and task count >3 - activate!
    return True, f"First call detected: {task_count} todos created (>3 threshold)"


def main():
    try:
        # Load input from stdin
        input_data = json.load(sys.stdin)

        # Extract tool data
        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})

        # Check if this is a first call
        is_first, reason = is_first_todowrite_call(tool_input, tool_response)

        if not is_first:
            # Not a first call - allow normal execution
            print(f"[DEBUG] {reason}", file=sys.stderr)
            sys.exit(0)

        # This is a first TodoWrite call - trigger recall!
        # Block and instruct Claude to invoke memory-recall skill
        output = {
            "decision": "block",
            "reason": "Call memory-recall skill to recall relevant memories for this task",
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse:TodoWrite",
                "additionalContext": f"Task started with {len(tool_input.get('todos', []))} todos"
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        # On any error, don't block execution
        print(f"Error in todowrite_memory_recall hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
