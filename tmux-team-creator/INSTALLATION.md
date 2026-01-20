# tmux Team Creator - Installation Guide

## Installation

**One command**:
```bash
./install-tmux-skill.sh
```

Professional installer with automated checks:
- Prerequisites verification (unzip, bash, tmux)
- Intelligent installation (creates or updates skill)
- Post-installation verification (3 automated checks)

**Time**: 30 seconds

---

## Prerequisites

**Required**:
- **unzip** - Extract skill archive
- **bash 4.0+** - Shell environment
- **tmux** - Terminal multiplexer

**Check prerequisites**:
```bash
# Verify unzip
unzip -v

# Verify bash version
bash --version

# Verify tmux
tmux -V
```

---

## Installation Verification

The installer runs 3 automated checks:

1. **Skill directory** - Verifies `~/.claude/skills/tmux-team-creator/` exists
2. **tm-send tool** - Verifies `~/.local/bin/tm-send` is executable
3. **Skill accessibility** - Confirms skill is ready to use

All checks must pass for successful installation.

---

## Next Steps

**Use the skill**:
```bash
# In Claude Code
/tmux-team-creator
```

**5 team templates available**:
- Scrum (6 roles: PO, SM, TL, BE, FE, QA)
- Lite (2 roles: PO, WORKER)
- Game Dev (6 roles: PO, SM, GD, TL, DEV, QA)
- Research (6 roles: VI, CS, RS, IR, BE, FE, QA)
- Insights (6 roles: EM, RL, PR, SR, DA, QR)

Claude will guide you through team creation and configuration.

---

## Troubleshooting

**"unzip not found"**:
```bash
# Ubuntu/Debian
sudo apt-get install unzip

# macOS
brew install unzip
```

**"tmux not found"**:
```bash
# Ubuntu/Debian
sudo apt-get install tmux

# macOS
brew install tmux
```

**"Installation failed"**:
- Check prerequisites are installed
- Verify you have write access to `~/.claude/` and `~/.local/bin/`
- Run installer with verbose output: `bash -x install-tmux-skill.sh`

---

## Uninstallation

```bash
# Remove skill
rm -rf ~/.claude/skills/tmux-team-creator/

# Remove tool
rm ~/.local/bin/tm-send
```

---

**Installation Time**: 30 seconds
**Disk Space**: ~200KB
