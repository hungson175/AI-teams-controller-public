# TEAM PLAYBOOK - Self-Evolving Lessons

**Purpose:** Structured knowledge base that evolves through sprint retrospectives. Based on ACE (Agentic Context Engineering) framework.

**Format:** Each bullet has `[ID] helpful=N harmful=N :: content`
- **ID**: Unique identifier (category-NNNNN)
- **helpful**: Count of times this lesson led to success
- **harmful**: Count of times following this lesson caused problems
- **content**: The specific, actionable lesson

**Categories:**
- `comm-NNNNN`: Communication patterns
- `sprint-NNNNN`: Sprint execution patterns
- `code-NNNNN`: Code quality patterns
- `infra-NNNNN`: Infrastructure patterns
- `role-NNNNN`: Role boundary patterns
- `retro-NNNNN`: Retrospective/learning patterns

**Maintenance:** SM updates after each sprint retrospective (Reflector → Curator flow)

---

## Communication Patterns

[comm-00001] helpful=15 harmful=0 :: Always use `tm-send` for cross-role communication. Raw `tmux send-keys` causes silent failures because agents forget the 2nd enter.

[comm-00002] helpful=14 harmful=0 :: FE/BE must report completion via tm-send immediately after task done. Format: `ROLE -> SM: [Task] DONE. [Summary]. WHITEBOARD updated.` Silence = sprint blocks.

[comm-00003] helpful=8 harmful=0 :: ALL cross-role communication goes through SM. Direct role-to-role bypasses SM visibility and blocks coordination.

[comm-00004] helpful=9 harmful=0 :: When assigned work, ACKNOWLEDGE immediately via tm-send. AI agents don't auto-respond; silence = SM thinks you're not working.

[comm-00005] helpful=5 harmful=0 :: After assigning work, SM must verify agent acts (check pane after 30-60s). Passive coordination = broken sprint.

---

## Sprint Execution Patterns

[sprint-00001] helpful=11 harmful=0 :: TL must complete technical design BEFORE FE/BE implementation starts. Boss directive: "design carefully before handing off to coders."

[sprint-00002] helpful=11 harmful=0 :: FE/BE use TDD: write failing tests first, then implement. Coverage targets: FE 70%, BE 80%.

[sprint-00003] helpful=7 harmful=0 :: App MUST work after every sprint. Each sprint ends with working system, not partial implementation.

[sprint-00004] helpful=6 harmful=0 :: After Boss accepts sprint, immediately push to remote: `git add -A && git commit && git push`. Work not pushed = not saved.

[sprint-00005] helpful=5 harmful=1 :: Progressive implementation: small → medium → full. Don't over-engineer first iteration.

---

## Code Quality Patterns

[code-00001] helpful=16 harmful=0 :: Frontend restart MUST include clean rebuild: `rm -rf .next && pnpm build`. Stale cache causes 500 errors on static chunks.

[code-00002] helpful=10 harmful=0 :: Backend Celery does NOT auto-reload. After ANY changes to celery_tasks.py or tts_providers.py, restart Celery worker.

[code-00003] helpful=6 harmful=0 :: CSS flexbox scroll fix: add `min-h-0 overflow-hidden` to ENTIRE flex ancestor chain, not just one level.

[code-00004] helpful=5 harmful=0 :: When requirement is ambiguous (e.g., "make popup scrollable" but multiple popups exist), ask "Which component?" BEFORE implementing.

[code-00005] helpful=1 harmful=0 :: When parsing terminal output for prompts, detect BOTH ASCII and Unicode variants. Claude Code uses `❯` (U+276F), older shells use `>`. External tools can change prompt format without notice - this silently broke voice feedback for 10-15 minutes.

[code-00006] helpful=1 harmful=0 :: React callbacks passed to custom hooks MUST be wrapped in useCallback. Inline callbacks create new references on every render → useEffect re-runs → connections (WebSocket, subscriptions) recreated = connection storm. P0 2026-01-11: Thousands of [WS] Error events because onRoleActivityUpdate was inline.

[code-00007] helpful=1 harmful=0 :: Unit tests passing ≠ bug fixed. Tests can pass while testing the WRONG thing. P0 2026-01-11: 8/8 tests passed (exception handling, state logic) but missed real bug (callback reference stability). Test quality > test quantity.

[code-00008] helpful=1 harmful=0 :: For UI rendering bugs (flickering, layout shifts), unit tests are INSUFFICIENT. Must use real browser testing (Playwright/Cypress) with actual login to verify fix works. Mocked tests can't catch render cycle issues.

[code-00009] helpful=1 harmful=0 :: Manual endpoint testing isolates frontend vs backend issues quickly. P0 2026-01-11: BE ran `websocat ws://localhost:17061/api/ws/state/...` - confirmed WS endpoint works, proving issue was 100% frontend.

[code-00010] helpful=1 harmful=0 :: When extracting fetch() to service classes (DIP pattern), fetch LOSES its `this` binding to window object → "Failed to execute 'fetch' on 'Window': Illegal invocation" error. Fix: call fetch() directly OR use `fetch.bind(window)`. P0 2026-01-12: Sprint 6 SOLID refactoring extracted fetch to TeamApiService class, blocked Boss usage completely until fixed.

---

## Infrastructure Patterns

[infra-00001] helpful=13 harmful=0 :: Production services (frontend, backend, celery) require manual restart after code changes. They don't auto-reload.

[infra-00002] helpful=8 harmful=0 :: Before QA testing, verify: (1) frontend rebuilt with latest code, (2) backend restarted, (3) celery restarted if voice features changed.

[infra-00003] helpful=5 harmful=0 :: Check ports are active before testing: `curl -I http://localhost:3334` (frontend), `curl http://localhost:17061/health` (backend).

[infra-00004] helpful=4 harmful=0 :: Verify COMPLETE testing infrastructure before QA assignment (not just build tools). Sprint 10 blocked because no Android emulator.

[infra-00005] helpful=2 harmful=0 :: Frontend runs as systemd user service (`ai-teams-frontend.service`), not background process. Use `systemctl --user disable/enable` (not just stop/start) to prevent race condition. Killing process directly causes systemd auto-restart race.

[infra-00006] helpful=1 harmful=0 :: After TTS/voice config changes, clear ALL caches: Celery Redis (`redis-cli KEYS "celery-task-meta-*" | xargs redis-cli DEL`), TTS file cache (`rm -rf backend/cache/tts/`). Stale caches served wrong voice for hours in Sprint 2026-01-10.

[infra-00007] helpful=1 harmful=0 :: Next.js NEXT_PUBLIC_* env vars are embedded at BUILD time, not runtime. Must export dynamically BEFORE `pnpm build`, not hardcode in source. Example: `export NEXT_PUBLIC_BUILD_VERSION=$(date '+%Y-%m-%d %H:%M:%S') && pnpm build`. Sprint 2026-01-11: Boss saw old timestamp despite new build because value was hardcoded.

[infra-00008] helpful=1 harmful=0 :: CLAUDE.md is the single source of truth for agent initialization. Keep critical startup instructions in CLAUDE.md (loaded automatically by Claude Code), not in SessionStart hooks. Hooks add complexity and duplicate what CLAUDE.md already provides. Sprint 2026-01-11: Deleted redundant SessionStart hook.

---

## Role Boundary Patterns

[role-00001] helpful=10 harmful=0 :: FE owns frontend ONLY (port 3334). BE owns backend ONLY (port 17061). Cross-service restarts MUST coordinate through SM.

[role-00002] helpful=8 harmful=0 :: PO owns requirements (WHAT). SM facilitates process (HOW). TL designs architecture. FE/BE implement. QA validates.

[role-00003] helpful=7 harmful=0 :: QA does BLACKBOX testing only - test from browser like real user. QA does NOT look at code or implementation details.

[role-00004] helpful=6 harmful=0 :: Boss sends requirements to PO, not SM. PO is bridge between stakeholders and team.

[role-00005] helpful=5 harmful=0 :: "Add to backlog" from Boss = ONLY add to backlog, NOT execute. No execution until Boss explicitly assigns.

[role-00006] helpful=1 harmful=0 :: Backlog management is 100% PO's responsibility. SM has NO role in backlog - no notifications, no tracking. SM only gets involved AFTER PO defines sprint from backlog items. Boss quote: "When you write a task into the backlog, it has nothing to do with the Scrum Master at all."

---

## Retrospective Patterns

[retro-00001] helpful=6 harmful=0 :: Be EXTREMELY selective in retro action items: 0 fixes is normal, 1 is ideal, 2 is MAX. Never force fixes.

[retro-00002] helpful=5 harmful=0 :: AI agents lose context between sessions. SM must record issues IN REAL-TIME during sprint, not ask agents later.

[retro-00003] helpful=4 harmful=0 :: Verbal reminders are forgotten by AI agents. If issue repeats after reminders, update role prompt (*_PROMPT.md) to enforce permanently.

[retro-00004] helpful=3 harmful=0 :: Two-phase retro: Phase 1 (auto, after PO accepts) for team process. Phase 2 (conditional) only if Boss feedback reveals new issues.

[retro-00005] helpful=1 harmful=0 :: AI teams move MUCH faster than human teams - multiple sprints per day possible. Always include exact time (HH:MM) in timestamps, not just date. Sprint Start/End times essential for tracking.

[retro-00006] helpful=1 harmful=0 :: WHITEBOARD must be reset to clean template after each sprint ends. It's for CURRENT sprint only - not historical records. 1000+ lines = failure. Keep just the template structure.

---

## Bullet Management

**Last Updated:** 2026-01-12 (Added [code-00010] - fetch binding bug from Sprint 6 SOLID refactoring)

**Next Bullet IDs:**
- comm-00006
- sprint-00006
- code-00011
- infra-00009
- role-00007
- retro-00007

**Promotion Threshold:** Bullets with helpful >= 10 and harmful = 0 should be considered for permanent inclusion in role prompts.

**Pruning Threshold:** Bullets with harmful >= helpful should be reviewed and potentially removed.

---

## How to Update (SM Workflow)

### After Each Sprint Retrospective:

1. **Reflector Step**: Identify NEW lessons from sprint
   - What succeeded that we should repeat?
   - What failed that we should avoid?
   - What pattern emerged?

2. **Curator Step**: Create delta bullets
   - Check if lesson already exists (avoid duplication)
   - If new: add bullet with helpful=1, harmful=0
   - If exists: increment helpful or harmful counter

3. **Grow-and-Refine**:
   - Append new bullets with fresh IDs
   - Update counters on existing bullets
   - Prune bullets where harmful >= helpful

4. **Promote High-Value Bullets**:
   - Bullets with helpful >= 10, harmful = 0 → add to role prompts
   - This makes the lesson permanent across sessions

---

## Example: Adding a New Lesson

Sprint 16 retrospective reveals: "BE forgot to restart Celery after changing TTS code, causing voice feedback to use old logic for 2 hours."

**Reflector Analysis:**
- Root cause: Celery doesn't auto-reload
- Similar lesson exists? Check [code-00002] - YES, already documented

**Curator Action:**
- Increment [code-00002] helpful counter: helpful=8 → helpful=9
- No new bullet needed (lesson already captured)

**If lesson was NEW:**
```
[code-00005] helpful=1 harmful=0 :: After changing TTS provider code, verify voice feedback works by testing end-to-end, not just unit tests.
```
