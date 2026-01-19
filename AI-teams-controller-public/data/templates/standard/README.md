# {team_name}

Multi-agent organization for building {project_description}.

## Two Goals

1. **Build the Product** - Complete the project successfully
2. **Perfect the Processes** - Learn from mistakes, update docs, never repeat errors

When Boss expresses frustration, PM must update this README or prompts to prevent recurrence.

## Common Mistakes (Hard-Learned Lessons)

| Mistake | Correct Approach |
|---------|------------------|
| Using `tmux send-keys` | Use `tm-send ROLE "message"` |
| Hardcoding pane IDs | Use role names (PM, SA, FS, CR, DK) |
| Coding without tests first | **MUST use TDD: Write tests FIRST, then implement** |

*Add new lessons as discovered.*

## Quick Start

```bash
./setup-team.sh
```

## Roles

| Role | Pane | Purpose |
|------|------|---------|
| PM | 0 | Coordinator - delegates all technical work |
| SA | 1 | Architecture design - no implementation |
| FS | 2 | Full-stack code implementation |
| CR | 3 | Code review - activated at step 9 |
| DK | 4 | Documentation sync |

**Boss** operates from outside tmux. Uses `>>>` prefix to delegate to team.

## Communication

Use `tm-send` for all tmux messaging:
```bash
tm-send FS "PM -> FS: implement feature X"
```

Role-to-pane mapping is dynamic via `@role_name` tmux option (set by `setup-team.sh`).

## Story Workflow

### Simple Fixes
PM -> FS directly -> CR review -> merge

### Complex Features (10 Steps)
1-3: PM <-> SA (architecture, ADR)
4: PM assigns to FS
5: Implementation with progressive commits
6-7: Clarification loop through PM
8: Completion report
9-10: CR review loop
Post: Boss approval -> merge -> DK sync

## Key Principles

- **TDD (Test-Driven Development)** - Write tests FIRST, then implement
- **Progressive development** - small deployable steps
- **App works after every story** - no broken states
- **PM is communication hub** - no direct FS <-> SA
- **Git is truth** - commits show progress
- **Report back** - all agents update WHITEBOARD + notify PM

## Files

```
{team_name}/
├── README.md          # This file
├── WHITEBOARD.md      # Current story status
├── BACKLOG.md         # Future work
├── setup-team.sh      # Team setup script (sets @role_name on panes)
└── prompts/           # Role-specific prompts
```
