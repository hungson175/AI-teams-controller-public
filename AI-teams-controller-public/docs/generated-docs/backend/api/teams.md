# Team Management API

Endpoints for managing tmux sessions and panes.

## Endpoints

### List Teams

```http
GET /api/teams
```

Returns all tmux sessions with activity status.

**Response:**
```json
{
  "teams": [
    {
      "id": "command-center",
      "name": "command-center",
      "isActive": true
    }
  ]
}
```

### List Available Teams

```http
GET /api/teams/available
```

Lists teams available to load from disk (`~/.claude/dev/` and `docs/tmux/`).

### List Roles

```http
GET /api/teams/{team_id}/roles
```

Returns panes in a session with activity status.

**Response:**
```json
{
  "roles": [
    {"id": "pane-0", "name": "PO", "isActive": true},
    {"id": "pane-1", "name": "SM", "isActive": false}
  ]
}
```

### Send Message

```http
POST /api/send/{team_id}/{role_id}
```

Sends message to a pane (uses `tm-send` for two-enter rule).

**Request:**
```json
{
  "message": "Hello from API"
}
```

### Get Pane State

```http
GET /api/state/{team_id}/{role_id}
```

Returns current pane output (REST alternative to WebSocket).

### WebSocket: Real-time Output

```
ws://backend:17061/api/ws/state/{team_id}/{role_id}
```

Streams pane output in real-time. Supports configuration:

```json
{"interval": 0.5}      // Polling: 0.5, 1, or 2 seconds
{"captureLines": 100}  // Lines to capture: 50-500
{"pause": true}        // Pause/resume streaming
```

## Commander Lifecycle

### Kill Team

```http
POST /api/teams/{team_id}/kill
Authorization: Bearer <token>
```

Kills tmux session. Requires JWT.

### Restart Team

```http
POST /api/teams/{team_id}/restart
Authorization: Bearer <token>
```

Kills session, finds `setup-team.sh` in README, runs script.

### Create Terminal

```http
POST /api/teams/create-terminal
Authorization: Bearer <token>
```

**Request:**
```json
{
  "name": "my-terminal"  // Optional, auto-generates if omitted
}
```

Creates new detached tmux session.
