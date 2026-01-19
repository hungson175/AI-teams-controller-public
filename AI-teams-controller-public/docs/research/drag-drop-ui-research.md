# Drag & Drop UI Research for Team Creator Module

**Date**: 2025-12-12
**Status**: RESEARCH COMPLETE
**Researcher**: CR Agent

---

## Executive Summary

After comprehensive research, **React Flow (@xyflow/react)** is the recommended library for building the Team Creator module - a visual workflow editor for managing AI agent teams.

---

## Requirements

1. **Visual Node-Based Editor**: Drag & drop roles/agents onto canvas
2. **Connection Lines**: Show communication flow between agents
3. **Real-time Status**: Highlight active/running agents
4. **Team Configuration**: Define team structure visually
5. **Integration**: Works with Next.js 16 + React 19 + shadcn/ui

---

## Winner: React Flow (@xyflow/react)

### Why React Flow?

| Criteria | Score | Notes |
|----------|-------|-------|
| Node-based editing | ✅ | Native support for nodes + edges |
| Connections | ✅ | Built-in edge routing |
| Real-time updates | ✅ | State-driven, React-native |
| Next.js compatibility | ✅ | Official template available |
| shadcn/ui integration | ✅ | xyflow.com/ui (shadcn-based) |
| License | ✅ | MIT |
| Maintenance | ✅ | Active 2024-25, v12.x |
| Community | ✅ | 23k+ GitHub stars |

### Production Usage

React Flow is used by:
- **Flowise** - LLM workflow builder
- **LangFlow** - LangChain visual editor
- **n8n** - Workflow automation
- **Stripe** - Internal tools
- **Typeform** - Form builder

### Quick Start

```bash
npm install @xyflow/react
# or
pnpm add @xyflow/react
```

### Official Resources

- **Documentation**: https://reactflow.dev/
- **Next.js Template**: https://reactflow.dev/ui/templates/workflow-editor
- **shadcn/ui Components**: https://xyflow.com/ui (pre-built node components)

---

## Rejected Alternatives

### 1. dnd-kit
- **Pros**: Modern, lightweight, accessible
- **Cons**: No connection/edge support - only drag & drop
- **Verdict**: ❌ Good for sortable lists, not workflow editors

### 2. react-beautiful-dnd
- **Pros**: Smooth animations
- **Cons**: DEPRECATED (Atlassian archived), no maintenance
- **Verdict**: ❌ Not recommended for new projects

### 3. Rete.js
- **Pros**: Visual scripting, data flow
- **Cons**: Steeper learning curve, less React-native
- **Verdict**: ⚠️ Overkill for team management

### 4. Cytoscape.js
- **Pros**: Graph visualization
- **Cons**: Not drag & drop focused, more for data viz
- **Verdict**: ❌ Wrong use case

---

## Architecture Recommendation

### Component Structure

```
frontend/
├── app/
│   └── page.tsx                    # Main page with tabs
├── components/
│   └── team-creator/
│       ├── TeamCreatorPanel.tsx    # Main container (React Flow canvas)
│       ├── nodes/
│       │   ├── RoleNode.tsx        # Custom node for agent role
│       │   └── TeamNode.tsx        # Custom node for team grouping
│       ├── edges/
│       │   └── CommunicationEdge.tsx  # Custom edge for agent communication
│       └── sidebar/
│           └── RolePalette.tsx     # Draggable role templates
└── lib/
    └── team-creator/
        ├── types.ts                # TypeScript types for nodes/edges
        └── templates.ts            # Pre-defined team templates
```

### UI Placement

**Recommended**: Add as leftmost tab in the main interface

```
┌─────────────────────────────────────────────────────┐
│  [Team Creator] | [Teams] | [Settings]              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐                                       │
│  │ Sidebar  │    ┌─────────────────────────────┐   │
│  │          │    │                             │   │
│  │ PM ○     │    │     React Flow Canvas       │   │
│  │ SA ○     │    │                             │   │
│  │ FE ○     │    │   [PM] ─────> [SA]          │   │
│  │ BE ○     │    │     │          │            │   │
│  │ CR ○     │    │     v          v            │   │
│  │          │    │   [FE]  <──> [BE]           │   │
│  │          │    │     └──────────┘            │   │
│  │          │    │          │                  │   │
│  └──────────┘    │          v                  │   │
│                  │        [CR]                 │   │
│                  └─────────────────────────────┘   │
│                                                     │
│  [Save Team] [Load Template] [Export Config]        │
└─────────────────────────────────────────────────────┘
```

### Key Features to Implement

1. **Drag from Sidebar**: Roles in sidebar are draggable onto canvas
2. **Connect Nodes**: Draw edges between roles to define communication
3. **Node Status**: Color-coded based on tmux pane status (idle/running/error)
4. **Team Templates**: Pre-built configurations (e.g., "Full Stack Team", "Data Team")
5. **Export/Import**: Save team config as JSON for sharing

---

## Implementation Sprints (Estimated)

| Sprint | Goal | Complexity |
|--------|------|------------|
| S1 | React Flow setup + basic canvas | Low |
| S2 | Custom RoleNode + styling | Medium |
| S3 | Sidebar with draggable roles | Medium |
| S4 | Edge connections + validation | Medium |
| S5 | Real-time status from tmux | High |
| S6 | Save/Load team configurations | Medium |

---

## References

- React Flow Docs: https://reactflow.dev/
- React Flow GitHub: https://github.com/xyflow/xyflow
- Flowise Source: https://github.com/FlowiseAI/Flowise
- LangFlow Source: https://github.com/langflow-ai/langflow
- xyflow/ui (shadcn): https://xyflow.com/ui

---

## Next Steps

1. **SA**: Design detailed ADR for Team Creator module
2. **FE**: Set up React Flow with shadcn/ui integration
3. **BE**: Add endpoint for team configuration CRUD
4. **PM**: Break down into progressive sprints
