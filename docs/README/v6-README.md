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
MCP server + Qdrant vector database + Memory skills + Memory subagent + Automatic hooks. Persistent memory shared across all projects.

**Includes**:
- 2 Claude Code skills (project-memory-store, project-memory-recall)
- Specialized memory-agent (file-access isolated for security)
- 2 automatic hooks (33% reminder, TodoWrite trigger)

**Status**: Ready to install (see Memory System section below)

### Component 3: Web UI
Next.js + FastAPI web application for visual team management, monitoring, and voice input.

**Features**:
- SQLite demo mode (default, no PostgreSQL required)
- One-command initialization
- Demo credentials included (test@example.com / test123)
- Voice input integration with default settings

**Status**: Ready to install (SQLite demo mode)

---

## Memory System

### What It Does

Persistent memory shared across **all projects**. Agents store and retrieve knowledge automatically:

- **Technical memory**: Bug solutions, error patterns, code fixes stored in Qdrant vector database
- **Procedural memory**: Process improvements embedded by Scrum Master
- **Cross-project learning**: Agent on Project A recalls solutions from Project B

Memory persists locally (not cloud). Agents get smarter over time without losing knowledge between sessions.

### Installation

**One command**:
```bash
cd memory-system
./install-memory-system.sh
```

The script installs:
- Qdrant vector database (Docker)
- Python dependencies (virtual environment)
- MCP server for Claude Code integration
- Memory skills (project-memory-store, project-memory-recall)
- Memory subagent (memory-agent, isolated from file system)
- Automatic hooks (memory_store_reminder, todowrite_memory_recall)
- Environment configuration

**Time**: 3-5 minutes

**Fully self-contained**: All components (skills, subagent, hooks) packaged in this repository. Zero external dependencies. Install once, works immediately.

**For detailed installation**, see: [memory-system/INSTALLATION.md](../memory-system/INSTALLATION.md)

### Configuration

**Voyage AI API Key** (required for embeddings):
```bash
# Add to memory-system/.env
VOYAGE_API_KEY=your-key-here
```
Get your key: https://www.voyageai.com/

**Qdrant** (auto-configured):
- Port: 16333 (non-standard to avoid conflicts)
- URL: http://localhost:16333
- Data: `memory-system/qdrant_storage/`

### Usage with Claude Code

Add MCP server to `~/.claude/mcp.json`:
```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/path/to/packaging-agent/memory-system",
      "env": {
        "PYTHONPATH": "/path/to/packaging-agent/memory-system"
      }
    }
  }
}
```

**Available MCP tools**:
- `search_memory` - Find relevant past solutions
- `store_memory` - Save new knowledge
- `get_memory` - Retrieve specific memory by ID
- `list_collections` - View memory categories

**Memory Skills** (automatic):
- `project-memory-store` - Stores lessons after task completion (hook: 33% reminder)
- `project-memory-recall` - Retrieves relevant memories before complex tasks (hook: first TodoWrite)

**Usage examples**:
```bash
# Automatic (via hooks)
# After completing task -> 33% chance hook prompts to store
# When you use TodoWrite -> auto-recalls relevant memories

# Manual invocation (if needed)
/project-memory-store
/project-memory-recall
```

**Memory Subagent**:
- Handles all memory operations (automatically spawned by skills)
- Zero file access (security isolation)
- Uses only MCP memory tools

### Troubleshooting

**Qdrant connection failed**:
```bash
# Check container
docker ps | grep qdrant

# Check logs
docker logs memory-system-qdrant

# Restart
docker restart memory-system-qdrant
```

**Voyage API errors**:
- Verify API key in `memory-system/.env`
- Check key validity at voyageai.com
- Check rate limits

**For detailed troubleshooting**, see: [memory-system/INSTALLATION.md](../memory-system/INSTALLATION.md)

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
