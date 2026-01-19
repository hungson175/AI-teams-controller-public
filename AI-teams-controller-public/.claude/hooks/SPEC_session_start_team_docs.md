# Technical Spec: SessionStart Hook - Auto-Read Team Docs

## Purpose
Force agents in tmux multi-agent team to read their role prompt and workflow.md BEFORE responding to any user messages.

## Problem
Agents in command-center team skip reading critical docs:
- `docs/tmux/command-center/prompts/{ROLE}_PROMPT.md`
- `docs/tmux/command-center/workflow.md`

This causes agents to violate team protocols (e.g., QA tests code instead of blackbox, SM forgets to coordinate, etc.).

## Requirements

### Functional
1. Detect if running in tmux multi-agent team (check for `@role_name` pane option)
2. Detect agent's role using `$TMUX_PANE` environment variable
3. Block agent startup with mandatory instructions to read team docs
4. Provide clear, non-skippable instructions
5. Only activate for command-center team (not other projects)

### Non-Functional
- Must NOT race with `setup-team.sh` (wait for role to be set)
- Must use `$TMUX_PANE` not `display-message` (pane detection bug)
- Must be executable (`chmod +x`)
- Must handle errors gracefully (don't block if error)

## Acceptance Criteria (for TDD + QA)

### AC1: Detect Role Correctly
- [ ] Hook reads `$TMUX_PANE` environment variable
- [ ] Hook uses `tmux show-options -pt $TMUX_PANE -qv @role_name` to get role
- [ ] If role is empty, hook exits without blocking (setup not complete)

### AC2: Detect Team Context
- [ ] Hook checks if in command-center team
- [ ] Hook exits without blocking if not in command-center
- [ ] Hook only activates for multi-agent teams with role assignments

### AC3: Block with Mandatory Instructions
- [ ] Hook outputs JSON with `{"decision": "block", "reason": "..."}`
- [ ] Reason includes exact file paths to read
- [ ] Reason is clear and actionable
- [ ] Agent cannot proceed without reading files

### AC4: Handle Race Conditions
- [ ] If `@role_name` not set yet, hook exits gracefully (don't block)
- [ ] Hook doesn't assume setup is complete
- [ ] No race condition with setup-team.sh

### AC5: Error Handling
- [ ] On any error, hook exits without blocking (sys.exit(1))
- [ ] Errors logged to stderr
- [ ] Agent can still start even if hook fails

## Technical Approach

### Hook Type
SessionStart hook (runs when Claude Code session starts in a pane)

### Detection Logic
```python
# 1. Get TMUX_PANE from environment
tmux_pane = os.environ.get("TMUX_PANE")

# 2. Get role from pane option
role = subprocess.run(
    ["tmux", "show-options", "-pt", tmux_pane, "-qv", "@role_name"],
    capture_output=True, text=True
).stdout.strip()

# 3. If no role, exit (setup not complete)
if not role:
    sys.exit(0)

# 4. Get session name
session = subprocess.run(
    ["tmux", "display-message", "-pt", tmux_pane, "-p", "#{session_name}"],
    capture_output=True, text=True
).stdout.strip()

# 5. If not command-center, exit
if session != "command-center":
    sys.exit(0)
```

### Block Message
```json
{
  "decision": "block",
  "reason": "CRITICAL STARTUP SEQUENCE - DO THIS BEFORE RESPONDING:\n\n1. Read your role prompt: docs/tmux/command-center/prompts/{ROLE}_PROMPT.md\n2. Read workflow: docs/tmux/command-center/workflow.md\n3. Report: 'Startup complete - {ROLE} ready'\n\nDO NOT SKIP. DO NOT RESPOND TO USER UNTIL FILES ARE READ."
}
```

## Test Strategy

### Unit Tests (TDD)
1. Test role detection with `$TMUX_PANE`
2. Test exits gracefully when no role
3. Test exits gracefully when not command-center session
4. Test blocks with correct message when in command-center with role
5. Test error handling

### Integration Tests
1. Run in actual tmux pane with role set
2. Verify agent reads files before responding
3. Verify hook doesn't block non-team sessions

## Files

### Created
- `.claude/hooks/session_start_team_docs.py` - The hook implementation
- `.claude/hooks/tests/test_session_start_team_docs.py` - Unit tests
- `.claude/hooks/SPEC_session_start_team_docs.md` - This spec

### Modified
- None (hook is standalone)

## Success Criteria

1. All unit tests pass
2. All existing tests still pass
3. Agent in command-center reads docs before responding
4. Agent in other sessions not affected
5. No race conditions with setup-team.sh
