# AI Teams Controller - Claude Code Memory

## This is a Multi-Agent Tmux Team

You are part of a 6-role Scrum team in tmux session `command-center`.

| Role | Pane | Responsibility |
|------|------|----------------|
| PO | 0 | Product Owner - requirements from Boss |
| SM | 1 | Scrum Master - facilitates process |
| TL | 2 | Tech Lead - architecture, code review |
| FE | 3 | Frontend - Next.js implementation |
| BE | 4 | Backend - FastAPI implementation |
| QA | 5 | Tester - blackbox browser testing |

## Initialization (Automatic Context Injection)

**A SessionStart hook automatically injects your role docs into context.** This happens automatically on:
- Startup (new session)
- Resume (reconnecting)
- Clear (`/clear` command)
- Compact (auto or manual)

**What the hook does:**
1. Detects your role: `tmux show-options -pt $TMUX_PANE -qv @role_name`
2. Reads `docs/tmux/command-center/prompts/{ROLE}_PROMPT.md`
3. Reads `docs/tmux/command-center/workflow.md`
4. Injects both into your context automatically

**How it works:**
- Hook (`.claude/hooks/session_start_team_docs.py`) runs on startup/resume/clear/compact
- Both files are injected as context immediately after compaction
- CLAUDE.md (this file) provides quick reference for key info
- No action required from you - it's fully automatic

## Universal Communication

Use `tm-send ROLE "message"` for ALL cross-role communication. Never use raw tmux send-keys.

## Ports

| Service | Port |
|---------|------|
| Frontend (Next.js) | 3334 |
| Backend (FastAPI) | 17061 |
| Terminal Service | 17071 |

## Service Restart (Use Scripts Only)

```bash
./scripts/restart-frontend.sh   # FE only - handles clean rebuild
./scripts/restart-backend.sh    # BE only
./scripts/restart-celery.sh     # BE only - required after voice/TTS changes
./scripts/restart-all.sh        # All services
```

**Never use manual pkill/systemctl** - scripts handle clean shutdown, rebuild, and verification.

## Key Files

| File | Purpose |
|------|---------|
| `docs/tmux/command-center/workflow.md` | Team workflow and roles |
| `docs/tmux/command-center/WHITEBOARD.md` | Current sprint status |
| `docs/tmux/command-center/TEAM_PLAYBOOK.md` | Lessons learned |
| `docs/tmux/command-center/prompts/*.md` | Role-specific prompts |
| `docs/generated-docs/` | Architecture documentation |

## Production Infrastructure

Services run locally, exposed via Vietnix VPS (14.225.192.6) reverse SSH tunnels:
- `voice-ui.hungson175.com` → localhost:3334
- `voice-backend.hungson175.com` → localhost:17061
- `voice-terminal.hungson175.com` → localhost:17071

## Environment Variables (backend/.env)

```bash
TTS_PROVIDER=google              # or "openai"
GOOGLE_APPLICATION_CREDENTIALS=  # Path to service account JSON
OPENAI_API_KEY=                  # For OpenAI TTS
XAI_API_KEY=                     # For Grok LLM
API_TOKEN=                       # Backend auth
```

