# Claude Code CLI Research: Team Creation & Restart Features

**Date:** 2026-01-15
**Author:** TL
**Status:** RESEARCH COMPLETE - Awaiting Boss Review
**Related Backlog:** P2 - Create Team Feature, P2 - Restart Team Feature

---

## 1. What is Claude Code CLI?

Claude Code is Anthropic's official command-line interface that allows developers to interact with Claude directly from the terminal. It uses the user's **Claude subscription** (e.g., Claude MAX at $100/month), NOT the API.

### Key Characteristics
- **Terminal-native**: Lives in your terminal, works with all CLI tools
- **Subscription-based**: Uses Claude MAX/Pro subscription, not API credits
- **Interactive by default**: Starts an interactive session when run
- **Headless mode available**: `-p` flag for non-interactive/scripted usage

### Installation
```bash
# macOS/Linux/WSL
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex

# Homebrew
brew install --cask claude-code
```

---

## 2. Claude Code CLI Usage

### Basic Commands
```bash
# Interactive session (default)
claude

# Non-interactive/headless mode with -p flag
claude -p "Your prompt here"

# Pipe integration
cat file.py | claude -p "Review this code"

# Continue previous session
claude --continue
claude -r <session-id>  # Resume specific session
```

### Key CLI Flags (Relevant to Team Features)

| Flag | Description | Relevance |
|------|-------------|-----------|
| `-p, --print` | Non-interactive mode, print and exit | **CRITICAL for automation** |
| `--model <model>` | Specify model (sonnet, opus, haiku) | Per-role model assignment |
| `--mcp-config <file>` | Load MCP server config | Per-role tool access |
| `--strict-mcp-config` | Only use specified MCP servers | Security isolation |
| `--system-prompt <prompt>` | Custom system prompt | Role-specific behavior |
| `--append-system-prompt` | Add to default system prompt | Inject role prompts |
| `--permission-mode <mode>` | Permission handling | `bypassPermissions` for automation |
| `--output-format <format>` | Output format (text, json, stream-json) | Parse responses programmatically |
| `--session-id <uuid>` | Use specific session ID | Session management |
| `--no-session-persistence` | Don't save session to disk | Clean restart |

### Output Formats for Automation
```bash
# Text output (default)
claude -p "prompt" --output-format text

# JSON output (structured)
claude -p "prompt" --output-format json

# Streaming JSON (real-time)
claude -p "prompt" --output-format stream-json
```

---

## 3. Solution Proposals for Team Features

### 3.1 Create Team Feature (Web UI)

**Current Flow:**
1. User runs `setup-team.sh` manually in terminal
2. Script creates tmux session with 6 panes
3. Each pane runs `claude --model <model> --mcp-config <config>`
4. Script sends `/init-role <ROLE>` to each pane

**Proposed Web UI Flow:**

#### Option A: Backend Executes Shell Script (Simple)

```
[Web UI] → [Backend API] → [Execute setup-team.sh] → [tmux session]
```

**Implementation:**
1. Frontend: "Create Team" button with team name input
2. Backend: `POST /api/teams/create` endpoint
3. Backend: Subprocess runs `setup-team.sh <team-name>`
4. Backend: Returns session details (pane IDs, status)

**Pros:**
- Reuses existing proven script
- Minimal new code
- Works today

**Cons:**
- Shell script execution from web (security consideration)
- Less granular control

#### Option B: Backend Creates Session Programmatically (More Control)

```
[Web UI] → [Backend API] → [Python tmux library] → [Claude CLI per pane]
```

**Implementation:**
1. Backend uses `libtmux` Python library
2. Create session: `server.new_session("team-name")`
3. Create panes: `window.split_window()` × 5
4. Execute in each pane: `pane.send_keys("claude --model opus ...")`
5. Initialize roles: `pane.send_keys("/init-role TL")`

**Pros:**
- Full programmatic control
- Better error handling
- Can track state in database

**Cons:**
- More code to write
- Need to replicate setup-team.sh logic

#### Option C: Claude Code Agent SDK (Most Advanced)

```
[Web UI] → [Backend API] → [Agent SDK (Python/TS)] → [Claude instances]
```

The Agent SDK allows running Claude Code programmatically:
```python
from claude_code import Agent

agent = Agent(
    model="opus",
    system_prompt="You are TL...",
    tools=["Bash", "Edit", "Read"]
)
response = agent.run("Initialize as TL for command-center team")
```

**Pros:**
- Native Python/TypeScript integration
- No tmux dependency
- Better for cloud deployment

**Cons:**
- Requires Agent SDK setup
- Different architecture than current tmux-based approach
- May need refactoring of team coordination

### 3.2 Restart Team Feature (Web UI)

**Current Flow:**
1. User manually kills tmux session: `tmux kill-session -t command-center`
2. User runs `setup-team.sh` again

**Proposed Web UI Flows:**

#### Restart Option A: Kill and Recreate (Clean Restart)

```
[Web UI "Restart"] → [Backend] → [kill-session] → [setup-team.sh]
```

1. `POST /api/teams/{team}/restart`
2. Backend: `tmux kill-session -t {team}`
3. Backend: Run `setup-team.sh {team}`
4. Return new session info

#### Restart Option B: Re-initialize Roles Only (Preserve Context)

```
[Web UI "Soft Restart"] → [Backend] → [Send /clear to each pane]
```

1. `POST /api/teams/{team}/reinitialize`
2. Backend: For each pane, send `/clear` command
3. Backend: Send `/init-role <ROLE>` to each pane
4. Roles re-read prompts, preserve tmux session

**Pros:**
- Faster than full restart
- Preserves tmux session
- Agents can resume with fresh context

#### Restart Option C: Per-Role Restart (Granular)

```
[Web UI "Restart Role"] → [Backend] → [Kill/restart single Claude instance]
```

1. `POST /api/teams/{team}/roles/{role}/restart`
2. Backend: Send `Ctrl+C` to specific pane
3. Backend: Re-run `claude --model <model> ...` in that pane
4. Backend: Send `/init-role <ROLE>`

**Pros:**
- Only restarts problematic agent
- Doesn't disrupt other agents

---

## 4. Recommended Approach

### For Create Team: Option A (Shell Script Execution)

**Rationale:**
- `setup-team.sh` already works perfectly
- Minimal risk - proven solution
- Can iterate to Option B later if needed

**Implementation Steps:**
1. Create `POST /api/teams/create` endpoint
2. Accept: `{ "team_name": "string", "template": "scrum-6" }`
3. Execute: `subprocess.run(["./setup-team.sh", team_name])`
4. Parse output for pane IDs
5. Return: `{ "session": "...", "panes": [...], "status": "created" }`

### For Restart Team: Option A + Option C (Combined)

**Rationale:**
- Full restart for major issues
- Per-role restart for stuck agents (common case)

**Implementation Steps:**
1. `POST /api/teams/{team}/restart` - Full restart
2. `POST /api/teams/{team}/roles/{role}/restart` - Single role restart
3. Frontend: "Restart Team" button + per-role restart buttons

---

## 5. Security Considerations

1. **Subprocess execution**: Validate team name (alphanumeric only)
2. **Path injection**: Use absolute paths, no user input in paths
3. **Session isolation**: Each team is isolated tmux session
4. **Permission mode**: Consider `bypassPermissions` for headless only in sandboxed environments

---

## 6. Next Steps (If Boss Approves)

1. **Phase 1**: Backend endpoints for create/restart
   - `POST /api/teams/create`
   - `POST /api/teams/{team}/restart`
   - `POST /api/teams/{team}/roles/{role}/restart`

2. **Phase 2**: Frontend UI
   - Create Team dialog
   - Restart Team button
   - Per-role restart buttons

3. **Phase 3**: Status monitoring
   - Real-time team status
   - Agent health indicators

---

## 7. References

- Claude Code CLI: `claude --help` (local installation)
- Official docs: https://code.claude.com/docs/en/overview
- Current setup script: `docs/tmux/command-center/setup-team.sh`
- Backlog items: `docs/tmux/command-center/backlog/p2.md`
