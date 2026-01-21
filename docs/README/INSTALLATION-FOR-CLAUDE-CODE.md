# Installation Guide for Claude Code

**IMPORTANT**: This file is designed for Claude Code to read and execute, not primarily for humans.

---

## Prerequisites Check

Before proceeding, verify these are installed:

```bash
python --version   # Should be 3.11+
node --version     # Should be 20+
pnpm --version
tmux -V
docker --version
claude --version   # Claude Code CLI
```

If any are missing, install them before continuing.

---

## Installation Steps

### Step 1: Install Component 1 - tmux Team Creator Skill

**What this does**: Installs Claude Code skill for creating multi-agent tmux teams

**Files involved**:
- `tmux-team-creator.skill` - Packaged skill (ZIP)
- `tm-send` - Critical communication tool
- `install-tmux-skill.sh` - Installer script

**Installation**:

```bash
cd packaging-agent/
./install-tmux-skill.sh
```

**What gets installed**:
- Skill directory: `~/.claude/skills/tmux-team-creator/`
- tm-send tool: `~/.local/bin/tm-send`

**Verification**:
```bash
ls ~/.claude/skills/tmux-team-creator/
which tm-send
```

Expected: Both paths exist

**If installation fails**:
- Check permissions: `chmod +x install-tmux-skill.sh`
- Manually create directories: `mkdir -p ~/.claude/skills ~/.local/bin`
- Check tm-send is executable: `chmod +x ~/.local/bin/tm-send`

---

### Step 2: Install Component 2 - Memory System

**Status**: TBD (implementation in progress)

**What will be installed**:
- MCP memory server (Python FastMCP)
- Local Qdrant vector database (Docker)
- Memory skills (coder-memory-store, coder-memory-recall)

**Installation** (when ready):
```bash
cd packaging-agent/memory-system/
./install-memory-system.sh
```

**This section will be completed when memory system packaging is ready.**

---

### Step 3: Install Component 3 - Web UI

**Status**: TBD (implementation in progress)

**What this does**: Installs full-stack web application for managing tmux teams

**Files involved**:
- Frontend: Next.js application
- Backend: FastAPI application
- Database: SQLite (demo mode) or PostgreSQL

**Installation** (when ready):
```bash
cd packaging-agent/AI-teams-controller-public/
./install-web-ui.sh
```

**Services started**:
- Frontend: http://localhost:3334
- Backend: http://localhost:17061
- Database: SQLite (default) or PostgreSQL on localhost:5432

**Voice Input Setup (Optional)**:

⚠️ **IMPORTANT**: If you want to use voice input features, you MUST provide your own xAI API key.

**How to set up**:
1. Get your xAI API key from https://console.x.ai/
2. Set environment variable in Web UI backend:
   ```bash
   # Add to backend/.env file:
   XAI_API_KEY=your-xai-api-key-here
   ```
3. Restart the backend service

**Why?**: The previously embedded API key was revoked for security reasons. Voice input requires xAI's Grok model for speech-to-text processing.

**This section will be completed when web UI installation script is ready.**

---

### Step 4: Verify Installation

**After all components installed, verify**:

**Test 1: tmux Team Creator Skill**
```bash
# In Claude Code, try:
# "Create a lite tmux team for my project"
# OR use slash command:
# /tmux-team-creator
```

Expected: Skill activates, prompts for team configuration

**Test 2: Memory System**
(TBD when memory system is installed)

**Test 3: Web UI**
(TBD when web UI is installed)

---

## Troubleshooting

### Issue: tm-send not found

**Solution**:
```bash
ls ~/.local/bin/tm-send
# If missing:
cp packaging-agent/tm-send ~/.local/bin/
chmod +x ~/.local/bin/tm-send
```

### Issue: Skill not appearing in Claude Code

**Solution**:
```bash
# Verify skill location
ls ~/.claude/skills/tmux-team-creator/SKILL.md
# If missing, reinstall:
./install-tmux-skill.sh
```

### Issue: Permission denied

**Solution**:
```bash
chmod +x install-tmux-skill.sh
chmod +x ~/.local/bin/tm-send
```

---

## Post-Installation

**After successful installation**:

1. **Test tmux team creation**: Ask Claude to create a team
2. **Review sample teams**: Explore `~/.claude/skills/tmux-team-creator/sample_team/`
3. **Customize**: Adapt team templates for your needs

---

## Notes for Claude Code

- If any step fails, diagnose the issue and retry
- Check file permissions if seeing "permission denied"
- Verify prerequisites before each component
- Provide clear error messages to user if blocking issues
- Adapt installation to user's specific system setup

---

**Last Updated**: 2026-01-19 16:20 UTC+7
