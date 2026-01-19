# Team Creator

Visual canvas for designing and monitoring AI agent team configurations.

## Modes

### Design Mode (Default)
Create and edit team layouts without connecting to tmux.

- **Templates**: Load pre-built team configurations (Full Stack, Minimal, etc.)
- **Save/Load**: Persist configurations to localStorage
- **Export/Import**: Share configurations as JSON files
- **Drag nodes**: Reposition team members on canvas
- **Create edges**: Connect roles to define communication flow

### Monitor Mode
View live agent status from running tmux sessions.

- **Team selector**: Choose from available tmux sessions
- **Live status**: Green dot = active, gray dot = idle
- **WebSocket**: Real-time updates via `/api/ws/state/{team}/{role}`

## Usage

1. **Design a team**: Start in Design mode, load a template or create from scratch
2. **Save your layout**: Use Save button to persist to localStorage
3. **Monitor live team**: Switch to Monitor mode, select a tmux session
4. **View status**: Status dots show which agents are active

## Components

| Component | Purpose |
|-----------|---------|
| `TeamCreatorPanel` | Main container with mode state |
| `TeamFlowCanvas` | React Flow canvas with nodes/edges |
| `TeamToolbar` | Toolbar with mode toggle, templates, save/load |
| `ModeToggle` | Design/Monitor mode switch |
| `TeamSelector` | Team dropdown for Monitor mode |
| `RoleNode` | Custom node with status dot |

## Edge Types

- **Command** (solid): One-way task delegation
- **Bidirectional** (violet): Two-way communication
- **Advisory** (dashed blue): Guidance/suggestions
- **Review** (dashed red): Code review flow

## WebSocket Connection

In Monitor mode, the app connects to WebSocket endpoints for each role:
```
ws://localhost:17061/api/ws/state/{team}/{role}
```

Messages received:
```json
{ "isActive": true }
```

Connection states:
- `disconnected`: Not connected
- `connecting`: Establishing connection
- `connected`: Receiving live updates
- `error`: Connection failed

## Templates

| Template | Roles |
|----------|-------|
| Full Stack | PM, SA, FE, BE, CR |
| Full Team + DK | PM, SA, FE, BE, CR, DK |
| Minimal | PM, FE |
| Backend Focus | PM, SA, BE, CR |

## Files

```
components/team-creator/
  TeamCreatorPanel.tsx    # Main container
  TeamFlowCanvas.tsx      # React Flow canvas
  WorkflowMatrix.tsx      # Matrix view (alternative)
  controls/
    TeamToolbar.tsx       # Toolbar with all controls
    ModeToggle.tsx        # Design/Monitor toggle
    TeamSelector.tsx      # Team dropdown
    TemplateSelector.tsx  # Template dropdown
  nodes/
    RoleNode.tsx          # Custom node with status
  edges/
    CommunicationEdge.tsx # Custom edge with type selector

hooks/
  useTeamStatus.ts        # WebSocket hook for status

lib/team-creator/
  types.ts                # TypeScript types
  templates.ts            # Pre-built templates
  storage.ts              # localStorage helpers
```
