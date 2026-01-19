# AI-Controller-App Team (PM + CR + TESTER)

**Target Audience**: PM, CR, and TESTER agents working in this system
**Project**: TMUX Team Controller - Web-based interface for AI agent teams

## System Overview

This is a **three-agent team** where:
- **Boss (Human User)** = Coder, Solution Architect - does ALL technical work
- **PM (Claude Code)** = Project management assistant - helps Boss stay organized
- **CR (Codex CLI)** = Code Reviewer - reviews code when Boss asks
- **TESTER (Claude Code)** = Tester - runs tests and verifies functionality

### Why This Structure?

The Boss prefers to code and design directly. The assistants help with:
- **PM**: Sprint management, documentation sync, commit messages, progress tracking
- **CR**: Code review, quality checks, suggestions for improvement
- **TESTER**: Run tests, verify functionality, report issues

**Important**: PM, CR, and TESTER do NOT talk to each other. All agents communicate **only with Boss** - they report their results directly to Boss, not to PM.

### Agent Roles

- **PM (Project Manager)** - Pane 0: Boss's assistant for project coordination
- **CR (Code Reviewer)** - Pane 1: Reviews code using `codex --yolo`
- **TESTER (Tester)** - Pane 2: Runs tests using `claude`
- **Boss (User)** - **Boss Terminal (outside tmux)**: Does all the work

## Boss Terminal (CRITICAL)

The Boss operates from a **separate terminal outside the tmux session**.

**Four Modes of Operation (MUST FOLLOW EXACTLY)**:

1. **Direct Work Mode** (NO prefix): Boss Terminal Claude executes tasks directly
   - Example: `add API endpoint for sessions` -> Boss Terminal Claude does the work itself
   - Use for: Code changes, file edits, running commands
   - **NEVER relay to PM, CR, or TESTER when there's no prefix!**

2. **PM Communication Mode** (`>>>` prefix): Send message to PM
   - Example: `>>> update whiteboard with current progress` -> PM receives and acts
   - Example: `>>> prepare commit for authentication feature` -> PM prepares commit message
   - Use for: Project management tasks PM should handle

3. **CR Communication Mode** (`<<<` prefix): Send message to Code Reviewer
   - Example: `<<< review the changes in frontend/app/page.tsx` -> CR reviews
   - Example: `<<< check for security issues in the API routes` -> CR analyzes
   - Use for: Code review, quality checks, improvement suggestions

4. **TESTER Communication Mode** (`###` prefix): Send message to Tester
   - Example: `### run all backend tests` -> TESTER runs tests
   - Example: `### verify the /teams endpoint works` -> TESTER tests endpoint
   - Use for: Running tests, verifying functionality, checking integration

**Boss Terminal Commands**:
```bash
# Send message to PM (pane 0)
tm-send AI-controller-app-PM:0.0 "BOSS [HH:MM]: your message here"

# Send message to CR (pane 1)
tm-send AI-controller-app-PM:0.1 "BOSS [HH:MM]: your message here"

# Send message to TESTER (pane 2)
tm-send AI-controller-app-PM:0.2 "BOSS [HH:MM]: your message here"

# View PM pane output
tmux capture-pane -t AI-controller-app-PM:0.0 -p | tail -50

# View CR pane output
tmux capture-pane -t AI-controller-app-PM:0.1 -p | tail -50

# View TESTER pane output
tmux capture-pane -t AI-controller-app-PM:0.2 -p | tail -50

# Attach to session (to observe all)
tmux attach -t AI-controller-app-PM
```

## Core Principles

1. **Boss Does All Technical Work**: PM/CR/TESTER never write production code
2. **PM Assists with Organization**: Sprint tracking, documentation, commit messages
3. **CR Reviews Code**: Quality checks, suggestions (uses codex --yolo)
4. **TESTER Runs Tests**: Test execution, verification (uses claude)
5. **No Inter-Agent Communication**: All agents report directly to Boss, never to each other or through PM
6. **Communication Prefixes**: `>>>` for PM, `<<<` for CR, `###` for TESTER

## Pane Layout

```
+------------------+------------------+
|                  | Pane 1           |
| Pane 0           | CR (Codex)       |
| PM (Claude)      |                  |
|                  +------------------+
|                  | Pane 2           |
|                  | TESTER (Claude)  |
|                  |                  |
+------------------+------------------+
```

## Project Context

### Current Status: Production Ready ✅

All development phases complete:
- ✅ Phase 1: UI Development (Next.js frontend)
- ✅ Phase 2: Mock APIs (removed - now using real backend)
- ✅ Phase 3: FastAPI Backend
- ✅ Phase 4: Real tmux Integration with Strategy Pattern

### Current Architecture

```
AI-teams-controller/
├── frontend/          # Next.js app (port 3334) - proxies to backend
├── backend/           # FastAPI server (port 17061) - real tmux integration
│   └── app/services/
│       ├── base.py          # TeamService ABC (Strategy interface)
│       ├── mock_data.py     # MockDataService (for testing)
│       ├── tmux_service.py  # TmuxService (production)
│       └── factory.py       # Service factory
└── docs/
    ├── product/       # PRD, frontend specs
    ├── proccesses/    # Development framework
    └── tmux/          # Team documentation
```

### API Endpoints (FastAPI Backend)

All requests proxy from Next.js to FastAPI backend (port 17061):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/teams` | GET | List real tmux sessions |
| `/api/teams/{team}/roles` | GET | List panes for a session |
| `/api/send/{team}/{role}` | POST | Send command to pane (Two-Enter Rule) |
| `/api/state/{team}/{role}` | GET | Get pane output |
| `/health` | GET | Health check |

**Service Mode**: Set `TEAM_SERVICE_TYPE=mock` for testing, `tmux` (default) for production.

## Agent Responsibilities

### PM (Project Manager)
- Sprint management, WHITEBOARD updates
- Documentation sync
- Commit message preparation
- Progress tracking
- **Does NOT**: Write code, run commands, make technical decisions

### CR (Code Reviewer)
- Code review when asked
- Quality checks, security analysis
- Improvement suggestions
- Reports findings **directly to Boss**
- **Does NOT**: Write code, communicate with PM/TESTER

### TESTER
- Run test suites
- Verify API endpoints
- Check integration
- Reports results **directly to Boss**
- **Does NOT**: Write code, communicate with PM/CR

## Communication Pattern

### Message Format

```
[ROLE] [HH:mm]: [Brief message]. See [reference].
```

Examples:
- `BOSS [14:30]: Update whiteboard - completed team list API`
- `PM [14:32]: WHITEBOARD updated. Ready for next task.`
- `CR [14:35]: Code review complete. Found 2 issues.`
- `TESTER [14:40]: All tests passing. 12/12.`

### Two-Enter Rule (CRITICAL)

Use `tm-send` which handles the two-enter rule automatically:
```bash
tm-send %PANE "message"
```

## Boss Communication Examples

- `>>> what's the current sprint status?` - PM reports from WHITEBOARD
- `>>> update: finished team list component` - PM updates WHITEBOARD
- `>>> prepare commit for API mocking` - PM drafts commit message
- `<<< review the backend routes` - CR reviews code
- `<<< check for security issues` - CR does security audit
- `### run all tests` - TESTER runs test suites
- `### verify frontend-backend integration` - TESTER checks integration

## Files in This Directory

```
AI-controller-app-PM/
├── README.md                    # This file
├── WHITEBOARD.md               # Current sprint status
├── setup-team.sh               # Team setup script
└── prompts/
    ├── PM_PROMPT.md            # PM role prompt
    ├── CR_PROMPT.md            # Code Reviewer prompt
    └── TESTER_PROMPT.md        # Tester prompt
```

## System is Ready

All three agents are briefed on the workflow:
- **PM** (`>>>`): Assists with project management while Boss codes
- **CR** (`<<<`): Reviews code when Boss asks using codex --yolo
- **TESTER** (`###`): Runs tests and verifies functionality

**PM, CR, and TESTER do NOT communicate with each other. All report directly to Boss.**
