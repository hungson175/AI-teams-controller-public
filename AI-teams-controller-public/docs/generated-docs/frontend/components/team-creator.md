# TeamCreator Component

Visual team builder using React Flow.

## Overview

Drag-drop editor for designing AI agent team configurations.

**Location:** `frontend/components/team-creator/`

## Components

| Component | Purpose |
|-----------|---------|
| `TeamCreatorPanel.tsx` | Layout, sidebar, mode state |
| `TeamFlowCanvas.tsx` | React Flow canvas |
| `RolePalette.tsx` | Draggable role cards |
| `RoleNode.tsx` | Custom node with status indicator |
| `CommunicationEdge.tsx` | Custom edge with type selector |
| `ModeToggle.tsx` | Design/Monitor mode switch |
| `TeamSelector.tsx` | Live team dropdown |
| `TemplateSelector.tsx` | Pre-built templates |
| `TeamToolbar.tsx` | Save/Load/Export buttons |

## Modes

| Mode | Purpose |
|------|---------|
| **Design** | Create/edit team layouts (offline) |
| **Monitor** | View real-time status of live team |

## Available Roles

| Role | Color | Description |
|------|-------|-------------|
| PM | Violet | Project Manager |
| SA | Blue | Solution Architect |
| BE | Orange | Backend Engineer |
| FE | Green | Frontend Engineer |
| CR | Red | Code Reviewer |
| DK | Cyan | Document Keeper |
| BL | Pink | Backlog Organizer |

## Edge Types

| Type | Color | Meaning |
|------|-------|---------|
| `command` | Blue | One-way command flow |
| `bidirectional` | Green | Two-way communication |
| `advisory` | Amber | Guidance/suggestions |
| `review` | Red | Code review flow |

## Pre-built Templates

- Full Stack (PM, SA, BE, FE, CR)
- Full Team + DK (6 roles)
- Minimal (PM, Coder)
- Backend Focus (PM, SA, BE, CR)

## Usage

```tsx
<TeamCreatorPanel />
```

## Data Persistence

- **localStorage**: Current canvas state, unsaved changes
- **Export**: Download as JSON file
- **Import**: Load from JSON file
