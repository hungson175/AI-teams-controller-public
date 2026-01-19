# Documentation Rewrite Plan: Progressive Disclosure

## Boss Feedback
> "When I read it, I don't feel like there's a proper overview."

## Current Problems

| Issue | Current State | Impact |
|-------|---------------|--------|
| **No true overview** | ARCHITECTURE.md starts with details | Reader lost in first 30 lines |
| **Everything in one file** | Backend README: 631 lines, Frontend: 690 lines | Wall of text, hard to find info |
| **Flat structure** | 3 files total | No depth/layering |
| **Mixed audiences** | API reference mixed with concepts | Developer onboarding slow |

## Target Structure (Progressive Disclosure)

```
docs/generated-docs/
├── README.md                    # NEW: 1-page overview (entry point)
├── ARCHITECTURE.md              # REWRITE: Concepts only, links to specifics
│
├── backend/
│   ├── README.md                # REWRITE: Backend overview + links
│   ├── api/
│   │   ├── README.md            # API overview
│   │   ├── teams.md             # Team management endpoints
│   │   ├── voice.md             # Voice command endpoints
│   │   ├── auth.md              # Authentication endpoints
│   │   └── files.md             # File browser endpoints
│   ├── services/
│   │   ├── README.md            # Services overview
│   │   ├── tmux-service.md      # TmuxService details
│   │   ├── tts-providers.md     # TTS provider details
│   │   └── voice-feedback.md    # Voice feedback pipeline
│   └── models.md                # Pydantic/SQLAlchemy models
│
└── frontend/
    ├── README.md                # REWRITE: Frontend overview + links
    ├── components/
    │   ├── README.md            # Components overview
    │   ├── controller.md        # TmuxController details
    │   ├── file-browser.md      # FileBrowser details
    │   ├── team-creator.md      # TeamCreator details
    │   └── voice.md             # Voice components
    ├── hooks/
    │   ├── README.md            # Hooks overview
    │   └── team-hooks.md        # useTeamState, usePanePolling, etc.
    └── contexts.md              # React contexts
```

## Level 1: Root README.md (NEW - Entry Point)

**Purpose:** 30-second overview. Answer: "What is this project?"

**Content (~50 lines):**
```markdown
# AI Teams Controller

Web application for managing tmux-based AI agent teams with voice command integration.

## What It Does
- Manage multiple AI agent teams running in tmux sessions
- Send commands via text or voice
- Monitor real-time terminal output
- Create new teams from templates

## Quick Start
[3-5 commands to get running]

## Technology
| Layer | Tech |
| Frontend | Next.js 16 |
| Backend | FastAPI |
| Voice | Soniox STT + Google TTS |

## Documentation Map
- [Architecture Overview](./ARCHITECTURE.md) - System design
- [Backend](./backend/README.md) - API, services, models
- [Frontend](./frontend/README.md) - Components, hooks, contexts
```

## Level 2: ARCHITECTURE.md (REWRITE)

**Purpose:** System design for technical readers. No code details.

**Content (~100 lines):**
- System diagram (keep existing mermaid)
- Core concepts (teams, roles, voice flow)
- Technology decisions (why FastAPI, why Next.js)
- Links to backend/frontend for details

**Remove:** All endpoint tables, code snippets, directory structures

## Level 3: Backend/Frontend README.md (REWRITE)

**Purpose:** Overview of each layer with links to specifics.

**Backend README (~80 lines):**
- Quick start (existing)
- Directory overview (brief)
- "Learn More" links to api/, services/, models.md

**Frontend README (~80 lines):**
- Quick start (existing)
- Directory overview (brief)
- "Learn More" links to components/, hooks/, contexts.md

## Level 4: Specific Files (NEW)

**Purpose:** Deep details for specific topics.

**Example: backend/api/teams.md (~60 lines):**
- Team Management endpoints only
- Request/response examples
- Error handling

**Example: frontend/components/controller.md (~80 lines):**
- TmuxController component details
- Props, state, interactions
- Related hooks

## Work Estimate

| Task | Est. Lines | Priority |
|------|------------|----------|
| Create root README.md | 50 | P1 |
| Rewrite ARCHITECTURE.md | 100 | P1 |
| Rewrite backend/README.md | 80 | P1 |
| Rewrite frontend/README.md | 80 | P1 |
| Create backend/api/* files | 200 | P2 |
| Create backend/services/* files | 150 | P2 |
| Create frontend/components/* files | 200 | P2 |
| Create frontend/hooks/* files | 100 | P2 |

**P1 Total:** ~310 lines (core restructure)
**P2 Total:** ~650 lines (deep details)

## Implementation Order

1. **Phase 1 (Core):** Root README + ARCHITECTURE rewrite
2. **Phase 2 (BE/FE Overviews):** Backend/Frontend README rewrites
3. **Phase 3 (Details):** Split existing content into specific files

## Key Principles

1. **Each file has ONE purpose** - overview OR details, not both
2. **Progressive depth** - Start general, link to specific
3. **Scannable** - Tables, headers, bullet points
4. **Exit links** - Every overview links to details
5. **Max 100 lines** per overview file, details can be longer

## Example Flow (Reader Journey)

```
Reader arrives → README.md (30 sec overview)
              → "I want to understand the API"
              → ARCHITECTURE.md (concepts)
              → backend/README.md (backend overview)
              → backend/api/README.md (API overview)
              → backend/api/teams.md (specific endpoints)
```

Each step reveals more detail. Reader stops when they have enough.
