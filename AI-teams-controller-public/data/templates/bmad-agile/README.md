# {team_name}

BMAD Agile development team for building {project_description}.

Based on [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) workflow with tmux communication.

## Two Goals

1. **Build the Product** - Complete the project successfully
2. **Perfect the Processes** - Learn from mistakes, update docs, never repeat errors

When Boss expresses frustration, PM must update this README or prompts to prevent recurrence.

## Common Mistakes (Hard-Learned Lessons)

| Mistake | Correct Approach |
|---------|------------------|
| Using `tmux send-keys` | Use `tm-send ROLE "message"` |
| Hardcoding pane IDs | Use role names (AN, PM, SA, SM, FS, CR, DK) |
| Coding without tests first | **MUST use TDD: Write tests FIRST, then implement** |
| Implementing outside story scope | Story file is SINGLE SOURCE OF TRUTH |
| Skipping research phase | AN MUST use quick-research skill |

*Add new lessons as discovered.*

## Quick Start

```bash
./setup-team.sh
```

## Roles (7 Agents)

| Role | Pane | Phase | Purpose |
|------|------|-------|---------|
| PM | 0 | ALL | **COORDINATOR** - Receives ideas, creates PRD, manages workflow |
| AN | 1 | Analysis | Researches ideas, creates product brief |
| SA | 2 | Solutioning | Designs architecture |
| SM | 3 | Solutioning | Creates epics and stories |
| FS | 4 | Implementation | Implements with TDD |
| CR | 5 | Implementation | Reviews code quality |
| DK | 6 | Post | Syncs documentation |

**Boss** operates from outside tmux. **Always talks to PM first.** PM delegates to team.

## 4-Phase BMAD Workflow

**Phases 1-3: LINEAR (one-time)** | **Phase 4: ITERATIVE (cycles)**

### Phase 1: Analysis (AN) - ONE TIME
```
Boss -> PM (idea) -> PM delegates to AN -> quick-research -> Product Brief -> PM
```

### Phase 2: Planning (PM) - ONE TIME
```
PM (brief) -> PRD -> SA
```

### Phase 3: Solutioning (SA, SM) - ONE TIME
```
SA (PRD) -> Architecture -> SM -> Epics/Stories
```

### Phase 4: Implementation (FS, CR) - **ITERATIVE LOOP**
```
┌─────────────────────────────────────────────────────────────┐
│  FOR EACH EPIC:                                              │
│    FOR EACH STORY:                                           │
│      ┌──────────────────────────────────────────────────┐   │
│      │  SM assigns story -> FS implements (TDD)          │   │
│      │       ↓                                           │   │
│      │  CR reviews (adversarial - finds issues)          │   │
│      │       ↓                                           │   │
│      │  [If issues] -> FS fixes -> CR re-reviews         │   │
│      │       ↓ (loop until passes)                       │   │
│      │  Story DONE                                       │   │
│      └──────────────────────────────────────────────────┘   │
│    RETROSPECTIVE -> learnings feed into next epic           │
└─────────────────────────────────────────────────────────────┘
```

**Key iteration points:**
- Story loops: implement → review → fix → re-review (until pass)
- Epic cycles: stories → retrospective → next epic
- Retrospective learnings improve future work

## Communication

Use `tm-send` for all tmux messaging:
```bash
tm-send PM "AN -> PM: Product brief ready at docs/product-brief.md"
```

Role-to-pane mapping is dynamic via `@role_name` tmux option (set by `setup-team.sh`).

## Key Principles (from BMAD)

- **Story file is SINGLE SOURCE OF TRUTH** - tasks sequence is authoritative
- **Red-Green-Refactor cycle** - write failing test, make it pass, improve
- **Never implement anything not in story** - no scope creep
- **All tests must pass 100%** before story complete
- **Progressive development** - small deployable steps
- **Report back** - all agents update WHITEBOARD + notify PM

## Files

```
{team_name}/
├── README.md              # This file
├── WHITEBOARD.md          # Current status
├── BACKLOG.md             # Future work
├── setup-team.sh          # Team setup script (sets @role_name on panes)
├── docs/
│   ├── product-brief.md   # From AN (Phase 1)
│   ├── prd.md             # From PM (Phase 2)
│   ├── architecture.md    # From SA (Phase 3)
│   ├── epics/             # From SM (Phase 3)
│   ├── stories/           # From SM (Phase 3)
│   ├── adrs/              # Architecture decisions
│   └── generated-docs/    # From DK (Post)
└── prompts/               # Role-specific prompts
```
