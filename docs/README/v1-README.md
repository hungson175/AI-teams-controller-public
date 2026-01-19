# AI Teams Controller - Installation Package

**Status**: Work in Progress

---

## What This Is

An autonomous AI software development team system built on Claude Code. Features multi-agent coordination via tmux, persistent memory across projects, and optional web UI for team management.

---

## Package Contents

This repository contains three installable components:

### Component 1: tmux Team Creator
- **Type**: Claude Code skill/plugin
- **Purpose**: Create and manage multi-agent tmux teams
- **Location**: `./tmux-team-creator/` (TBD)
- **Installation**: Copy to `~/.claude/skills/`

### Component 2: Memory System
- **Type**: MCP server + Vector database
- **Purpose**: Persistent memory across all projects
- **Location**: `./memory-system/` (TBD)
- **Installation**: Global setup in `~/.claude/`
- **Components**:
  - MCP server (Python FastMCP)
  - Local Qdrant vector database
  - Memory skills (store/recall)

### Component 3: Web UI (Optional)
- **Type**: Full-stack web application
- **Purpose**: Control interface for tmux teams
- **Location**: `./AI-teams-controller-public/`
- **Installation**: Local deployment
- **Components**:
  - Frontend (Next.js)
  - Backend (FastAPI)
  - Note: Agents work without UI via pure tmux

---

## Installation Instructions for Claude Code

**IMPORTANT**: These instructions are designed for Claude Code to read and execute.

### Prerequisites

Check these are installed:
- Python 3.11+
- Node.js 20+
- pnpm
- tmux
- Docker (for Qdrant)
- Claude Code CLI

### Installation Steps

**Step 1: Install Component 2 - Memory System**
(Instructions TBD - will be added)

**Step 2: Install Component 1 - tmux Team Creator**
(Instructions TBD - will be added)

**Step 3: Install Component 3 - Web UI (Optional)**
(Instructions TBD - will be added)

**Step 4: Verify Installation**
(Verification steps TBD - will be added)

---

## Quick Start

(Usage examples TBD - will be added)

---

## Architecture

```
User
  ↓
Claude Code + tmux Team Creator Skill
  ↓
tmux Sessions (Multi-agent teams)
  ↓
MCP Memory Server (Global)
  ↓
Qdrant Vector DB (Local)

Optional: Web UI for team management
```

---

## For Human Users

**Installation**:
1. Clone this repository
2. Open the project directory in Claude Code
3. Let Claude Code read this README and follow the installation instructions
4. Claude Code will handle any issues during installation

**Why Claude Code?**: Installation is AI-guided. Claude Code intelligently adapts to your system and resolves issues automatically.

---

## Development Status

- [ ] Memory System MCP server
- [ ] tmux Team Creator packaging
- [ ] Installation instructions complete
- [ ] Testing on clean system
- [ ] Demo video

---

## License

(TBD)

---

## Author

Hung Son - Proof of work for AI/ML engineering positions

---

**Last Updated**: 2026-01-19
