# Technical Spec: Rename 'command-center' to 'command-center'

**Created by**: TL
**Date**: 2026-01-01
**Sprint**: 5

---

## Overview

Rename the tmux session and all associated files/references from `command-center` to `command-center`.

---

## Impact Analysis Summary

| Category | Count | Details |
|----------|-------|---------|
| **Directory rename** | 1 | `docs/tmux/command-center/` → `docs/tmux/command-center/` |
| **Files with references** | 14 | See detailed list below |
| **Case variations found** | 0 | No `scrum_team`, `Scrum-Team`, or `SCRUM-TEAM` found |

---

## PHASE 1: Directory Rename

### Action
```bash
git mv docs/tmux/command-center docs/tmux/command-center
```

### Contents Being Moved
```
docs/tmux/command-center/
├── BACKLOG.md
├── PANE_ROLES.md
├── WHITEBOARD.md
├── configs/
│   ├── qa-mcp.json
│   └── standard-mcp.json
├── prompts/
│   ├── BE_PROMPT.md
│   ├── FE_PROMPT.md
│   ├── PO_PROMPT.md
│   ├── QA_PROMPT.md
│   ├── SM_PROMPT.md
│   └── TL_PROMPT.md
├── scripts/
│   └── tm-send
├── setup-team.sh
├── sprint_1/
│   └── TL_SPECS.md
├── sprints/
│   ├── sprint_1/
│   └── sprint_2/
└── tmux_team_overview.md
```

---

## PHASE 2: File Content Updates

### 2.1 Core Configuration Files (CRITICAL)

#### File: `setup-team.sh` (6 occurrences)
| Line | Current | New |
|------|---------|-----|
| 10 | `SESSION_NAME="command-center"` | `SESSION_NAME="command-center"` |
| 11 | `PROMPTS_DIR="$PROJECT_ROOT/docs/tmux/command-center/prompts"` | `PROMPTS_DIR="$PROJECT_ROOT/docs/tmux/command-center/prompts"` |
| 84 | `PANE_ROLES="$PROJECT_ROOT/docs/tmux/command-center/PANE_ROLES.md"` | `PANE_ROLES="$PROJECT_ROOT/docs/tmux/command-center/PANE_ROLES.md"` |
| 90 | `./docs/tmux/command-center/setup-team.sh` | `./docs/tmux/command-center/setup-team.sh` |
| 112 | `tmux list-panes -t command-center` | `tmux list-panes -t command-center` |
| 142 | `MCP_CONFIG_DIR="$PROJECT_ROOT/docs/tmux/command-center/configs"` | `MCP_CONFIG_DIR="$PROJECT_ROOT/docs/tmux/command-center/configs"` |
| 190 | `$PROJECT_ROOT/docs/tmux/command-center/WHITEBOARD.md` | `$PROJECT_ROOT/docs/tmux/command-center/WHITEBOARD.md` |

#### File: `scripts/tm-send` (2 occurrences)
| Line | Current | New |
|------|---------|-----|
| 23-24 | `docs/tmux/command-center/PANE_ROLES.md` | `docs/tmux/command-center/PANE_ROLES.md` |

#### File: `PANE_ROLES.md` (3 occurrences)
| Line | Current | New |
|------|---------|-----|
| 5 | `./docs/tmux/command-center/setup-team.sh` | `./docs/tmux/command-center/setup-team.sh` |
| 27 | `tmux list-panes -t command-center` | `tmux list-panes -t command-center` |

---

### 2.2 Documentation Files

#### File: `tmux_team_overview.md` (5 occurrences)
| Line | Current | New |
|------|---------|-----|
| 255 | `docs/tmux/command-center/WHITEBOARD.md` | `docs/tmux/command-center/WHITEBOARD.md` |
| 264 | `docs/tmux/command-center/sprints/sprint_N/SPRINT_BACKLOG.md` | `docs/tmux/command-center/sprints/sprint_N/SPRINT_BACKLOG.md` |
| 273 | `docs/tmux/command-center/BACKLOG.md` | `docs/tmux/command-center/BACKLOG.md` |
| 284 | `docs/tmux/command-center/WHITEBOARD.md` | `docs/tmux/command-center/WHITEBOARD.md` |
| 300 | `command-center/` (folder name in tree) | `command-center/` |

#### File: `WHITEBOARD.md` (9 occurrences)
All references to `command-center` should be updated to `command-center`, including:
- Sprint goal description
- Acceptance criteria
- Directory paths
- tmux commands

#### File: `BACKLOG.md` (7+ occurrences)
All references to `command-center` should be updated to `command-center`.

---

### 2.3 Role Prompt Files (12 occurrences total)

Each prompt file has 2 occurrences:

| File | Lines | Pattern |
|------|-------|---------|
| `BE_PROMPT.md` | 150, 203 | `docs/tmux/command-center/WHITEBOARD.md`, `docs/tmux/command-center/tmux_team_overview.md` |
| `FE_PROMPT.md` | 204, 256 | Same pattern |
| `PO_PROMPT.md` | 161, 192 | Same pattern |
| `QA_PROMPT.md` | 241, 285 | Same pattern |
| `SM_PROMPT.md` | 186, 217 | Same pattern |
| `TL_PROMPT.md` | 186, 216 | Same pattern |

---

### 2.4 External Files (Outside docs/tmux/command-center/)

#### File: `.claude/commands/init-role.md` (12 occurrences)
| Line | Current | New |
|------|---------|-----|
| 8 | `command-center` | `command-center` |
| 21-22 | `For command-center:`, `docs/tmux/command-center/tmux_team_overview.md` | `For command-center:`, `docs/tmux/command-center/tmux_team_overview.md` |
| 34-40 | All 6 prompt file paths | Update all to `docs/tmux/command-center/prompts/` |
| 75-76 | `For command-center:` section | `For command-center:` |

#### File: `frontend/components/controller/TerminalPanel.test.tsx` (2 occurrences)
| Line | Current | New |
|------|---------|-----|
| 792 | `selectedTeam="command-center"` | `selectedTeam="command-center"` |
| 806 | `team=command-center` | `team=command-center` |

---

### 2.5 Hooks (NO CHANGES NEEDED)

These hooks do NOT reference `command-center`:
- `.claude/hooks/session_start_team_docs.py` - Only handles `ai_controller_full_team` session
- `.claude/hooks/post_compact_tmux_reminder.sh` - Only handles `ai_controller_full_team` and `AI-controller-app-PM`
- `.claude/hooks/post_compact_tmux_reminder.py` - Only handles `ai_controller_full_team` and `AI-controller-app-PM`
- `.claude/hooks/dk_git_commit_trigger.py` - No session-specific references

**NOTE**: If you want `command-center` session to be supported by these hooks in the future, that would be a separate story.

---

## PHASE 3: Verification

### Test Cases

1. **Grep verification** (Acceptance Criteria):
   ```bash
   # All should return empty
   grep -r "command-center" docs/
   grep -r "command-center" .claude/
   grep -r "command-center" frontend/
   ```

2. **Directory exists**:
   ```bash
   ls docs/tmux/command-center/
   ```

3. **Setup script works**:
   ```bash
   ./docs/tmux/command-center/setup-team.sh
   tmux list-sessions | grep command-center
   ```

4. **tm-send works**:
   ```bash
   tm-send PO "Test message"
   ```

5. **Frontend test passes**:
   ```bash
   cd frontend && pnpm test TerminalPanel.test.tsx
   ```

---

## Implementation Order (for FE/BE)

Since this is a pure rename operation (no FE/BE split), recommended order:

1. **Directory rename** (git mv)
2. **Update setup-team.sh** (most critical - creates session)
3. **Update scripts/tm-send** (communication depends on it)
4. **Update PANE_ROLES.md** (single source of truth)
5. **Update all prompts** (use sed for bulk replace)
6. **Update tmux_team_overview.md**
7. **Update WHITEBOARD.md and BACKLOG.md**
8. **Update .claude/commands/init-role.md**
9. **Update frontend test**
10. **Run verification**

### Bulk Replace Command (after directory rename)
```bash
cd docs/tmux/command-center
find . -type f -name "*.md" -exec sed -i 's/command-center/command-center/g' {} +
find . -type f -name "*.sh" -exec sed -i 's/command-center/command-center/g' {} +
find . -type f -name "tm-send" -exec sed -i 's/command-center/command-center/g' {} +
```

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Missed references | Use grep verification after completion |
| Broken tm-send | Test immediately after updating |
| Session name mismatch | Kill old session before starting new one |
| Stale caches | Clear any tmux options before restart |

---

## Acceptance Criteria (from PO)

- [ ] Directory `docs/tmux/command-center/` renamed to `docs/tmux/command-center/`
- [ ] `grep -r "command-center" docs/` returns NO results
- [ ] `grep -r "command-center" .claude/` returns NO results
- [ ] `grep -r "command-center" frontend/` returns NO results
- [ ] `setup-team.sh` creates session named 'command-center'
- [ ] `tm-send` works with new paths
- [ ] Frontend test passes

---

## Summary

| Metric | Count |
|--------|-------|
| Total files to modify | 14 |
| Directory to rename | 1 |
| Total `command-center` occurrences | ~50+ |
| Estimated effort | S (mostly sed replacements) |
