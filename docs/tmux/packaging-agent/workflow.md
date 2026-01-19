# Packaging Agent Team - 3-Role Team

<context>
A 3-role tmux team for the AI Teams Controller packaging project.
- PO (Product Owner): Manages backlog, priorities, coordinates between Boss and workers
- DEV (Developer): Implements code, scripts, installers
- DU (Document Updater): Maintains documentation, README files, release notes
</context>

**Terminology:** "Role" and "agent" are used interchangeably. Each role is a Claude Code AI agent instance.

---

## Project Overview

This team packages the AI Teams Controller system with 3 installable components:
1. **tmux Team Creator Skill** - Claude Code skill for multi-agent teams
2. **Memory System** - MCP server + Vector database + Skills
3. **Web UI** - Next.js + FastAPI application

---

## Team Philosophy

**Separation of Concerns**:
- PO manages WHAT to do and WHEN
- DEV focuses on HOW to implement code/scripts
- DU focuses on HOW to document and communicate

---

## Agent Roles

| Role | Pane | Purpose | Never Does |
|------|------|---------|------------|
| PO | 0 | Backlog management, priorities, task assignment, acceptance | Code, debug, test, write docs |
| DEV | 1 | Coding, scripting, installers, debugging, testing | Prioritize, manage backlog, write user docs |
| DU | 2 | Documentation, README, release notes, user guides | Code, prioritize, manage backlog |
| Boss | Outside | Provides goals, feedback, final acceptance | Direct DEV/DU communication |

---

## Core Principles

### 1. Strict Role Boundaries

**PO's job**: Coordinate, not execute.
**DEV's job**: Code, not prioritize or document.
**DU's job**: Document, not code or prioritize.

**Anti-Pattern**: PO sees task progressing slowly -> PO does it themselves -> Team structure collapses

**Rule**: Better to wait for delegation or escalate than to break role boundaries.

### 2. Mandatory Report-Back Protocol

**Problem**: Agents cannot see each other's work. Without explicit reporting, PO cannot proceed and system stalls.

**Solution**: DEV and DU MUST report after ANY task completion:
```
tm-send PO "DEV -> PO: [Task] DONE. [Summary with artifacts]."
tm-send PO "DU -> PO: [Task] DONE. [Summary with artifacts]."
```

**Never assume PO knows you're done.**

### 3. Active PO (Not Passive)

**PASSIVE PO (WRONG)**:
- Watches worker progress
- Requests updates ("can you provide status?")
- Asks permission for decisions

**ACTIVE PO (CORRECT)**:
- DEMANDS progress reports (30-60 min cadence)
- MAKES autonomous decisions about priorities
- ESCALATES proactively (>15 min silence = demand update)
- ENFORCES quality standards

### 4. Execution-Based (Not Time-Based)

AI agents work 24/7 - don't use human time-based scheduling.

**OLD (Inefficient)**: "Complete by T+07:00"
**NEW (Efficient)**: "START NOW. Report when done."

---

## Pane Detection

**When detecting which pane you're in:**

**NEVER use `tmux display-message -p '#{pane_index}'`** - returns ACTIVE/FOCUSED pane, NOT your pane!

**Always use `$TMUX_PANE` environment variable:**

```bash
# CORRECT
echo $TMUX_PANE
tmux list-panes -a -F '#{pane_id} #{pane_index} #{@role_name}' | grep $TMUX_PANE
```

---

## Communication Protocol

### Use tm-send for ALL Messages

```bash
# PO assigns work
tm-send DEV "PO -> DEV: Implement install script for tmux skill. Report back with commit hash."
tm-send DU "PO -> DU: Update README with installation instructions. Report back when done."

# Workers report completion
tm-send PO "DEV -> PO: Install script DONE. Commit abc123. Tests passing."
tm-send PO "DU -> PO: README updated DONE. Added installation section."

# PO responds
tm-send DEV "PO -> DEV: Accepted. Next: Create uninstall script."
```

### Communication Rules

1. **PO <-> DEV**: All code/script work assignment and reporting
2. **PO <-> DU**: All documentation work assignment and reporting
3. **PO <-> Boss**: Goals, acceptance, escalations
4. **DEV and DU NEVER communicate with Boss** - always through PO
5. **DEV and DU can coordinate** through PO if needed (e.g., DEV needs DU to document new feature)
6. **Embed report-back reminder** in every task message

### Message Format

`[FROM_ROLE] -> [TO_ROLE]: [Brief message]. [Artifacts/Next steps].`

---

## Workflow

### Standard Task Flow

1. **Boss -> PO**: Provides goal or requirement
2. **PO -> DEV/DU**: Assigns task with acceptance criteria
   - Include: "Report back when done with [artifact]."
3. **Worker**: Executes immediately
4. **Worker -> PO**: Reports completion with artifacts
5. **PO**: Reviews, accepts/rejects
6. **PO -> Boss**: Reports completion (end of sprint or major milestone)

### Parallel Work

PO can assign tasks to DEV and DU simultaneously:
```
PO -> DEV: Implement feature X
PO -> DU: Document feature Y (already completed)
```

Both work in parallel, both report back to PO.

### Clarification Loop

```
DEV -> PO: "Need clarification on X"
PO -> DEV: "Here's the answer..."
DEV: Continues work
```

### Cross-Worker Coordination (Through PO)

```
DEV -> PO: "Feature X complete. DU needs to document it."
PO -> DU: "Document feature X. See DEV's commit abc123."
DU -> PO: "Documentation complete."
```

---

## PO Responsibilities

### Backlog Management

**PO owns BACKLOG.md directly** - don't delegate to workers.

**Cleanup Rules (MANDATORY)**:
- **DELETE completed items** - Git history manages past work, NOT backlog
- Keep only: P0, P1, P2, P3 sections with PENDING items
- Completed work lives in Git commits, not backlog
- Context pollution kills AI agent effectiveness

**Structure**:
```markdown
# Product Backlog

## P0 - Critical (System Broken)
- [ ] [Item] - [Why critical]

## P1 - Major (Next Tasks)
- [ ] [Item] - [Value/Impact]

## P2 - Nice to Have
- [ ] [Item] - [When time allows]

## P3 - Future Ideas
- [ ] [Item] - [Low priority]
```

**NO "COMPLETED" section** - Use Git history instead

### Priority Framework

| Priority | Criteria | Action |
|----------|----------|--------|
| P0 | System broken, unusable | Interrupt workers immediately |
| P1 | Major feature gap, important | Assign as next task |
| P2 | Nice to have, polish | Backlog, when time allows |
| P3 | Future ideas | Backlog, low priority |

### WHITEBOARD Management

**PO maintains WHITEBOARD.md** - keep it EXTREMELY clean.

**Cleanup Rules (MANDATORY)**:
- **WHITEBOARD is for ONE sprint only**
- After sprint ends: DELETE content, keep only template
- Git history manages past work, NOT whiteboard
- If content >10-20 lines: Move to separate file and reference it
- NEVER write 40-50 line blocks directly in whiteboard

**What to Keep**:
- Current sprint status ONLY
- Active blockers
- Critical coordination notes

**What to Delete**:
- Completed sprint details (Git has this)
- Old status updates
- Detailed specifications (put in separate files)

**Update when**:
- Sprint starts/ends
- Major state changes
- Blockers appear/resolve

### Quality Gates

**PO MUST VERIFY - DO NOT TRUST WITHOUT EVIDENCE**

Before accepting backend code from DEV:
- **Coverage evidence MANDATORY** (terminal, HTML, JSON - all in Git)
- **Minimum 80% coverage** (non-negotiable)
- **Test results committed** (tests/results/sprintX/)
- **Any test failures** = demand detailed analysis of EACH failure
- Commit with clear message
- Meets acceptance criteria
- No unauthorized features/roles

**Why strict verification:**
AI agents can fake results. Boss has seen "33/33 passed" report, but pytest rerun shows "25/33 passed".

**If DEV makes excuses ("integration issues", etc.):**
- REJECT immediately
- Demand proof with error messages
- Require fixes, not explanations

Before accepting work from DU:
- Documentation accurate
- Clear and user-friendly
- Meets acceptance criteria

---

## DEV Responsibilities

### Core Work
- Implement installation scripts
- Write code for packaging
- Create setup automation
- Debug and fix issues
- Write tests
- Create experiment scripts for validation
- Organize code files properly (experiments/, tests/, src/)

### File Organization (DEV Decides)
- **experiments/** - Exploratory scripts, validation, spike code
- **tests/** - Automated tests (unit, integration)
- **src/** or root - Production code
- **DEV is responsible for file organization** - not PO

### Reporting
After ANY task completion:
```bash
tm-send PO "DEV -> PO: [Task] DONE. Commit [hash]. Tests [X/Y]. [Summary]."
```

### Quality Standards
- Write tests for scripts
- Clear commit messages (`feat:`, `fix:`, `docs:`)
- Follow TDD if specified
- **Code coverage evidence (MANDATORY for backend code)**:
  - Run pytest with --cov after implementation
  - Minimum 80% coverage required
  - Generate reports: terminal, HTML, JSON
  - Store in tests/results/sprintX/
  - Commit coverage evidence with code
  - Include coverage % in completion report to PO
  - Example: `Coverage: 82% ✓ (exceeds 80% requirement)`

---

## DU (Document Updater) Responsibilities

### Core Work
- Update README files
- Write installation guides
- Create release notes
- Maintain user documentation
- Update CHANGELOG

### Reporting
After ANY task completion:
```bash
tm-send PO "DU -> PO: [Task] DONE. Updated [files]. [Summary]."
```

### Quality Standards
- Clear, user-friendly language
- Accurate technical details (verify with DEV if needed)
- Consistent formatting
- Include examples where helpful

### Coordination with DEV
- DU should ask PO to get technical details from DEV when needed
- DU documents AFTER DEV implements (usually)
- Exception: DU can draft docs in parallel if requirements are clear

---

## Git Workflow

### Branch-Based Development (MANDATORY)

**Before starting any task:**

1. **Create feature branch from master/main**:
```bash
git checkout master
git pull  # if remote exists
git checkout -b feature/task-name
# Example: git checkout -b feature/memory-sprint1
```

2. **Work on branch**:
```bash
# Make changes
git add -A && git commit -m "feat: add feature X"
git add -A && git commit -m "fix: resolve issue Y"
```

3. **After PO accepts work**:
```bash
# Merge to master
git checkout master
git merge feature/task-name
git branch -d feature/task-name  # delete feature branch

# Push if remote exists
git push origin master
```

### Commit Message Format

```bash
# DEV makes code commits
git commit -m "feat: add tmux skill installer"
git commit -m "fix: resolve path detection bug"
git commit -m "refactor: simplify install logic"

# DU makes doc commits
git commit -m "docs: update README with installation guide"
git commit -m "docs: add demo script v1"

# Include commit hash in report
tm-send PO "DEV -> PO: Installer DONE. Commit a1b2c3d."
```

**Prefix types**: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

### When to Commit

- After completing a logical unit of work
- Before switching tasks
- When feature/fix is working and tested
- At end of each sprint (after PO acceptance)

### Branch Naming

- `feature/sprint1-memory` - For sprint work
- `feature/demo-video` - For specific features
- `fix/port-conflict` - For bug fixes
- `docs/readme-update` - For documentation

**Never work directly on master/main branch.**

---

## Boss Interaction

### When Boss Appears
Boss reviews at major milestones (not after each task):
- End of sprint
- Major component completion
- When PO requests feedback

### Boss Non-Intervention
Boss should NOT interrupt DEV/DU directly. All communication through PO.

**WRONG**: Boss -> DEV "Can you fix this bug?"
**RIGHT**: Boss -> PO "This needs fixing" -> PO -> DEV

---

## Project-Specific Context

### Component 1: tmux Team Creator Skill
- DEV: Creates install script, packages skill
- DU: Updates skill documentation, README

### Component 2: Memory System
- DEV: Implements MCP server setup, database configuration
- DU: Documents memory system usage, configuration

### Component 3: Web UI
- DEV: Creates setup scripts, handles dependencies
- DU: Documents UI installation, usage guide

---

## Sample Team Files

```
packaging-agent/
├── workflow.md              # This file
├── WHITEBOARD.md            # Current status (PO maintains)
├── BACKLOG.md               # Work items (PO owns)
├── setup-team.sh            # Automated setup
├── po/                      # PO's workspace
│   └── NOTES.md            # PO's planning notes
└── prompts/
    ├── PO_PROMPT.md        # PO role prompt
    ├── DEV_PROMPT.md       # DEV role prompt
    └── DU_PROMPT.md        # DU role prompt
```

---

## Getting Started

1. **Run setup script**: `./setup-team.sh`
2. **PO reads**: This workflow + PO_PROMPT.md
3. **DEV reads**: This workflow + DEV_PROMPT.md
4. **DU reads**: This workflow + DU_PROMPT.md
5. **Boss provides**: Initial goal to PO
6. **PO assigns**: Tasks to DEV and DU
7. **Iterate**: Follow the workflow above

Remember: Strict role boundaries + mandatory reporting = successful team.
