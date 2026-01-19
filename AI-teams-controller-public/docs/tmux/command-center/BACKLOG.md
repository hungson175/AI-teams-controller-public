# Product Backlog - AI Teams Controller

**Owner:** Product Owner (PO)
**Last Updated:** 2026-01-11
**Purpose:** Index to prioritized backlog files. PO owns this backlog.

---

## Backlog Structure (Split by Priority)

This backlog is organized into priority-based files for better manageability:

| File | Priority | Description | When to Work |
|------|----------|-------------|--------------|
| **This file** | P0 | Critical items | Current/Next Sprint |
| **[backlog/p1.md](./backlog/p1.md)** | P1 | High priority | Soon (1-2 sprints) |
| **[backlog/p2.md](./backlog/p2.md)** | P2 | Medium priority | When capacity allows |
| **[backlog/p3.md](./backlog/p3.md)** | P3 | Low priority | Nice to have |
| **[backlog/completed.md](./backlog/completed.md)** | Archive | Completed/closed items | Reference only |

**Why this structure?**
- BACKLOG.md is under 300 lines (was 2,871 lines)
- Easier to find items by priority during sprint planning
- Clear separation between active and completed work
- Faster to read and maintain

---

## Priority Legend

| Priority | Meaning | When to Work |
|----------|---------|--------------|
| **P0** | Critical | Current/Next Sprint |
| **P1** | High | Soon (1-2 sprints) |
| **P2** | Medium | When capacity allows |
| **P3** | Low | Nice to have |

---

## P0 - Current Sprint Priorities

### Verify Session Start Hook Stability After Auto Compact
**Status:** TODO (Boss Request 2026-01-11)
**Size:** XS (Manual verification)
**Priority:** P0 (Critical quality assurance)

**Problem:**
Need to manually verify that after Claude Code auto compact finishes, all roles in the team continue to work stably. Session start hook behavior must be validated by eye to ensure no roles break or behave incorrectly after conversation compaction.

**Boss Quote:**
"I need to carefully review the session start hook by eye to ensure that after the auto compact finishes, all the roles continue to work stably."

**Task:**
Manual review and verification by Boss to ensure session start hook doesn't break role functionality after auto compact.

**Acceptance Criteria:**
- [ ] Boss manually reviews session start hook behavior
- [ ] All 6 roles (PO, SM, TL, FE, BE, QA) verified working after auto compact
- [ ] No role confusion or broken functionality
- [ ] Document findings if issues found

**Priority:** P0 (Critical for team stability)

---

### Make Voice Feedback Robust Against Claude Code Prompt Changes
**Status:** TODO (Boss Request 2026-01-11 09:29)
**Size:** S (Small - improve prompt detection)
**Priority:** P2

**Problem:**
Our voice feedback relies on detecting Claude Code's prompt character (`>` or `❯`) to find last message boundary. When Claude Code changed from `>` to `❯` (Unicode), our voice feedback broke - reading old messages from 10-15 minutes ago.

**Risk:**
- We have NO control over when Claude Code changes its prompt format
- Software goes "rogue" when external tool behavior changes
- Current fix detects both `>` and `❯`, but what if Claude Code changes to something else?

**As a** system maintainer
**I want** voice feedback to work regardless of Claude Code prompt changes
**So that** our software doesn't break when external tools update

**Possible Solutions:**
- [ ] Dynamic prompt detection (scan for common patterns: `>`, `❯`, `$`, `#`, etc.)
- [ ] Fallback mechanism if prompt not found (use time-based boundary)
- [ ] Alternative trimming strategy that doesn't rely on prompt character
- [ ] Document as known dependency risk (accept the limitation)

**Acceptance Criteria:**
- [ ] Voice feedback continues working even if Claude Code changes prompt format
- [ ] OR: Clear monitoring/alerting when prompt format changes
- [ ] OR: Documented risk with manual fix procedure

**Priority:** P2 (Dependency risk, but not blocking - current fix handles both `>` and `❯`)

---

### Terminal File Popup Closes Unexpectedly
**Status:** TODO (Boss Request 2026-01-11 06:56)
**Size:** TBD (Need more details from Boss)
**Priority:** P2

**Problem:**
When clicking terminal file path link, the popup that appears sometimes closes unexpectedly while loading or viewing. No clear reason - probably UI updating during that time causes popup to close suddenly.

**As a** user viewing terminal output
**I want** the file popup to stay open while I'm viewing it
**So that** I can read the file content without it closing unexpectedly

**Acceptance Criteria:**
- TBD (Boss will provide more details when we work on this)

**Note:** Ask Boss for more details when starting this work.

**Priority:** P2

---

### Research: Replace tmux with zellij
**Status:** TODO (Boss Request 2026-01-10 21:38)
**Size:** XS (Research task)
**Priority:** P2 (Research and recommendation)

**Boss Directive:**
"tmux works like shit, I want to replace (in this project) with zellij: https://github.com/zellij-org/zellij. Tell TL to research that (in context of this project) and tell me his suggestions."

**Research Scope:**
- [ ] What is zellij? (features, capabilities)
- [ ] How does zellij compare to tmux for our use case?
- [ ] Feasibility: Can we replace tmux with zellij?
- [ ] Migration effort: How much work to switch?
- [ ] Benefits for AI Teams Controller multi-agent system
- [ ] Drawbacks or limitations
- [ ] Recommendation: Should we switch?

**Context:**
Our project uses tmux for:
- Multi-agent team sessions (command-center, jarvis, wife_tts, trading-bot)
- Pane-based role separation (PO, SM, TL, FE, BE, QA)
- tm-send command for cross-pane/cross-session messaging
- Backend API integration (reading pane output, sending commands)

**Deliverable:**
- Research document with TL's findings and recommendation
- Present to Boss for decision

**Priority:** P2 (Research first, implement if Boss approves)

---

## Quick Links to Other Priorities

### **→ [P1 - High Priority Items](./backlog/p1.md)** (932 lines)
- Technical Debt Evaluation
- Codebase Refactor
- Pluggable TTS Architecture
- Voice Speed UI Setting
- Mini Online IDE Epic
- Multi-User Docker Deployment
- Vietnamese Educational Content Library
- And more...

### **→ [P2 - Medium Priority Items](./backlog/p2.md)** (209 lines)
- Direct Tmux Pane Attachment
- Package Software for Distribution
- Voice Command Auto-On/Auto-Off
- File Browser improvements
- And more...

### **→ [P3 - Low Priority Items](./backlog/p3.md)** (524 lines)
- Claude Code CLI for Team Operations
- Polish File Browser Epic
- Security Hardening
- Voice-Controlled Navigation
- Team Creator UI
- And more...

### **→ [Completed/Archived Items](./backlog/completed.md)** (231 lines)
- Standardize Service Restart Mechanism
- Terminal Clickable File Paths
- Simple File Search Epic
- Fix Cmd+P File Search
- Add Interactive Terminal Tab
- Fix Frontend 500 Errors
- And more...

---

**Last Updated:** 2026-01-11 (Backlog reorganization - Option 2: Split by Priority)
