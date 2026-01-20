---
description: Create and start tmux team for current project
argument-hint: [optional-team-name]
allowed-tools: Read, Glob, Bash
model: sonnet
---

# Create Tmux Team for Current Project

You are creating a multi-agent tmux team for the current project using the **tmux-team-creator** skill.

## Step 1: Check for Existing Team

First, check if this project already has a tmux team:

Use the Glob tool to search for team workflow files:
```
Pattern: "docs/tmux/*/workflow.md"
```

**If team exists**:
- Report: "Team already exists at docs/tmux/[name]/"
- STOP - Do not create duplicate team

**If NO team found**: Proceed to Step 2

## Step 2: Determine Team Name

Team name: $1

**If no argument provided ($1 is empty)**:
- Use current project directory name
- Example: If in `/home/user/my-project/`, team name is `my-project`

## Step 3: Invoke tmux-team-creator Skill

Use the **tmux-team-creator** skill to create the team:

**Pass to skill**:
- Team name: [determined in Step 2]
- Project directory: Current working directory
- Follow full skill workflow (template selection, customization, file creation)

**Important**: The skill will ask which template to use. Guide the user through template selection.

## Step 4: Auto-Run Setup Script

After the tmux-team-creator skill completes and team structure is created:

1. **Locate setup script**:
   - Path: `docs/tmux/[team-name]/setup-team.sh`

2. **Verify script exists**:
   - Use Read tool to check if file exists
   - If NOT found: Report error "Setup script not found at expected location"

3. **Execute setup script**:
   - Use Bash tool: `bash docs/tmux/[team-name]/setup-team.sh`
   - This will:
     - Create tmux session
     - Set up all panes with correct roles
     - Initialize team

4. **Report completion**:
   ```
   ✓ Team created: docs/tmux/[team-name]/
   ✓ Tmux session started: [team-name]

   Next steps:
   1. Attach to session: tmux attach -t [team-name]
   2. Each agent should run: /init-role [ROLE_NAME]
   3. Check WHITEBOARD: docs/tmux/[team-name]/WHITEBOARD.md
   ```

## Error Handling

**If team already exists**: Stop with clear message

**If skill fails**: Report error, do not attempt setup script

**If setup script fails**: Report error with output, team structure remains (user can manually run setup-team.sh)

**If tmux not installed**: Report error "tmux is required. Install with: sudo apt install tmux"

## Usage Examples

```bash
# Auto-detect team name from project directory
/create-tmux-team

# Specify team name
/create-tmux-team my-api-project
```

---

**This command provides ONE-COMMAND team creation**: Check → Create → Start → Ready
