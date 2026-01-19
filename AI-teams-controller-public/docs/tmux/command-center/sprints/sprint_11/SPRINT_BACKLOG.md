# Sprint 11 Backlog - WebSocket Streaming + Stop Word Detection

**Sprint Goal**: Replace file-based recording with real-time WebSocket streaming to Soniox, enabling stop word detection

**Epic**: Native Android App (P0) - Sprint 2 of 5
**Started**: 2026-01-03
**Status**: IN PROGRESS

---

## Context

**Why Sprint 11 is Needed:**
- Sprint 10 architecture was fundamentally flawed (MediaRecorder cannot support stop words)
- Boss requires stop word detection ("thank you" to end recording) like web frontend
- Must use AudioRecord + WebSocket streaming instead of file upload

**Key Difference from Sprint 10:**

| Aspect | Sprint 10 (CANCELLED) | Sprint 11 (REQUIRED) |
|--------|----------------------|----------------------|
| API | MediaRecorder (high-level) | AudioRecord (low-level) |
| Mode | File-based recording | Real-time streaming |
| Stop trigger | Manual button release | Stop word ("thank you") |
| Duration | 5-second timer | Continuous until stop word |
| Backend | File upload to /api/voice/transcribe | WebSocket to Soniox |

---

## Technical Spec

**Location**: `docs/tmux/command-center/sprints/sprint_11/TL_SPEC.md`

**Key Architecture:**
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

## Work Items (FE - Android Developer)

### 1. AudioRecord Low-Level Capture (M)

**File**: `android/app/src/main/java/com/aicontroller/voicecommand/audio/AudioRecordCapture.kt`

**Requirements:**
- Initialize AudioRecord with 16kHz, mono, PCM16
- Capture raw audio chunks in background coroutine
- Provide flow/callback for audio data
- Handle permissions and lifecycle

**Test Cases (TDD):**
1. Start recording → Get PCM chunks → Verify format (16kHz, PCM16)
2. Stop recording → AudioRecord released
3. Permission denied → Error handling

**Acceptance Criteria:**
- [ ] AudioRecord initialized with correct parameters (16kHz, mono, PCM16)
- [ ] Audio chunks captured in background (not blocking UI)
- [ ] Start/stop lifecycle managed correctly
- [ ] Tests pass before implementation commit

---

### 2. Soniox WebSocket Streaming Service (M)

**File**: `android/app/src/main/java/com/aicontroller/voicecommand/services/SonioxStreamingService.kt`

**Requirements:**
- Connect to `wss://stt-rt.soniox.com/transcribe-websocket`
- Send JSON config first message (API key, sample rate, format)
- Stream binary audio chunks
- Receive and parse transcript responses
- Expose transcript flow for UI/ViewModel

**WebSocket Protocol (Same as Web Frontend):**

1. **Connect**: `wss://stt-rt.soniox.com/transcribe-websocket`

2. **First Message** (JSON):
   ```json
   {
     "api_key": "...",
     "model": "stt-rt-preview",
     "sample_rate": 16000,
     "num_channels": 1,
     "audio_format": "pcm_s16le"
   }
   ```

3. **Subsequent Messages**: Binary PCM chunks

4. **Response Format**:
   ```json
   { "tokens": [{ "text": "hello ", "is_final": true }] }
   ```

**Get API Token From Backend:**
```kotlin
GET https://voice-backend.hungson175.com/api/voice/token/soniox
```

**Test Cases (TDD):**
1. Connect → Verify WebSocket opened
2. Send config message → Verify format
3. Stream audio chunk → Verify sent as binary
4. Receive transcript → Parse JSON correctly
5. Connection closed → Graceful cleanup

**Acceptance Criteria:**
- [ ] WebSocket connects successfully to Soniox
- [ ] Config message sent correctly (JSON with API key)
- [ ] Audio chunks streamed as binary
- [ ] Transcripts received and parsed
- [ ] Connection lifecycle managed (open/close/error)
- [ ] Tests pass before implementation commit

---

### 3. Stop Word Detector (S)

**File**: `android/app/src/main/java/com/aicontroller/voicecommand/utils/StopWordDetector.kt`

**Requirements:**
- Check if transcript ends with "thank you"
- Extract command text (everything before stop word)
- Case-insensitive matching

**Logic:**
```kotlin
fun checkStopWord(transcript: String, stopWord: String = "thank you"): Boolean {
    return transcript.lowercase().trim().endsWith(stopWord)
}

fun extractCommand(transcript: String, stopWord: String = "thank you"): String {
    val lower = transcript.lowercase()
    return if (lower.endsWith(stopWord)) {
        transcript.substring(0, transcript.length - stopWord.length).trim()
    } else {
        transcript
    }
}
```

**Test Cases (TDD):**
1. "fix bug thank you" → detected=true, command="fix bug"
2. "thank you" → detected=true, command="" (empty)
3. "fix bug" → detected=false, command="fix bug"
4. "THANK YOU" (uppercase) → detected=true
5. "  fix bug thank you  " (whitespace) → detected=true, command="fix bug"

**Acceptance Criteria:**
- [ ] Stop word detected case-insensitively
- [ ] Command text extracted correctly
- [ ] Edge cases handled (empty, whitespace, uppercase)
- [ ] Tests pass before implementation commit

---

### 4. Update ViewModel for Streaming (M)

**File**: `android/app/src/main/java/com/aicontroller/voicecommand/viewmodel/MainViewModel.kt`

**Changes:**
- Replace MediaRecorder + file upload with AudioRecord + WebSocket
- Add `Connecting` and `Listening` states
- Stream audio chunks to SonioxStreamingService
- Accumulate transcript from WebSocket responses
- Detect stop word → Send command to backend
- Handle errors (connection failures, API errors)

**Updated State Machine:**
```kotlin
sealed class RecordingState {
    object Idle : RecordingState()
    object Connecting : RecordingState()      // NEW: Connecting to Soniox
    object Listening : RecordingState()       // NEW: Streaming, awaiting stop word
    object Processing : RecordingState()      // Sending command to backend
    data class Success(val transcription: String) : RecordingState()
    data class Error(val message: String) : RecordingState()
}
```

**Flow:**
1. User presses "Record" → State = Connecting
2. WebSocket connected → State = Listening
3. Audio chunks streamed → Transcript accumulates
4. Stop word detected → State = Processing
5. Command sent → State = Success
6. Error → State = Error

**Test Cases (TDD):**
1. Start recording → Connecting → Listening states
2. Receive transcript → UI updated
3. Stop word detected → Command extracted and sent
4. Connection fails → Error state
5. Stop word not detected → Keeps listening

**Acceptance Criteria:**
- [ ] Old MediaRecorder code removed
- [ ] AudioRecord + WebSocket integrated
- [ ] State machine updated (Connecting, Listening states)
- [ ] Transcript accumulation works
- [ ] Stop word detection triggers command send
- [ ] Error handling for connection failures
- [ ] Tests pass before implementation commit

---

### 5. Update UI for Streaming States (S)

**File**: `android/app/src/main/java/com/aicontroller/voicecommand/MainActivity.kt`

**Changes:**
- Show "Connecting..." when establishing WebSocket
- Show "Listening... (say 'thank you' when done)" during recording
- Display transcript in real-time (not just on success)
- Keep screen on during Listening state

**UI States:**

| State | Button Text | Status Text | Screen On |
|-------|-------------|-------------|-----------|
| Idle | "Record" | Ready | No |
| Connecting | "Connecting..." | Establishing connection | Yes |
| Listening | "Listening..." | "Say 'thank you' when done" + transcript | Yes |
| Processing | "Sending..." | "Sending command..." | Yes |
| Success | "Record" | Transcription + confirmation | No |
| Error | "Record" | Error message | No |

**Acceptance Criteria:**
- [ ] UI shows correct state for Connecting/Listening
- [ ] Transcript displays in real-time (not just on completion)
- [ ] Instructions clear: "Say 'thank you' when done"
- [ ] Screen stays on during Connecting/Listening/Processing
- [ ] Visual feedback polished (loading indicators)

---

## Test Strategy

### Unit Tests (JUnit + Mockito)
- AudioRecordCapture - Mock AudioRecord, verify PCM chunks
- SonioxStreamingService - Mock WebSocket, verify protocol
- StopWordDetector - Pure logic, no mocks needed
- MainViewModel - Mock services, verify state machine

### Integration Tests (Optional - if time permits)
- End-to-end: Record → Stream → Detect stop word → Send command
- Requires real Soniox API (or mock server)

### Manual Testing (QA)
- Test on Android emulator
- Speak voice command + "thank you"
- Verify transcript displays in real-time
- Verify command sent to backend
- Test error scenarios (no network, invalid API key)

---

## Dependencies

**Already in Project:**
- OkHttp 4.x (via Retrofit) - WebSocket support included
- Kotlin Coroutines - Background audio processing
- Jetpack Compose - UI layer

**No New Dependencies Required** ✅

---

## Acceptance Criteria (Sprint 11)

### AC1: Real-time Audio Streaming ✅
- [ ] AudioRecord captures audio at 16kHz PCM16
- [ ] Audio chunks streamed to Soniox via WebSocket
- [ ] No file creation (pure streaming)

### AC2: WebSocket Connection ✅
- [ ] Connect to `wss://stt-rt.soniox.com/transcribe-websocket`
- [ ] Send JSON config first message
- [ ] Binary audio chunks sent
- [ ] Transcript responses received

### AC3: Real-time Transcript Display ✅
- [ ] Transcript updates in UI as words arrive
- [ ] User can see what's being recognized live

### AC4: Stop Word Detection ✅
- [ ] Saying "thank you" ends recording
- [ ] Command extracted (everything before "thank you")
- [ ] Works case-insensitively

### AC5: Command Sent to Backend ✅
- [ ] Extracted command sent to `POST /api/send/command-center/PO`
- [ ] Same backend integration as Sprint 10

### AC6: UI States ✅
- [ ] "Connecting..." shown during WebSocket setup
- [ ] "Listening... (say 'thank you' when done)" during recording
- [ ] Transcript visible in real-time
- [ ] Screen stays on during recording

### AC7: Error Handling ✅
- [ ] Network errors shown to user
- [ ] WebSocket disconnection handled gracefully
- [ ] Invalid API key detected and reported

### AC8: Boss Can Use It ✅
- [ ] Open app, press "Record"
- [ ] Speak: "fix the bug in the login screen"
- [ ] Say: "thank you"
- [ ] Command appears in PO's tmux pane
- [ ] No crashes, professional UX

---

## Migration Notes

**Remove from Sprint 10:**
- `MediaRecorder` usage
- File-based recording logic
- 5-second timer
- File upload to `/api/voice/transcribe`

**Keep from Sprint 10:**
- Material 3 UI structure
- Permission handling (RECORD_AUDIO)
- Backend integration (`/api/send/command-center/PO`)
- Screen wake lock (FLAG_KEEP_SCREEN_ON)

---

## Reference

**Web Frontend Implementation:**
- `frontend/hooks/useVoiceRecorder.ts` - WebSocket streaming to Soniox
- Study how web frontend does:
  - WebSocket connection
  - Binary audio chunk streaming
  - Stop word detection
  - Transcript accumulation

**TL Spec:**
- `sprints/sprint_11/TL_SPEC.md` - Full technical design

---

## Team Assignments

| Role | Assigned Work | Status |
|------|--------------|--------|
| FE | Implement all 5 work items (AudioRecord, WebSocket, StopWord, ViewModel, UI) | ⏳ ASSIGNED |
| TL | Code review when FE completes | ⏳ Ready |
| QA | Blackbox testing with Android emulator | ⏳ Ready |

---

## Timeline Estimate

| Task | Effort | Notes |
|------|--------|-------|
| AudioRecord capture | M | Similar to MediaRecorder, but lower-level |
| WebSocket service | M | Core complexity, follow web frontend pattern |
| Stop word detector | S | Simple utility, mostly tests |
| ViewModel update | M | State machine changes, integration |
| UI updates | S | Polish states and messaging |

**Total Estimate**: M-L sprint (larger than Sprint 10 due to architecture change)

---

## Definition of Done

- [ ] All 8 acceptance criteria met
- [ ] All unit tests passing (TDD: tests first, code after)
- [ ] TL code review passed
- [ ] QA blackbox testing passed
- [ ] Boss can record voice commands with stop word
- [ ] Commands appear in PO's tmux pane
- [ ] No crashes, clean logs, professional UX
- [ ] Code committed to git (progressive commits)

---

**Sprint 11 Ready for Execution**
