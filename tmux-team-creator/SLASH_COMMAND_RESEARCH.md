# Research: Claude Code Slash Commands

**Date**: 2026-01-20 21:58
**Task**: Create /create-tmux-team slash command

---

## Research Findings

### What is a Claude Code Slash Command?

A slash command is a markdown file that Claude Code executes when invoked with `/command-name`.

**Key characteristics:**
- Markdown files stored in `~/.claude/commands/` (personal) or `.claude/commands/` (project)
- Invoked with `/command-name [arguments]`
- Can accept dynamic arguments (`$ARGUMENTS`, `$1`, `$2`)
- Can reference files with `@syntax`
- Can execute bash with `!`git command`` syntax
- Optional YAML frontmatter for metadata

### Command Structure

```markdown
---
description: Brief description (shown in /help, <60 chars)
argument-hint: [arg1] [arg2]
allowed-tools: Read, Write, Bash(git:*)
model: sonnet|opus|haiku
---

Prompt body with instructions for Claude.

Use $ARGUMENTS for all args, or $1, $2 for positional args.
Use @file.ts to reference files.
Use !`git status` to execute bash (requires allowed-tools).
```

### Examples Found

1. **`/create-team`** - Creates tmux team using tmux-team-creator skill
   - Uses frontmatter with `description` and `argument-hint`
   - Uses `$1`, `$2`, `$3` for team-name, roles, notes
   - Invokes skill directly

2. **`/discuss`** - Quick discussion command
   - No frontmatter
   - Uses `$ARGUMENTS` for all input
   - Simple, focused prompt

3. **`/init-role`** - Initialize agent role in team
   - No frontmatter
   - Uses `$ARGUMENTS` for role name
   - References team files at `docs/tmux/[team-name]/`

### Installation

Commands are installed by copying to `~/.claude/commands/`:
```bash
cp command.md ~/.claude/commands/
```

---

## Implementation Plan: /create-tmux-team

### Requirements Analysis

**Must do:**
1. Check if current project has existing tmux team
2. If NO team: Use tmux-team-creator skill to create team
3. After creation: Run setup-team.sh automatically
4. Package into tmux-team-creator/ directory
5. Install script must install command

### Design

**File**: `tmux-team-creator/commands/create-tmux-team.md`

**Frontmatter:**
```yaml
---
description: Create and start tmux team for current project
argument-hint: [optional-team-name]
allowed-tools: Read, Glob, Bash
model: sonnet
---
```

**Logic flow:**
1. **Check for existing team** (using Glob tool)
   - Look for `docs/tmux/*/workflow.md`
   - If found: Error "Team already exists at docs/tmux/[name]"

2. **Use tmux-team-creator skill**
   - Invoke with team name ($1 if provided, or auto-detect from project)
   - Skill creates team structure in `docs/tmux/[name]/`

3. **Auto-run setup script**
   - After team created, find `docs/tmux/[name]/setup-team.sh`
   - Execute with Bash: `bash docs/tmux/[name]/setup-team.sh`
   - This starts the tmux session

**Arguments:**
- `$1` (optional): Team name
- If no arg: Auto-detect from project directory name

### Implementation Steps

**Step 1: Create command file**
- Create `tmux-team-creator/commands/create-tmux-team.md`
- Implement detection logic
- Implement skill invocation
- Implement auto-run setup

**Step 2: Update install script**
- Modify `install-tmux-skill.sh`
- Add section to install command:
  ```bash
  # Install command
  cp commands/create-tmux-team.md ~/.claude/commands/
  ```

**Step 3: Test**
- Test detection (existing team)
- Test creation (no team)
- Test auto-run (setup-team.sh)
- Test from fresh install

**Step 4: Update documentation**
- Add command to README
- Add usage examples
- Add to INSTALLATION.md

### Edge Cases

1. **Team exists**: Error message, don't overwrite
2. **No team name provided**: Use project directory name
3. **setup-team.sh fails**: Report error, don't leave partial state
4. **User interrupts**: Graceful handling

### Files to Create/Modify

**New:**
- `tmux-team-creator/commands/create-tmux-team.md`

**Modify:**
- `tmux-team-creator/install-tmux-skill.sh` (add command installation)
- `tmux-team-creator/INSTALLATION.md` (document command)
- `tmux-team-creator/README.md` (add usage example)

---

## Recommendation

**Proceed with implementation?**

This approach:
- ✅ Follows Claude Code command patterns
- ✅ Integrates with existing tmux-team-creator skill
- ✅ Automates full workflow (create + start)
- ✅ Handles edge cases (existing teams)
- ✅ Packaged and installable

**Alternative approach:**
Instead of auto-running setup-team.sh in the command, we could:
- Just create the team structure
- Instruct user to run setup-team.sh manually

**Pros of auto-run**: One-command experience (/create-tmux-team → team running)
**Cons of auto-run**: Less control, harder to debug

**Recommendation**: Auto-run setup-team.sh (better UX, aligns with "one command" goal)

---

**Ready for approval to implement.**
