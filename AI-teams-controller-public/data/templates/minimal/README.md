# {team_name}

Minimal 2-agent team for building {project_description}.

## Two Goals

1. **Build the Product** - Complete the project successfully
2. **Perfect the Processes** - Learn from mistakes, update docs, never repeat errors

When Boss expresses frustration, PM must update this README or prompts to prevent recurrence.

## Common Mistakes (Hard-Learned Lessons)

| Mistake | Correct Approach |
|---------|------------------|
| Using `tmux send-keys` | Use `tm-send ROLE "message"` |
| Hardcoding pane IDs | Use role names (PM, CODER) |
| Coding without tests first | **MUST use TDD: Write tests FIRST, then implement** |

*Add new lessons as discovered.*

## Quick Start

```bash
./setup-team.sh
```

## Roles

| Role  | Pane | Purpose |
|-------|------|---------|
| PM    | 0    | Coordinator - delegates all work |
| CODER | 1    | Full-stack implementation |

**Boss** operates from outside tmux. Delegates to PM.

## Communication

Use `tm-send` for all tmux messaging:
```bash
tm-send CODER "PM -> CODER: implement feature X"
```

Role-to-pane mapping is dynamic via `@role_name` tmux option (set by `setup-team.sh`).

## Workflow

PM -> CODER -> (PM verify) -> merge

## Key Principles

- **TDD (Test-Driven Development)** - Write tests FIRST, then implement
- **Progressive development** - small deployable steps
- **App works after every commit** - no broken states
- **Git is truth** - commits show progress
- **Report back** - all agents update WHITEBOARD + notify PM

## Files

```
{team_name}/
├── README.md          # This file
├── WHITEBOARD.md      # Current task status
├── setup-team.sh      # Team setup script (sets @role_name on panes)
└── prompts/           # Role-specific prompts
```
