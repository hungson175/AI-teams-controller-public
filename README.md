# AI Teams Controller - Autonomous Multi-Agent Development System

**Built by**: Hung Son
**Demo Video**: [Link TBD]

---

## What This Is

A production-ready autonomous AI software development system built on Claude Code. Real working multi-agent teams that coordinate via tmux, maintain persistent memory across all projects, and provide an optional web UI for team management.

**This is not a demo.** It's a system I built and use daily for real development work.

---

## Key Features

- **Multi-Agent Coordination**: Teams of AI agents working together via tmux sessions
- **Self-Improving**: Two types of memory - technical solutions in vector DB, procedural improvements embedded by Scrum Master
- **3 Teams**: Scrum, Light, McKinsey
- **Voice Input Support**: Natural voice commands to AI teams
- **Web UI**: Visual control interface (optional - agents work via pure tmux too)

---

## Quick Start

**Prerequisites**: Python 3.11+, Node.js 20+, pnpm, tmux, Docker, Claude Code CLI

**Installation**:
1. Clone this repository
2. Open project in Claude Code
3. Ask Claude Code: "Read docs/README/INSTALLATION-FOR-CLAUDE-CODE.md and install the system"
4. Claude Code will read the installation guide and handle everything

**Why Claude Code handles installation?** AI-guided setup adapts to your system and resolves issues automatically. Better than rigid bash scripts.

**For detailed installation instructions**, see: [docs/README/INSTALLATION-FOR-CLAUDE-CODE.md](./docs/README/INSTALLATION-FOR-CLAUDE-CODE.md)

---

## Slash Command

**Quick team creation**:
```bash
/create-tmux-team [optional-name]
```

**What it does**: Creates and starts a tmux team for your current project in ONE command.

**When to use**: For projects that don't have a team yet.

**Features**:
- Auto-detects team name from project directory
- Checks for existing team first (prevents duplicates)
- Starts team immediately after creation

---

## What's Included

This repository contains three installable components:

### Component 1: tmux Team Creator Skill
Claude Code skill that creates and manages multi-agent tmux teams. Includes team templates, tm-send communication tool, and workflow documentation.

### Component 2: Memory System
MCP server + Qdrant vector database + Memory skills + Memory subagent + Automatic hooks. Persistent memory shared across all projects.

**What it does**:
- Technical memory: Bug solutions stored in vector DB
- Procedural memory: Process improvements by Scrum Master
- Cross-project learning: Knowledge persists across all your projects

### Component 3: Web UI
Next.js + FastAPI web application for visual team management, monitoring, and voice input.

**Features**:
- SQLite demo mode (default, no PostgreSQL required)
- Demo credentials: test@example.com / test123
- Voice input integration

---

## Installation Instructions for Claude Code

**See**: [docs/README/INSTALLATION-FOR-CLAUDE-CODE.md](./docs/README/INSTALLATION-FOR-CLAUDE-CODE.md)

This file contains detailed step-by-step instructions designed for Claude Code to read and execute. Includes installation for all three components.

---

## License

MIT (TBD)

---

## Author

**Hung Son**

**Contact**: [TBD]

---

**Last Updated**: 2026-01-20
