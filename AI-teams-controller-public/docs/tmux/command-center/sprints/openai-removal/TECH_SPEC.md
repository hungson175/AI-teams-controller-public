# Technical Spec: OpenAI Code Removal

## Overview

Remove ALL OpenAI Realtime API code from codebase. System now uses Soniox for STT (speech-to-text) exclusively.

## Scope Summary

| Component | Files to Modify | Action |
|-----------|-----------------|--------|
| BE: Token endpoint | `token_routes.py` | DELETE `/token` endpoint (keep `/token/soniox`) |
| BE: TTS Provider | `tts_providers.py` | DELETE `OpenAITTSProvider` class |
| BE: Schemas | `voice_schemas.py` | DELETE `EphemeralTokenResponse`, `ClientSecret` |
| BE: Tests | `test_*.py` | DELETE OpenAI-related tests |
| FE: Types | `voice-types.ts` | DELETE all GPT Realtime API types |
| FE: Audio | `audio-capture.ts` | UPDATE comments (remove GPT references) |

## Backend Changes

### 1. DELETE: `/api/voice/token` endpoint
**File:** `backend/app/api/voice_routes/token_routes.py`
- Remove `get_voice_token()` function (lines 48-95)
- Remove `OPENAI_REALTIME_SESSIONS_URL` constant
- Remove `REALTIME_SESSION_CONFIG` constant
- Keep `/token/soniox` endpoint

### 2. DELETE: OpenAITTSProvider
**File:** `backend/app/services/tts_providers.py`
- Remove `@TTSProviderFactory.register("openai")` decorator and class (lines 194-244)
- Update `validate_provider()` to remove "openai" from legacy list (line 176-177)
- Update factory default from "openai" to "google" (lines 121, 150)

### 3. DELETE: OpenAI schemas
**File:** `backend/app/models/voice_schemas.py`
- Remove `ClientSecret` class (lines 19-23)
- Remove `EphemeralTokenResponse` class (lines 26-31)
- Remove import from `token_routes.py`

### 4. DELETE: OpenAI tests
**Files:** `backend/tests/test_tts_providers.py`, `test_voice_routes.py`
- Remove OpenAI TTS provider tests
- Remove `/token` endpoint tests

## Frontend Changes

### 1. DELETE: GPT Realtime API types
**File:** `frontend/lib/voice-types.ts`
- Remove `EphemeralTokenResponse` interface (lines 12-19)
- Remove ALL Realtime API types (lines 24-121):
  - `RealtimeSessionConfig`
  - `AudioBufferAppendMessage`
  - `TranscriptionCompletedEvent`
  - `SessionCreatedEvent`
  - `SessionUpdatedEvent`
  - `RealtimeErrorEvent`
  - `InputAudioBufferSpeechStartedEvent`
  - `InputAudioBufferSpeechStoppedEvent`
  - `RealtimeIncomingEvent`
  - `RealtimeOutgoingMessage`
- Remove `AUDIO_CONFIG` 24000 sampleRate reference (line 195) - update to 16000 only

### 2. UPDATE: Audio capture comments
**File:** `frontend/lib/stt/audio-capture.ts`
- Update header comment: remove "GPT Realtime (24kHz)" reference
- Update `AudioCaptureConfig.sampleRate` type: `16000` only (remove `| 24000`)

## Test Requirements

### Backend Tests (80% coverage required)
1. Verify `/token` returns 404 (endpoint removed)
2. Verify `/token/soniox` still works
3. Verify `TTSProviderFactory.create("openai")` raises ValueError
4. Verify default TTS provider is "google"

### Frontend Tests (70% coverage required)
1. Verify voice-types exports only Soniox-related types
2. Verify AudioCaptureConfig only accepts 16000 sampleRate

## Coordination (BE First, Then FE)

1. **BE removes endpoints/providers** - tests should pass independently
2. **FE removes types** - no breaking changes (Soniox already in use)
3. **Verification:** Both services restart cleanly

## Environment Variables

**Keep for documentation (commented):**
```bash
# backend/.env
# OPENAI_API_KEY=  # Removed - was for GPT Realtime API
```

**Active:**
```bash
SONIOX_API_KEY=xxx  # STT provider (active)
TTS_PROVIDER=google  # Update default from "openai"
```
