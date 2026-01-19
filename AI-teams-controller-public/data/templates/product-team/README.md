# {team_name}

Complete product development team for building {project_description}.

## Two Goals

1. **Build the Product** - Complete the project successfully
2. **Perfect the Processes** - Learn from mistakes, update docs, never repeat errors

When Boss expresses frustration, PM must update this README or prompts to prevent recurrence.

## Common Mistakes (Hard-Learned Lessons)

| Mistake | Correct Approach |
|---------|------------------|
| Using `tmux send-keys` | Use `tm-send ROLE "message"` |
| Hardcoding pane IDs | Use role names (PdM, PM, SA, FS, CR, DK) |
| Coding without tests first | **MUST use TDD: Write tests FIRST, then implement** |
| Skipping research phase | PdM MUST use quick-research skill before writing PRD |

*Add new lessons as discovered.*

## Quick Start

```bash
./setup-team.sh
```

## Roles

| Role | Pane | Purpose |
|------|------|---------|
| PdM | 0 | Product Manager - researches ideas, writes PRD |
| PM | 1 | Project Manager - coordinates technical work |
| SA | 2 | Solution Architect - designs architecture |
| FS | 3 | Full-Stack Engineer - implements code |
| CR | 4 | Code Reviewer - reviews code quality |
| DK | 5 | Document Keeper - maintains documentation |

**Boss** operates from outside tmux. Provides ideas to PdM.

## Communication

Use `tm-send` for all tmux messaging:
```bash
tm-send PM "PdM -> PM: PRD ready at docs/prd/feature_X.md"
tm-send FS "PM -> FS: implement feature X per ADR"
```

Role-to-pane mapping is dynamic via `@role_name` tmux option (set by `setup-team.sh`).

## Full Workflow

```
Boss -> PdM (research, PRD) -> PM <-> SA (ADR) -> FS -> CR -> merge -> DK
```

### Step by Step

1. **Boss -> PdM**: Boss provides idea/description
2. **PdM researches**: Uses quick-research skill
3. **PdM writes PRD**: Creates docs/prd/feature_X.md
4. **PdM -> PM**: Notifies PM that PRD is ready
5-7. **PM <-> SA**: Architecture discussion, ADR creation
8. **PM -> FS**: Assigns implementation with ADR reference
9-11. **FS implements**: Progressive commits
12. **FS -> PM**: Reports completion
13-14. **CR review loop**: Code review and fixes
15. **Boss approval**: Merge to main
Post. **DK syncs**: Documentation updated

## Key Principles

- **Research First** - PdM uses quick-research before writing PRD
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
├── docs/
│   └── prd/           # PRD files from PdM
└── prompts/           # Role-specific prompts
```
