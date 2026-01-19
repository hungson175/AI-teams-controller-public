# Technical Spec: Create Team & Restart Team Features

## Overview
Add Web UI buttons to create and restart AI agent teams via Claude Code CLI.
**Order:** Restart Team first (simpler), then Create Team.

---

## Work Item 1: Restart Team Endpoints (BE)

### 1.1 Full Team Restart
**Endpoint:** `POST /api/teams/{team}/restart`
**Response:** `{"status": "restarted", "team": "...", "panes": [...]}`

**Logic:** Kill session → Execute setup-team.sh → Return new pane IDs

### 1.2 Per-Role Restart
**Endpoint:** `POST /api/teams/{team}/roles/{role}/restart`
**Response:** `{"status": "restarted", "role": "TL", "pane_id": "%142"}`

**Logic:** Find pane by @role_name → Send Ctrl+C → Re-run claude command → Send /init-role

**Model Mapping:** SM/TL=opus, PO/FE/BE=sonnet, QA=haiku

---

## Work Item 2: Create Team Endpoint (BE)

**Endpoint:** `POST /api/teams`
**Request:** `{"name": "my-team", "template": "scrum-6"}`
**Response:** `{"status": "created", "team": "my-team", "panes": [...]}`

**Logic:** Validate name → Check no duplicate → Execute setup-team.sh {name} → Return info
**Security:** Sanitize name (alphanumeric + hyphens only) to prevent shell injection.

---

## Work Item 3: Frontend UI (FE)

**Location:** Left panel, alongside New Terminal, Kill Team, Settings

**Buttons:** "Restart Team" (full restart), "Create Team" (dialog with name input)
**Per-Role:** Restart icon next to each role in sidebar
**States:** Loading spinner, success/error toast

---

## Test Requirements

**Backend (80% min):** restart_team_success, restart_team_not_found, restart_role_success, restart_role_invalid, create_team_success, create_team_duplicate, create_team_invalid_name

**Frontend (70% min):** Button triggers API, loading state, toast display, dialog validation

---

## Acceptance Criteria
- [ ] Full team restart works from Web UI
- [ ] Per-role restart works from Web UI
- [ ] Create team works from Web UI
- [ ] BE tests 80%+, FE tests 70%+
- [ ] No shell injection vulnerabilities
