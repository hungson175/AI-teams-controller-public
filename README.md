# AI Teams Controller - Autonomous Multi-Agent Development System

**Built by**: Hung Son

**Demo Video**: https://www.youtube.com/watch?v=bBhs13kKtjs

**Note**: The strongest part of this system is the invisible memory - read [the design doc](./docs/memory_design_v7.md) if interested.

---

## What This Is

Autonomous AI development system built on Claude Code. Multi-agent teams coordinate via tmux, maintain persistent memory, with optional web UI.

**This is not a demo.** It's a production system I use daily.

**Target Audience**: Professional engineers with 3+ months Claude Code experience.

---

## Key Features

- **Multi-Agent Teams**: AI agents working together via tmux (Scrum, Light, McKinsey templates)
- **Self-Improving Memory**: Technical solutions in vector DB + procedural improvements
- **Voice Input**: Natural voice commands (requires your xAI API key)
- **Web UI**: Optional visual control interface

---

## Quick Start

**Prerequisites**: Python 3.11+, Node.js 20+, pnpm, tmux, Docker, Claude Code CLI

**Installation**:
1. Clone this repository
2. Open in Claude Code:
   ```bash
   claude --settings ~/.claude/settings.json --dangerously-skip-permissions
   ```
3. Ask Claude: "Read docs/README/INSTALLATION-FOR-CLAUDE-CODE.md and install the system"

**Voice Input Setup** (Optional):
If you want voice control, provide your own xAI API key. See [Installation Guide](./docs/README/INSTALLATION-FOR-CLAUDE-CODE.md) for details.

**Detailed instructions**: [docs/README/INSTALLATION-FOR-CLAUDE-CODE.md](./docs/README/INSTALLATION-FOR-CLAUDE-CODE.md)

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

**1. tmux Team Creator**: Claude Code skill for multi-agent teams

**2. Memory System**: Vector DB + MCP server for persistent learning

**3. Web UI**: Optional Next.js/FastAPI interface with voice input

---

## Troubleshooting

**"tm-send not found"**: Add `~/.local/bin` to PATH in `~/.bashrc` or `~/.zshrc`

**More help**: See [Installation Guide](./docs/README/INSTALLATION-FOR-CLAUDE-CODE.md)

---

## License

MIT (TBD)

---

## Author

**Hung Son**

**Contact**: [TBD]

---

**Last Updated**: 2026-01-20
