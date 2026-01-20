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
- **Persistent Memory**: Global memory system shared across all projects
- **Battle-Tested Templates**: 5 pre-built team templates (Scrum, Lite, Game Dev, Research, Insights)
- **Voice Input Support**: Natural voice commands to AI teams
- **Web UI**: Visual control interface (optional - agents work via pure tmux too)
- **Self-Improving**: Memory system allows agents to learn from past mistakes

---

## Quick Start for Humans

**Prerequisites**: Python 3.11+, Node.js 20+, pnpm, tmux, Docker, Claude Code CLI

**Installation**:
1. Clone this repository
2. Open project in Claude Code
3. Ask Claude: "Install the AI Teams Controller system"
4. Claude will read the installation guide and handle everything

**Why Claude Code handles installation?** AI-guided setup adapts to your system and resolves issues automatically. Better than rigid bash scripts.

**For detailed installation instructions**, see: [INSTALLATION.md](./INSTALLATION.md)

---

## Architecture

```
User/Voice Input
  ↓
Claude Code + tmux Team Creator Skill
  ↓
tmux Sessions (Multi-agent teams)
  ↓
MCP Memory Server (Global)
  ↓
Qdrant Vector DB (Local)

Optional: Web UI for visual team management
```

---

## Package Contents

This repository contains three installable components:

### Component 1: tmux Team Creator Skill

**Type**: Claude Code skill (extends Claude's capabilities)

**What it does**:
- Creates and manages multi-agent tmux teams
- Provides 5 battle-tested team templates
- Handles inter-agent communication via tm-send tool
- Includes workflow documentation and role prompts

**Installation**: One-command install script

**Package includes**:
- `tmux-team-creator.skill` - Packaged skill (ZIP archive)
- `tm-send` - Critical communication tool
- `install-tmux-skill.sh` - One-command installer
- Full skill readable as text for code review

**Installation command**:
```bash
./install-tmux-skill.sh
```

**What gets installed**:
- Skill at: `~/.claude/skills/tmux-team-creator/`
- Tool at: `~/.local/bin/tm-send`
- Ready to use: `/tmux-team-creator`

### Component 2: Memory System

**Type**: MCP server + Vector database + Claude Code Skills

**What it does**:
- Persistent memory shared across ALL projects
- Agents learn from past mistakes globally
- Memory stored locally (not cloud)
- Automatic pattern storage and retrieval

**Includes**:
- MCP server (Python FastMCP) for memory operations
- Local Qdrant vector database (Docker) for vector storage
- **2 Claude Code skills** (critical for functionality):
  - `coder-memory-store` - Stores lessons and patterns after task completion
  - `coder-memory-recall` - Retrieves relevant knowledge before complex tasks
- One-command installer

**Installation**: TBD
- Skills are being rebuilt from scratch for optimal performance
- Full installation instructions will be provided with Component 2 package
- Will include automated skill installation

**Status**: Implementation in progress

### Component 3: Web UI

**Type**: Full-stack web application (Next.js + FastAPI)

**What it does**:
- Visual interface for managing tmux teams
- Monitor agent activity in real-time
- Voice input integration
- Control interface for team operations

**Location**: `./AI-teams-controller-public/`

**Demo Mode**: SQLite database with pre-configured test user (no external database setup required)

**Demo Credentials**:
```
Email: test@example.com
Password: test123
```

**Note**: Agents work without UI via pure tmux (for lightweight use), but UI is core feature for demonstration and control.

**Installation**: TBD - will include:
- Frontend setup (Next.js + pnpm)
- Backend setup (FastAPI + Python 3.11+)
- Database setup (SQLite for demo, PostgreSQL for production)
- Demo user auto-created during installation
- One-command installer

---

## Technical Highlights

**Novel architecture**: Multi-agent coordination via tmux (not API orchestration)

**Key technologies**:
- Claude Code skill system (modular, reusable)
- MCP (Model Context Protocol) for memory
- tmux for agent isolation and communication
- Vector DB (Qdrant) for semantic memory
- FastAPI + Next.js for modern web stack

**Production-ready**:
- Battle-tested templates
- Real-world usage and error handling
- Voice integration for natural commands
- Persistent memory for continuous improvement

---

## Project Status

- [x] Core tmux team coordination working
- [x] 5 battle-tested team templates
- [x] Voice input integration
- [x] Web UI (frontend + backend)
- [ ] Memory system packaging (in progress)
- [ ] One-command installation scripts
- [ ] Demo video
- [ ] Public GitHub release

---

## Installation Instructions for Claude Code

**See**: [INSTALLATION.md](./INSTALLATION.md)

This file contains detailed step-by-step instructions designed for Claude Code to read and execute. Includes installation for all three components.

---

## License

MIT (TBD)

---

## Author

**Hung Son**

**Contact**: [TBD]

---

**Last Updated**: 2026-01-19 16:25 UTC+7
