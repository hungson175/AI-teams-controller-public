# Technical Spec: Sprint 11 - WebSocket Streaming + Stop Word Detection

**Goal**: Real-time streaming to Soniox with stop word detection (like web frontend)

---

## Architecture Overview

```
[AudioRecord] → 16kHz PCM16 → [OkHttp WebSocket] → Soniox
                                                      ↓
                                           Real-time transcription
                                                      ↓
                                          [StopWordDetector]
                                                      ↓
                                    ("thank you" detected) → Send command
```

---

## Key Design Decisions

1. **AudioRecord over MediaRecorder** - Low-level API gives raw PCM data for streaming
2. **OkHttp WebSocket** - Already in project (Retrofit uses OkHttp), battle-tested
3. **Soniox protocol** - JSON config first, then binary audio chunks (same as web)
4. **Stop word detection** - Client-side, check transcript ends with "thank you"
5. **Coroutines** - Background audio capture, IO for WebSocket, Main for UI

---

## Files to Create/Modify

| File | Purpose |
|------|---------|
| `AudioRecordCapture.kt` | Low-level audio capture (16kHz, mono, PCM16) |
| `SonioxStreamingService.kt` | WebSocket connection + audio streaming |
| `StopWordDetector.kt` | Detect "thank you" at end of transcript |
| `MainViewModel.kt` | MODIFY: Use streaming instead of file upload |
| `RecordingState.kt` | ADD: `Listening` state for continuous mode |

---

## Soniox WebSocket Protocol (Same as Web)

### Connect
```
wss://stt-rt.soniox.com/transcribe-websocket
```

### First Message (JSON)
```json
{
  "api_key": "...",
  "model": "stt-rt-preview",
  "sample_rate": 16000,
  "num_channels": 1,
  "audio_format": "pcm_s16le"
}
```

### Subsequent Messages
Binary audio chunks (Int16 PCM data)

### Response Format
```json
{ "tokens": [{ "text": "hello ", "is_final": true }] }
```

---

## Audio Capture (AudioRecord)

```kotlin
val recorder = AudioRecord(
    MediaRecorder.AudioSource.MIC,
    16000,  // sample rate
    AudioFormat.CHANNEL_IN_MONO,
    AudioFormat.ENCODING_PCM_16BIT,
    bufferSize
)
```

---

## Stop Word Detection Logic

```kotlin
fun checkStopWord(transcript: String, stopWord: String = "thank you"): Boolean {
    return transcript.lowercase().trim().endsWith(stopWord)
}
```

---

## UI States (Updated)

```kotlin
sealed class RecordingState {
    object Idle : RecordingState()
    object Connecting : RecordingState()
    object Listening : RecordingState()  // NEW: Streaming, awaiting stop word
    object Processing : RecordingState() // Sending command
    data class Success(val transcription: String) : RecordingState()
    data class Error(val message: String) : RecordingState()
}
```

---

## Test Cases (TDD)

1. **AudioRecordCapture**: Start → Get PCM chunks → Stop
2. **SonioxStreamingService**: Connect → Send config → Stream → Receive transcripts
3. **StopWordDetector**: "fix bug thank you" → detected=true, command="fix bug"
4. **Integration**: Speak → See transcript → Say "thank you" → Command sent

---

## Dependencies

- OkHttp 4.x (already via Retrofit)
- Kotlin Coroutines (already in project)
- No new dependencies needed

---

## Migration from Sprint 10

| Sprint 10 | Sprint 11 |
|-----------|-----------|
| MediaRecorder (file) | AudioRecord (streaming) |
| Upload file after stop | Stream in real-time |
| Manual button release | Stop word detection |
| 5-second timer | Continuous until "thank you" |

---

## API Token

Get Soniox API key from backend: `GET /api/voice/token/soniox`
(Same endpoint web frontend uses)
