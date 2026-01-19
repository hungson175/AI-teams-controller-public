# Retrospective - P0 Frontend 500 Errors Sprint 2026-01-11

**Date:** 2026-01-11
**Sprint Start:** 2026-01-10 20:47 (Boss assigned Frontend 500 P0)
**Sprint End:** 2026-01-11 06:53 (Commit pushed, Boss verified)
**Duration:** ~10 hours (with overnight break)
**Commit:** ca163235
**Type:** P0 Sprint (Frontend 500 errors + Voice switch)

---

## Sprint Summary

This sprint addressed two critical issues:
1. **Frontend 500 Errors** - Recurring static chunk errors after rebuilds
2. **Voice Feedback Regression** - HD-TTS random voice (switched to Google TTS)

---

## Frustration Signals (4 total - HIGH)

| Time | Signal | Issue |
|------|--------|-------|
| 20:47 | "fuck, crazy, cursing, tired" | Frontend 500 errors recurring |
| 20:48 | "fuck, shit, fed up" | Voice feedback regression |
| 20:50 | "fuck, stupid as hell, shit, fed up" | Voice gender switching |
| 21:32 | "fuck x3, shit, ghost, fed up, tired" | Voice worse, Boss exhausted |

---

## What Went Well

1. **TL Research** - Thorough root cause analysis, identified 4 causes quickly
2. **FE Implementation** - Phase 1 + Phase 2 completed efficiently
3. **TL Code Review** - Fast and matched spec 100%
4. **QA Testing** - Comprehensive blackbox testing with Playwright
5. **Google TTS Switch** - Quick relief for Boss (5 min fix)
6. **Team Coordination** - SM kept sprint moving, no blockers

---

## What Failed / Issues

### Issue 1: BUILD_VERSION Hardcoded in Source
- **Impact:** Boss saw old timestamp despite new build
- **Root Cause:** NEXT_PUBLIC_BUILD_VERSION not set before build
- **Fix:** Updated restart script to export timestamp dynamically
- **Lesson:** Next.js NEXT_PUBLIC_* vars embedded at BUILD time, not runtime

### Issue 2: HD-TTS Voice Regression
- **Impact:** Random voice switching (male/female), then ghost voice
- **Root Cause:** HD-TTS ONNX CUDA generates random noise (external bug)
- **Fix:** Switched to Google Cloud TTS (deterministic)
- **Lesson:** Have TTS fallback ready when using experimental providers

### Issue 3: Initial Voice Misdiagnosis
- **Impact:** Wasted time investigating cache when issue was API
- **Root Cause:** Assumed cache issue first, didn't test API directly
- **Fix:** BE tested HD-TTS API directly (5 requests → 5 different outputs)
- **Lesson:** Test external APIs directly before assuming cache

---

## Curator Actions

### Added:
- [infra-00007] helpful=1 harmful=0 :: Next.js NEXT_PUBLIC_* env vars are embedded at BUILD time. Must export dynamically BEFORE pnpm build, not hardcode in source. Example: `export NEXT_PUBLIC_BUILD_VERSION=$(date) && pnpm build`

### Updated:
- [infra-00005] helpful=1→2 (Systemd disable/enable pattern used successfully)
- [code-00001] helpful=14→15 (Frontend clean rebuild prevented 500 errors)

---

## Action Items (1 - per retro guidelines)

1. **[infra-00007] NEXT_PUBLIC_* dynamic export** - Added to TEAM_PLAYBOOK
   - High impact: Prevents build timestamp confusion
   - Universal: Applies to all Next.js projects

**NOTE:** 0-1-2 max action items per retro. Single item selected due to direct impact on this sprint.

---

## Boss Feedback (Post-Retro)

**Feedback (06:57):** Timestamps in retrospectives should include exact time (HH:MM), not just date. AI teams move much faster than human teams - multiple sprints can happen in a single day.

**Action:** Added [retro-00005] to TEAM_PLAYBOOK: "AI teams move MUCH faster than human teams - multiple sprints per day possible. Always include exact time (HH:MM) in timestamps."

---

## Phase 2 Retro Needed?

**No.** Boss feedback was positive (build verified, timestamp correct). No new issues revealed during Sprint Review that weren't covered in Phase 1.

---

## Sprint Metrics

| Metric | Value |
|--------|-------|
| Sprint Duration | ~2 hours |
| Frustration Signals | 4 (HIGH) |
| Root Causes Fixed | 4 (systemd race, verification gap, dynamic timestamp, TTS switch) |
| Files Changed | 8 |
| Lines Added | 771 |
