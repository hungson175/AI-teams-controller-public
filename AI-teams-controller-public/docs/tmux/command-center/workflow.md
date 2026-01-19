# AI Controller Scrum Team

**Target Audience**: AI agents (SM, PO, TL, FE, BE, QA) working in this system
**Project**: TMUX Team Controller - Web-based interface for managing AI agent teams

**Terminology:** "Role" and "agent" are used interchangeably in this documentation. Each role (PO, SM, TL, FE, BE, QA) is a Claude Code AI agent instance.

---

## System Overview

This is a **multi-agent scrum team** where each Claude Code instance takes on a specific role to collaboratively develop the AI Teams Controller application through sprint-based workflows.

### Scrum Roles (Official)

**Scrum has exactly 3 roles:**

| Role | Description | Owns |
|------|-------------|------|
| **Product Owner (PO)** | Maximizes product value, manages stakeholder expectations | **Product Backlog** |
| **Scrum Master (SM)** | Facilitates Scrum process, removes blockers, protects team | Process (facilitates, not owns) |
| **Developers** | Everyone contributing to the increment | **Sprint Backlog** |

**In this team, Developers = TL + FE + BE + QA** (all roles that deliver the increment)

### Backlog Ownership (Per Scrum Guide)

| Backlog | Owner | Location |
|---------|-------|----------|
| **Product Backlog** | PO (exclusively) | `BACKLOG.md` |
| **Sprint Backlog** | Developers (TL, FE, BE, QA) | `sprints/sprint_N/SPRINT_BACKLOG.md` |

- **PO** prioritizes WHAT to build (Product Backlog)
- **Developers** decide HOW to build it (Sprint Backlog)
- **SM** facilitates but does NOT own either backlog

**Reference**: `docs/research/2020-Scrum-Guide-US.md`

### Agent Pane Mapping

| Role | Pane | Scrum Role | Responsibility |
|------|------|------------|----------------|
| **PO** | 0 | Product Owner | Requirements from Boss, owns Product Backlog |
| **SM** | 1 | Scrum Master | Facilitates process, maintains process docs |
| **TL** | 2 | Developer | Architecture design, code review |
| **FE** | 3 | Developer | Frontend implementation (TDD) |
| **BE** | 4 | Developer | Backend implementation (TDD) |
| **QA** | 5 | Developer | Blackbox testing |
| **Boss** | Outside tmux | Stakeholder | Provides requirements via `>>>` to PO |

### Boss Terminal

The Boss (stakeholder) operates from a **separate terminal outside the tmux session**.

**Communication Protocol**:
- When Boss types `>>> [message]`, the message is sent to **PO** pane (not SM!) with prefix:
  ```
  BOSS [HH:MM]: [original_message]
  ```
- Example: Boss types `>>> add user authentication` -> PO receives `BOSS [14:30]: add user authentication`

**Why PO, not SM?** In Scrum, PO is the bridge between stakeholders and the team. PO receives requirements, prioritizes them, and defines the sprint backlog. SM facilitates the process but doesn't own requirements.

**Boss Voice Communication:**
- Boss primarily communicates via **voice** (transcription may have typos)
- All agents must **interpret context and intent**, not literal text
- Don't ask for clarification on obvious typos - understand from context
- Examples: "write panel" = "right panel", "algorism" = "algorithm", "cliquable" = "clickable"

---

## Core Principles

1. **PO owns requirements, SM facilitates** - PO receives from Boss, SM coordinates execution
2. **Sprint-based Workflow** - Work in short iterations with clear goals
3. **TDD First** - FE and BE write tests before implementation based on TL specs
4. **Git as Progress Tracker** - Commits show real progress, not chat logs
5. **Progressive Implementation** - Build incrementally (small -> medium -> full)
6. **Boss Appears After Sprint** - Team self-coordinates during sprint execution
7. **Two-Enter Rule** - Tmux messages require two SEPARATE commands
8. **App MUST Work After Every Sprint** - Each sprint ends with a working system
9. **Push to Remote After Sprint** - After Boss accepts, commit, merge to master, push to GitHub
10. **Re-read Docs Before New Epic** - All roles re-read workflow.md + their role prompt before starting new epic

---

## MANDATORY: Git Push After Sprint Accepted

**After Boss accepts a sprint, changes MUST be pushed to remote GitHub:**

```bash
# 1. Commit all changes
git add -A
git commit -m "feat: Sprint N - [Sprint Goal]"

# 2. Merge to master (if on feature branch)
git checkout master
git merge [branch]

# 3. Push to remote
git push origin master
```

**Why?** Work not pushed to remote is not saved. If local machine fails, sprint work is lost. Push immediately after acceptance.

---

## CRITICAL: Use tm-send for ALL Tmux Communication

**ALWAYS use `tm-send` command with ROLE NAMES - NEVER use raw `tmux send-keys`!**

```bash
# CORRECT - Use tm-send with ROLE NAME
tm-send SM "FE -> SM: Task complete."

# WRONG - NEVER use this
tmux send-keys -t %16 "message" C-m C-m   # FORBIDDEN!
```

### Dynamic Role Lookup via @role_name

**Role-to-pane mapping is DYNAMIC using tmux's `@role_name` pane option.**

- The `setup-team.sh` script sets `@role_name` on each pane at startup
- `tm-send` looks up panes dynamically: `tmux list-panes -F "#{pane_id} #{@role_name}"`
- **NO static file needed** - roles are resolved at runtime
- Role mapping (set by setup-team.sh):
  - PO = Pane index 0 (receives requirements from Boss)
  - SM = Pane index 1 (facilitates process)
  - TL = Pane index 2
  - FE = Pane index 3
  - BE = Pane index 4
  - QA = Pane index 5

**To verify role mapping:**
```bash
tmux list-panes -t command-center -F "#{pane_id} #{pane_index} #{@role_name}"
```

---

## CRITICAL: Correct Pane Detection (Prevent Bugs)

**THIS BUG WILL WASTE HOURS IF NOT PREVENTED!**

### The Problem

When agents need to determine their role or which pane they're in, **NEVER query without specifying the pane target** - commands without `-t $TMUX_PANE` return the **ACTIVE/FOCUSED pane** (where the user's cursor is), NOT the pane where the agent is actually running!

### Wrong vs Correct

```bash
# WRONG - Returns active cursor pane, not YOUR pane
tmux display-message -p '#{pane_index}'
tmux show-options -pv @role_name

# CORRECT - Returns YOUR actual pane using $TMUX_PANE environment variable
echo $TMUX_PANE
tmux show-options -pt $TMUX_PANE -qv @role_name
tmux list-panes -a -F '#{pane_id} #{pane_index} #{@role_name}' | grep $TMUX_PANE
```

### Why This Matters

- In multi-agent teams, each pane has a specific role (PO, SM, TL, FE, BE, QA)
- Messages must route correctly based on pane roles
- If agents misidentify their pane, they send messages to wrong agents
- This causes hours of debugging "why is PO acting like TL?"

### Where to Check

When writing scripts or hooks that need pane detection:

1. **Bash scripts:** `ROLE=$(tmux show-options -t "$TMUX_PANE" -qv @role_name)`
2. **Python scripts:**
   ```python
   tmux_pane = os.environ.get("TMUX_PANE")
   subprocess.run(["tmux", "show-options", "-pt", tmux_pane, "-qv", "@role_name"])
   ```

**The `$TMUX_PANE` environment variable is set by tmux for each pane and is the ONLY reliable way to detect which pane your code is running in.**

---

## Sprint Workflow

### Sprint Planning
1. **Boss -> PO**: Provides ideas/requirements (stakeholder input)
2. **PO**: Prioritizes and defines sprint backlog with acceptance criteria
3. **SM**: Facilitates sprint planning meeting
4. **PO -> TL**: Request technical design for sprint items
5. **TL**: Creates technical specs for FE/BE

### Sprint Execution (FE + BE with TDD)
6. **SM facilitates**: Assigns sprint work, removes blockers
7. **FE/BE**: Write tests first (TDD), then implement progressively
8. **FE/BE <-> TL**: Clarification on technical specs (SM facilitates if blocked)
9. **FE/BE -> SM**: Sprint completion report

### Sprint Review (TL + QA)
10. **TL**: Code review - reviews code quality and architecture
11. **TL -> FE/BE**: Feedback loop until code approved
12. **QA**: Blackbox testing based on TL specs and PO acceptance criteria
13. **QA**: Test results (PASS/FAIL)

### Sprint Retrospective (Two-Phase Approach)

**Phase 1: Auto-Retro (After PO Acceptance)**
14. **SM runs autonomously**: Internal retrospective (team process only)
    - Focus: Communication, TDD, code review, coordination
    - Document in `sprints/sprint_N/RETROSPECTIVE.md`
    - Action items: 0-1-2 max (prefer 0-1, NEVER force fixes)
    - Apply improvements immediately (prompt updates if needed)

**Phase 2: Post-Review Retro (Conditional)**
15. **PO -> Boss**: Sprint demo and review
16. **Boss**: Approve sprint or request changes
17. **SM evaluates**: Does Boss feedback require additional retro?
    - If YES: SM -> PO: "Request Phase 2 retro before Sprint N+1"
    - If NO: Proceed to next sprint (Phase 1 already covered learnings)
18. **PO**: Updates backlog for next sprint

**Note**: Boss does NOT participate in retrospectives (stakeholder, not team member). Boss participates in Sprint Review only.

---

## Role Boundaries (CRITICAL)

| Role | CAN DO | CANNOT DO |
|------|--------|-----------|
| **PO** | Receive requirements from Boss, define backlog, prioritize, accept/reject work | Write code, make technical decisions |
| **SM** | Facilitate process, remove blockers, protect team, run ceremonies, **coordinate ALL cross-role actions** | Write code, define requirements, prioritize backlog |
| **TL** | Design architecture, create specs, review code | Write implementation code |
| **FE** | Write frontend code with TDD, restart **frontend only** | Make architecture decisions, write backend, **restart backend**, touch backend code, communicate directly with other roles |
| **BE** | Write backend code with TDD, restart **backend only** | Make architecture decisions, write frontend, **restart frontend**, touch frontend code, communicate directly with other roles |
| **QA** | Blackbox testing, validate against specs | Write code, review code |

**PO owns the WHAT (requirements).** PO is the bridge between Boss/stakeholders and the team.
**SM owns the HOW (process).** SM facilitates but doesn't define what to build.
**TL is a DESIGNER and REVIEWER, not an implementer.**

### CRITICAL: NO Direct Role-to-Role Communication During Sprint

**ALL communication MUST go through SM:**

```
FE needs BE help:    FE -> SM -> BE
BE needs FE help:    BE -> SM -> FE
Anyone needs TL:     Role -> SM -> TL
Cross-role restarts: Role -> SM -> Other Role
```

**WHY**:
1. SM needs visibility to coordinate (cross-role restarts, dependencies, sequencing)
2. Direct communication bypasses SM, blocking coordination
3. Cross-role restarts without SM cause cascading failures

**Boss's Rule (Sprint 13):**
"All of that must go through the Scrum Master for coordination, not just generally. The frontend is only allowed to own and touch its own code and stuff. It's forbidden to touch backend stuff. Conversely, the backend is the same."

**Service Ownership:**
- FE owns frontend ONLY (code, services, port 3334)
- BE owns backend ONLY (code, services, port 17061)
- Cross-service restarts MUST coordinate through SM

---

## TDD Workflow (FE and BE)

### Test-First Development

1. **Receive specs from TL** (via SM)
2. **Write failing tests first** based on specs
3. **Implement code** to make tests pass
4. **Refactor** while keeping tests green
5. **Commit progressively** at each stage

### Test Categories

1. **Unit Tests** - Test individual functions/components
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test full user flows (if applicable)

### TDD Commands

**Frontend**:
```bash
cd frontend
pnpm test           # Run tests
pnpm test:watch     # Watch mode
pnpm lint           # Lint check
pnpm build          # Build check
```

**Backend**:
```bash
cd backend
uv run python -m pytest                    # Run tests
uv run python -m pytest --cov=app          # With coverage
```

### Code Coverage Standards

**Reference:** `docs/tmux/command-center/standards/CODE_COVERAGE_STANDARDS.md`

| Component | Minimum Coverage | Target | Why |
|-----------|------------------|--------|-----|
| **Frontend (Next.js)** | 70% | 75-80% | UI complexity, Server Components testing limitations |
| **Backend (FastAPI)** | 80% | 85-90% | Business logic criticality, deterministic API testing |

**Research-based standards** (Google, Microsoft, TDD experts):
- 70-80% is the practical sweet spot for most projects
- Diminishing returns above 80% (last 20% takes 90% of effort)
- Frontend lower due to UI testing complexity
- Backend higher due to deterministic logic testing

**TL must specify coverage targets in technical specs** for each work item.

**FE/BE must check coverage before reporting complete:**
- Frontend: `pnpm test -- --coverage`
- Backend: `uv run python -m pytest --cov=app --cov-report=term-missing`

**NOT arbitrary 100%**: Focus on meaningful behavior testing, not gaming metrics.

### MANDATORY: Regression Tests for Bug Fixes (Boss Directive)

**When fixing bugs, a regression test is REQUIRED before the fix is considered complete.**

**Protocol (Bug Fix → Test → Done):**
1. **Identify bug** - Understand root cause
2. **Write failing test** - Test that reproduces the bug
3. **Apply fix** - Make the test pass
4. **Verify existing tests pass** - No regressions
5. **Report complete** - Include test in completion report

**Why?** Without a regression test, the same bug can return in future refactoring. P0 bugs especially need test coverage to prevent recurrence.

**Example from Sprint 6 (2026-01-12):**
- P0: `fetch` binding lost in DIP refactoring → "Failed to execute 'fetch' on 'Window'"
- Fix: Arrow function wrapper
- Missing: Regression test (Boss flagged this)
- Lesson: Every bug fix deserves a test that would have caught it

**Boss Quote:** "Bug found → Fix bug → ADD TESTS. Tests must reproduce the issue and verify the fix."

---

## Project Context

### Technology Stack

**Frontend (Next.js)**:
- Next.js 16 with React 19
- TypeScript
- Tailwind CSS v4
- shadcn/ui components (Radix UI)
- Port: 3334

**Backend (FastAPI)**:
- Python 3.11+
- FastAPI with Pydantic
- Real tmux integration
- Port: 17061

**Terminal Service (Node.js)**:
- Node.js + node-pty
- WebSocket-based interactive shell
- JWT authentication via FastAPI
- Port: 17071

### Project Structure

```
AI-teams-controller/
├── frontend/          # Next.js app (port 3334)
│   ├── app/           # App router pages
│   ├── components/    # UI components
│   └── lib/           # Utilities
├── backend/           # FastAPI server (port 17061)
│   └── app/
│       ├── api/       # Route handlers
│       ├── services/  # Business logic
│       └── schemas/   # Pydantic models
└── docs/              # Documentation
    └── tmux/          # Team documentation
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/teams` | GET | List tmux sessions |
| `/api/teams/{team}/roles` | GET | List panes for session |
| `/api/send/{team}/{role}` | POST | Send message to pane |
| `/api/state/{team}/{role}` | GET | Get pane output |
| `/health` | GET | Health check |

---

## Communication Patterns

### Message Format

`[ROLE] [HH:mm]: [Brief message]. See [reference].`

Examples:
- `SM [23:11]: Sprint assigned to FE. See docs/sprints/sprint-1.md`
- `FE [22:10]: Task complete. Tests: 42/42 passing. See Git commits.`
- `TL [22:15]: Code review approved. Ready for QA.`
- `QA [22:30]: All tests PASS. Sprint complete.`

### Two-Enter Rule (CRITICAL)

Use `tm-send` which handles this automatically!

---

## Collaboration Tools

### WHITEBOARD (Sprint Status)
**Location**: `docs/tmux/command-center/WHITEBOARD.md`

**Purpose:** Real-time status dashboard for CURRENT sprint.
- Sprint goal and current status
- Team status (who's working on what)
- Blockers and issues (SM tracks)
- Clear after each sprint

### SPRINT BACKLOG
**Location**: `docs/tmux/command-center/sprints/sprint_N/SPRINT_BACKLOG.md`
**Owner**: Developers (TL, FE, BE, QA) - per Scrum Guide

**Purpose:** Detailed sprint work items with tasks and acceptance criteria.
- Pulled from Product Backlog by Developers
- SM facilitates but does NOT own
- Includes TL technical specs

### PRODUCT BACKLOG
**Location**: `docs/tmux/command-center/BACKLOG.md` (index) + `docs/tmux/command-center/backlog/` (items)
**Owner**: PO (exclusively)

**Purpose:** Future work items and prioritized stories. Only PO adds/removes/prioritizes items.

**File Structure (Split by Priority):**
```
docs/tmux/command-center/
├── BACKLOG.md           # Index file - links to priority files
├── backlog/
│   ├── p1.md            # P1 items (High priority - next sprint)
│   ├── p2.md            # P2 items (Medium priority - future)
│   ├── p3.md            # P3 items (Low priority - nice to have)
│   └── completed.md     # Completed items (reference)
```

**Why split?** Single BACKLOG.md grew too large. Split by priority for faster sprint planning.

---

## ⚠️ CRITICAL: Active Communication (ALL AGENTS)

**THIS IS AN AI TEAM, NOT A HUMAN TEAM. COMMUNICATE EXPLICITLY VIA tm-send.**

### When Assigned Work: ACKNOWLEDGE Immediately

**When SM or anyone assigns you work, ACKNOWLEDGE and START:**

```bash
# SM assigns: "TL -> Review Sprint 13 backlog"
# You MUST respond:
tm-send SM "TL -> SM: Backlog review ACKNOWLEDGED. Starting now."
```

**Why?** AI agents don't auto-respond. Silence = SM thinks you're not working = sprint blocks.

### When You Need Something: ASK via tm-send

**If you need clarification, help, or resources - SPEAK UP:**

```bash
tm-send SM "FE -> SM: Need clarification on CodeMirror version. Which should I use?"
```

**Don't stay silent!** In AI teams, silence = stalled sprint.

### When You Finish: REPORT via tm-send

See "Report Back After Every Task" section below.

---

## ⚠️ CRITICAL: Report Back After Every Task (ALL AGENTS)

**COMPLETING WORK WITHOUT REPORTING = NOT DONE. THIS IS NON-NEGOTIABLE.**

**After completing ANY task, EVERY agent (PO, TL, FE, BE, QA) MUST IMMEDIATELY:**

1. **Update WHITEBOARD** (`docs/tmux/command-center/WHITEBOARD.md`):
   - Update your row in Team Status table
   - Add summary of work done

2. **Report to SM via tmux** (DO NOT SKIP THIS):
   ```bash
   tm-send SM "FE -> SM: [Task] DONE. [Summary]. WHITEBOARD updated."
   ```

**WHY THIS IS CRITICAL:**
- In multi-agent systems, visibility is NOT automatic
- Each agent operates in isolation
- **Without explicit reporting, SM CANNOT proceed and the entire system stalls**
- **The sprint gets BLOCKED waiting for a report that never comes**
- Other team members sit idle

**LESSON LEARNED (Sprint 12):**
- FE completed task but didn't report for 16 minutes
- Entire sprint blocked: SM, QA, PO, TL all waiting
- Boss had to intervene to discover work was done
- **Completing work without reporting = System failure**

**IF YOU FINISH A TASK, REPORT IT IMMEDIATELY. No exceptions.**

---

## Files in This Directory

```
command-center/
├── workflow.md              # This file
├── WHITEBOARD.md            # Current sprint status
├── BACKLOG.md               # Backlog index (links to priority files)
├── backlog/                 # Backlog items by priority
│   ├── p1.md               # P1 - High priority (next sprint)
│   ├── p2.md               # P2 - Medium priority
│   ├── p3.md               # P3 - Low priority
│   └── completed.md        # Completed items
├── setup-team.sh            # Automated setup script (sets @role_name on panes)
├── configs/
│   ├── standard-mcp.json    # MCP config for most roles
│   └── qa-mcp.json          # MCP config for QA (with Playwright)
└── prompts/
    ├── SM_PROMPT.md         # Scrum Master
    ├── PO_PROMPT.md         # Product Owner
    ├── TL_PROMPT.md         # Tech Lead
    ├── FE_PROMPT.md         # Frontend Engineer
    ├── BE_PROMPT.md         # Backend Engineer
    └── QA_PROMPT.md         # Tester (QA)
```

**Note:** Role-to-pane mapping is dynamic via `@role_name` tmux option, set by `setup-team.sh`.

---

## AI Agent Behavior (Important for Coordination)

Since this is a **multi-agent AI system**, each agent (PO, SM, TL, FE, BE, QA) is a Claude Code instance. Understanding AI agent behavior is critical for smooth coordination.

### SessionStart Hook (Automatic Initialization)

**All agents in command-center team have a SessionStart hook that BLOCKS them from responding until they read their role prompt and workflow.md.**

**When it triggers:**
- Session startup (fresh `claude` command)
- Session resume (reconnecting to existing session)
- Context clear (`/clear` command)
- Auto-compact (when context window fills up)

**What it does:**
1. Detects agent role via `$TMUX_PANE` and `@role_name`
2. Blocks agent with mandatory instructions:
   - Read `docs/tmux/command-center/prompts/{ROLE}_PROMPT.md`
   - Read `docs/tmux/command-center/workflow.md`
   - Report "Startup complete - {ROLE} ready"

**Why this exists:**
- Agents often skipped reading docs, causing protocol violations
- Now initialization is **enforced by hook, not optional**
- Works together with CLAUDE.md (hook blocks, CLAUDE.md provides context)

**Location:** `.claude/hooks/session_start_team_docs.py`

**Note:** Hook only activates for command-center team. Other projects/sessions are not affected.

### Auto-Compact (Context Summarization)

**What it is:** When an AI agent's context window fills up, it automatically summarizes its work to continue. This is called "auto-compact."

**What to expect:**
- Agent may pause for 30-60+ seconds during auto-compact
- This is **normal system behavior**, not a failure
- Agent will resume with full context of its work

**SM Response:**
- Be patient - wait for agent to complete auto-compact
- Do NOT send repeated messages during this time
- If no response after 2+ minutes, check agent pane directly

### Agent Response Times

| Situation | Expected Wait |
|-----------|---------------|
| Normal response | 5-15 seconds |
| Complex task | 30-60 seconds |
| Auto-compact in progress | 30-90 seconds |
| Agent stuck (rare) | Check pane after 2 minutes |

**Lesson Learned:** Impatience during auto-compact leads to duplicate messages and confusion. Wait for agents to complete their work.

---

## Prompt Maintenance

When modifying any role prompt (`prompts/*.md`), use the **prompting skill** (`/prompting` or invoke via Skill tool).

Why? Role prompts contain hard-earned lessons from past bugs. Careless edits can remove critical constraints. The prompting skill applies best practices:
- Provide WHY for constraints (helps AI generalize)
- Use positive framing
- Keep lessons while removing redundancy

```bash
# Before editing a prompt
/prompting "Review and optimize [ROLE]_PROMPT.md"
```

---

## System is Ready

All agents are now briefed on the workflow. When Boss provides requirements to PO, the sprint begins.

**Team: Execute autonomously through the sprint. Boss will review after completion.**
