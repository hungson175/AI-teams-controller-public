# Technical Spec: Sprint 10 - Android Voice Command App (Complete Flow)

**Goal**: Manual button → record → transcribe → send command (usable product)

---

## Architecture Overview

```
[Record Button] → [MediaRecorder] → audio.wav → [Retrofit] → Backend
                                                     ↓
[Display Text] ← transcription ← /api/voice/transcribe
                                                     ↓
                              /api/send/command-center/PO → tmux pane
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `MainActivity.kt` | Compose UI: Record button, status, transcription display |
| `AudioRecorder.kt` | MediaRecorder wrapper: start/stop, save to temp file |
| `api/BackendApi.kt` | Retrofit interface: transcribe + send endpoints |
| `api/RetrofitClient.kt` | Singleton HTTP client with base URL |
| `AndroidManifest.xml` | RECORD_AUDIO + INTERNET permissions |

---

## API Contracts

### POST /api/voice/transcribe
**Request**: `multipart/form-data` with audio file
**Response**: `{ "transcription": "text here", "success": true }`

### POST /api/send/{team}/{role}
**Request**: `{ "message": "transcribed command" }`
**Response**: `{ "success": true }`

---

## Key Design Decisions

1. **MediaRecorder over AudioRecord** - Simpler API, outputs MP3/AAC directly
2. **No background service** - Keep screen on during recording (FLAG_KEEP_SCREEN_ON)
3. **Hardcoded config** - team=command-center, role=PO, backend URL in BuildConfig
4. **State management** - Single ViewModel with StateFlow for UI state
5. **Permission flow** - Request on app launch, show rationale if denied

---

## UI States

```kotlin
sealed class RecordingState {
    object Idle : RecordingState()
    object Recording : RecordingState()
    object Sending : RecordingState()
    data class Success(val transcription: String) : RecordingState()
    data class Error(val message: String) : RecordingState()
}
```

---

## Security

- API token in BuildConfig (not hardcoded in source)
- HTTPS only (backend URL is https://)
- No sensitive data stored locally

---

## Test Cases (TDD)

**Recording**: Permission granted → record starts → file created
**API**: Audio file sent → transcription received → command forwarded
**Error**: Network failure → show error message → allow retry
**Permission**: Denied → show rationale → retry or exit

---

## Dependencies

- Retrofit 2.9+ (HTTP client)
- Gson converter (JSON parsing)
- Compose Material 3 (UI)
