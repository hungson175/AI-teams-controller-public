# AI Teams Controller - Autonomous Multi-Agent Development System

**Built by**: Hung Son
**Purpose**: Autonomous multi-agent development system for public use
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
- Full skill readable as text (for humans reviewing code)

**Installation command**:
```bash
./install-tmux-skill.sh
```

**What gets installed**:
- Skill at: `~/.claude/skills/tmux-team-creator/`
- Tool at: `~/.local/bin/tm-send`
- Ready to use: `/tmux-team-creator`

### Component 2: Memory System

**Type**: MCP server + Vector database + Skills

**What it does**:
- Persistent memory shared across ALL projects
- Agents learn from past mistakes globally
- Memory stored locally (not cloud)

**Installation**: TBD - will include:
- MCP server (Python FastMCP)
- Local Qdrant vector database (Docker)
- Memory skills (store/recall)
- One-command installer

**Status**: Implementation in progress

### Component 3: Web UI

**Type**: Full-stack web application (Next.js + FastAPI)

**What it does**:
- Visual interface for managing tmux teams
- Monitor agent activity in real-time
- Voice input integration
- Control interface for team operations

**Location**: `./AI-teams-controller-public/`

**Note**: Agents work without UI via pure tmux (for lightweight use), but UI is core feature for demonstration and control.

**Installation**: TBD - will include:
- Frontend setup (Next.js)
- Backend setup (FastAPI)
- Database setup (PostgreSQL)
- One-command installer

---

## For Hiring Managers / Technical Reviewers

**What makes this project interesting**:

1. **Real, not a demo**: I use this daily for actual development
2. **Novel architecture**: Multi-agent coordination via tmux (not API orchestration)
3. **Persistent memory**: Agents improve over time across all projects
4. **Voice integration**: Natural language commands to AI teams
5. **Production-ready**: Battle-tested templates, error handling, real-world usage

**Technical highlights**:
- Claude Code skill system (modular, reusable)
- MCP (Model Context Protocol) for memory
- tmux for agent isolation and communication
- Vector DB (Qdrant) for semantic memory
- FastAPI + Next.js for modern web stack

**Code quality**:
- All components readable as text (no obfuscation)
- Includes hooks, commands, scripts
- Real documentation (not generated boilerplate)

---

## Project Status

- [x] Core tmux team coordination working
- [x] 5 battle-tested team templates
- [x] Voice input integration
- [x] Web UI (frontend + backend)
- [ ] Memory system packaging (in progress)
- [ ] One-command installation scripts
- [ ] Demo video (45-90 seconds)
- [ ] Public GitHub release

**Target completion**: 2026-01-19 (today)

---

## Installation Instructions for Claude Code

**See**: [INSTALLATION.md](./INSTALLATION.md)

This file contains detailed step-by-step instructions designed for Claude Code to read and execute. Includes installation for all three components.

---

## License

TBD

---

## Author

**Hung Son**
AI/ML Engineer

**Contact**: [TBD]

---

**Last Updated**: 2026-01-19 16:20 UTC+7
