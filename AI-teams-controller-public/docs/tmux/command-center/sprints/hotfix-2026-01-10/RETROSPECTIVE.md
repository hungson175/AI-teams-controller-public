# Retrospective - Hotfix Session 2026-01-10

**Date:** 2026-01-10
**Commit:** 005ddf06
**Type:** Hotfix session (multiple P0 fixes)

---

## Sprint Summary

This was a hotfix session addressing multiple P0 issues:
1. Terminal paths not working for all sessions (jarvis, command-center)
2. Voice feedback wrong content (Celery cache)
3. TTS audio not playing (HD-TTS auth method)
4. Jarvis voice wrong (TTS file cache)
5. P2: Preserve swear words in voice correction

---

## Frustration Signals (9 total - HIGH)

| Time | Signal | Issue |
|------|--------|-------|
| 12:52 | swearing | Voice feedback duplication/replay |
| 12:55 | what the hell | WHITEBOARD 2263 lines |
| 12:57 | punch you/crappy | SM lazy fix proposal |
| 12:58 | fuck x2 | PO wrong terminology |
| 12:59 | fuck | PO not interpreting typos |
| 13:02 | stupid as a dog | BE/TL removed intentional feature |
| 13:05 | stupid as a pig | Team not checking systemd ports |
| 13:43 | what the fuck | TTS not playing |
| 18:15 | very weird | Jarvis wrong voice |

**Boss acknowledgement:** "Too many hotfixes during sprint (process deviation)"

---

## Failure Analysis

### Issue 1: Multiple Cache Layers Causing Stale Data
- **Celery Redis cache:** 52 stale task results
- **TTS file cache:** 19 old audio files with wrong voice
- **Root cause:** Config changes (TTS provider, voice settings) but caches not cleared
- **Impact:** 2+ hours debugging, Boss frustration

### Issue 2: Wrong Diagnosis Pattern
- SM proposed "debounce fix" without investigating root cause
- TL/BE removed intentional '>' detection feature
- **Root cause:** Jumping to solutions without understanding existing code
- **Impact:** Boss frustration, wasted time on wrong fixes

### Issue 3: API Integration Mismatch
- HD-TTS expected query param auth, code sent header auth
- **Root cause:** API contract not verified during integration
- **Impact:** Audio generation failed silently

---

## Lessons Learned

### NEW: Cache Awareness After Config Changes
After ANY config change (TTS provider, voice settings, environment variables), clear ALL related caches:
- Celery Redis: `redis-cli KEYS "celery-task-meta-*" | xargs redis-cli DEL`
- TTS file cache: `rm -rf backend/cache/tts/`
- Then restart services

### REINFORCED: Understand Before Fixing
The '>' detection was intentional (finds last message start). Team tried to remove it thinking it was a bug.
- Always ask "why does this code exist?" before modifying
- Don't remove code without understanding its purpose

---

## Curator Actions

### Added:
- [infra-00006] helpful=1 harmful=0 :: After TTS/voice config changes, clear ALL caches (Celery Redis + TTS file cache). Stale caches served wrong voice for hours.

### Updated:
- [code-00002] helpful=8→9 (Celery restart reminder - issue recurred)
- [infra-00001] helpful=10→11 (Production restart after changes)

---

## Action Items (1 - per retro guidelines)

1. **[infra-00006] Cache clearing after config changes** - Added to TEAM_PLAYBOOK

**NOTE:** 0-1-2 max action items per retro. Single item selected due to high impact of cache issues this session.

---

## Phase 2 Retro Needed?

**No.** Boss feedback was positive ("all fixes working"). No new issues revealed during Sprint Review that weren't covered in Phase 1.
