# TmuxService

Production service for tmux subprocess commands.

## Overview

Implements `TeamService` abstract interface for real tmux operations.

**Location:** `backend/app/services/tmux_service.py`

## Key Methods

### get_teams()

Lists all tmux sessions.

```python
# Runs: tmux list-sessions -F "#{session_name}"
teams = service.get_teams()
# Returns: [{"id": "command-center", "name": "command-center", "isActive": true}]
```

### get_roles(team_id)

Lists panes in a session with activity status.

```python
# Runs: tmux list-panes -t {session} -F "#{pane_id} #{pane_index} #{@role_name}"
roles = service.get_roles("command-center")
# Returns: [{"id": "pane-0", "name": "PO", "isActive": true}]
```

### send_message(team_id, role_id, message)

Sends message to pane using `tm-send` (handles two-enter rule).

```python
# Runs: tm-send {pane} "{message}"
result = service.send_message("command-center", "pane-0", "Hello")
```

### get_pane_state(team_id, role_id)

Captures current pane output.

```python
# Runs: tmux capture-pane -t {pane} -p
output = service.get_pane_state("command-center", "pane-0")
```

## Commander Lifecycle Methods

### kill_team(team_id)

```python
# Validates team exists, then:
# tmux kill-session -t {team_id}
service.kill_team("command-center")
```

### restart_team(team_id)

1. Kill session
2. Find README at `docs/tmux/{team_id}/README.md`
3. Parse for `setup-team.sh` pattern
4. Run script with 60s timeout

```python
result = service.restart_team("command-center")
# Returns: {"success": true, "script_found": true, "output": "..."}
```

### create_terminal(name)

```python
# tmux new-session -d -s {name}
service.create_terminal("my-terminal")
```

## Two-Enter Rule

Claude CLI in tmux requires two Enter keypresses with 0.3s delay. The `tm-send` utility handles this automatically.
