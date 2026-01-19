# AI Teams Controller - Autonomous Multi-Agent Development System

**Built by**: Hung Son
**Demo Video**: [Link TBD]

---

## What This Is

A production-ready autonomous AI software development system built on Claude Code. Real working multi-agent teams that coordinate via tmux, maintain persistent memory across all projects, and provide an optional web UI for team management.

**This is not a demo.** It's a system I built and use daily for real development work.

---

## Key Features

- **Self-Improving Teams**: The system learns and improves continuously. Each agent builds knowledge to debug faster when hitting bugs. The Scrum Master embeds process improvements from retrospectives, making teams more effective over time.

- **Multi-Agent Coordination**: Teams of AI agents working together via tmux sessions with natural voice commands.

- **Battle-Tested Templates**: 5 production-ready team configurations (Scrum, Lite, Game Dev, Research, Insights) ready to deploy.

---

## Installation Instructions for Claude Code

**See**: [INSTALLATION-FOR-CLAUDE.md](./INSTALLATION-FOR-CLAUDE.md)

This file contains step-by-step instructions designed for Claude Code to read and execute. Includes installation for all three components.

**Quick Start for Humans**:
1. Clone this repository
2. Open project in Claude Code
3. Ask Claude: "Install the AI Teams Controller system"
4. Claude will read the installation guide and handle everything

**Prerequisites**: Python 3.11+, Node.js 20+, pnpm, tmux, Docker, Claude Code CLI

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
- `install-tmux-skill.sh` - One-command installer (TBD - see backlog)
- Full skill readable as text for code review

**Installation command** (when script is ready):
```bash
./install-tmux-skill.sh
```

**What gets installed**:
- Skill at: `~/.claude/skills/tmux-team-creator/`
- Tool at: `~/.local/bin/tm-send`
- Ready to use: `/tmux-team-creator`

**Note**: install-tmux-skill.sh script is not yet implemented. See backlog for P0 task.

### Component 2: Memory System

**Type**: MCP server + Vector database + Skills

**What it does**:
- Persistent knowledge shared across ALL projects
- Agents learn from past mistakes globally
- Memory stored locally (not cloud)

**Installation**: TBD - will be provided by Boss

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
- **Database setup (SQLite for demo)** - Production version uses PostgreSQL, but demo uses SQLite for easier setup. Includes hardcoded demo user (test/test123).
- One-command installer

**Database Note**: This demo version uses SQLite to avoid conflicts and simplify setup. Production version (Boss's current setup) uses PostgreSQL.

---

## Technical Documentation

For those interested in technical details:

- **Memory System (B-memory)**: Blog post TBD - explains the memory architecture and implementation
- **tmux Team Establishment**: Documentation TBD - how teams are created and coordinated

---

## Project Status

- [x] Core tmux team coordination working
- [x] 5 battle-tested team templates
- [x] Voice input integration
- [x] Web UI (frontend + backend)
- [ ] Memory system packaging (in progress)
- [ ] One-command installation scripts (in backlog)
- [ ] Demo video
- [ ] Public GitHub release

---

## License

MIT (TBD)

---

## Author

**Hung Son**

**Contact**: [TBD]

---

**Last Updated**: 2026-01-19 16:35 UTC+7
