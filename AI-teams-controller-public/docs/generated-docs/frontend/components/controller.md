# TmuxController Component

Main control panel for tmux team management.

## Overview

Central component for terminal monitoring and command input.

**Location:** `frontend/components/controller/TmuxController.tsx`

## Features

| Feature | Description |
|---------|-------------|
| **Team Selector** | Dropdown with activity indicators (green = active) |
| **Role Tabs** | Pane tabs with activity dots (green pulse = working) |
| **Terminal Output** | Real-time WebSocket streaming |
| **Message Input** | Send commands with voice support |
| **Tab Navigation** | Monitor (terminal) / Browse (file browser) |

## Sub-components

| Component | Purpose |
|-----------|---------|
| `TeamSidebar` | Team list, kill/restart/create buttons |
| `LoadTeamDialog` | Load existing teams from disk |
| `CreateTeamDialog` | Create new team from template |
| `HeadphoneButton` | Media Session integration for headphone controls |

## Usage

```tsx
<TmuxController />
```

Typically rendered as the main content of the Controller tab.

## State Management

Uses several hooks for state:

```tsx
const { teams, roles, selectedTeam, selectedRole } = useTeamState()
const { paneStates, wsConnected } = usePanePolling({...})
const { handleKillTeam, handleRestartTeam } = useTeamLifecycle({...})
```

## Auto-Scroll Behavior

- Automatically scrolls to bottom on new output
- Manual scroll up disables auto-scroll
- Scroll FAB appears when not at bottom
- Scroll to bottom re-enables auto-scroll

## Activity Indicators

- **Team level**: Green text if ANY role is active
- **Role level**: Green dot with pulse animation if role is working
- Polling interval: 5 seconds
