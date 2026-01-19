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
- **5 Team Templates**: Scrum, Lite, Game Dev, Research, Insights
- **Voice Input Support**: Natural voice commands to AI teams
- **Web UI**: Visual control interface (optional - agents work via pure tmux too)

---

## Quick Start

**Prerequisites**: Python 3.11+, Node.js 20+, pnpm, tmux, Docker, Claude Code CLI

**Installation**:
1. Clone this repository
2. Open project in Claude Code
3. Ask Claude: "Install the AI Teams Controller system"
4. Claude will read the installation guide and handle everything

**Why Claude Code handles installation?** AI-guided setup adapts to your system and resolves issues automatically. Better than rigid bash scripts.

**For detailed installation instructions**, see: [INSTALLATION-FOR-CLAUDE.md](./INSTALLATION-FOR-CLAUDE.md)

---

## What's Included

This repository contains three installable components:

### Component 1: tmux Team Creator Skill
Claude Code skill that creates and manages multi-agent tmux teams. Includes 5 templates, tm-send communication tool, and workflow documentation.

**Installation**: `./install-tmux-skill.sh` (when ready)

### Component 2: Memory System
MCP server + Qdrant vector database + 2 Claude Code skills (coder-memory-store, coder-memory-recall). Persistent memory shared across all projects.

**Status**: Implementation in progress

### Component 3: Web UI
Next.js + FastAPI web application for visual team management, monitoring, and voice input.

**Status**: TBD - installation instructions coming

---

## Installation Instructions for Claude Code

**See**: [INSTALLATION-FOR-CLAUDE.md](./INSTALLATION-FOR-CLAUDE.md)

This file contains detailed step-by-step instructions designed for Claude Code to read and execute. Includes installation for all three components.

---

## License

MIT (TBD)

---

## Author

**Hung Son**

**Contact**: [TBD]

---

**Last Updated**: 2026-01-19
