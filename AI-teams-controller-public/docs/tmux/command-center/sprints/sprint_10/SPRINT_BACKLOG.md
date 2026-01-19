# Sprint 10 Backlog - Simplest Complete Flow (Manual Button → Backend)

**Sprint Goal:** Boss can send voice commands and see them work END-TO-END

**Start Date:** 2026-01-03
**Platform:** Android Native (NEW - Kotlin + Jetpack Compose)

---

## What Boss Can Do After This Sprint

- ✅ Open app, press "Record" button
- ✅ Speak a voice command
- ✅ See transcription displayed in app
- ✅ Command sent to backend (command-center team, hardcoded role)
- ✅ **ACTUALLY USABLE - Complete flow works!**

---

## Deliberately OUT OF SCOPE (Save for Later Sprints)

- ❌ NO background service yet (screen must stay on - simpler)
- ❌ NO headphone buttons yet (manual button only - simpler)
- ❌ NO team/role selection yet (hardcoded to command-center/PO - simpler)
- ❌ NO TTS feedback yet (just shows text - simpler)

---

## Why This Approach

- **Product-Oriented**: Boss has working app after Sprint 10, not after Sprint 12
- **Progressive**: Start simple (manual button, screen on), add complexity later
- **Risk Reduction**: Validate backend integration early, not in Sprint 12

---

## Reference Projects for TL Study

TL should study these before creating specs:
- `sample_codes/Demo_CleanEmptyCompose` - Minimal Compose project template
- `sample_codes/AudioRecorder` - Retrofit HTTP client setup
- `sample_codes/Android-Wave-Recorder` - Basic audio recording (simplified version, no background yet)

---

## Deliverables

- [ ] Android project created (Kotlin + Jetpack Compose)
- [ ] Simple UI: "Record" button (NO background service yet)
- [ ] Record audio (5-second button press, screen stays on)
- [ ] Send to backend: `POST /api/voice/transcribe`
- [ ] Display transcription text in UI
- [ ] Send command to hardcoded team/role: `POST /api/send/command-center/PO`

---

## Acceptance Criteria

**Permission Handling:**
- [ ] App requests RECORD_AUDIO permission on first launch
- [ ] Permission denied → show explanation and exit gracefully

**Recording:**
- [ ] "Record" button starts recording (5 seconds or until released)
- [ ] Screen stays on during recording (no background service)
- [ ] Visual feedback: button state changes during recording

**Backend Integration:**
- [ ] Audio sent to `https://voice-backend.hungson175.com/api/voice/transcribe`
- [ ] Transcription text received and displayed in UI
- [ ] Command automatically sent to `POST /api/send/command-center/PO`
- [ ] Success/error messages shown to user

**Usability:**
- [ ] **BOSS CAN USE: Send voice commands and see them work!**
- [ ] Error handling: Network failures, permission denials, transcription errors
- [ ] Clean UI: Material 3 design, clear status messages

---

## Files to Create

### Android App Structure
```
android-app/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── kotlin/com/aiteams/
│   │       │   ├── MainActivity.kt          # Main activity with Record button
│   │       │   ├── AudioRecorder.kt         # Simple recording (NO foreground service)
│   │       │   └── api/
│   │       │       └── BackendApi.kt        # Retrofit interface
│   │       └── AndroidManifest.xml          # Basic permissions only
│   └── build.gradle.kts
└── build.gradle.kts
```

---

## Technical Stack

- **Language:** Kotlin 1.9+
- **UI:** Jetpack Compose (Material 3)
- **HTTP Client:** Retrofit for API calls
- **Audio Recording:** MediaRecorder (simple, no AudioRecord yet)
- **Target:** Android 14 (API 34)
- **Build Tool:** Gradle with Kotlin DSL

### Hardcoded Values (For Sprint 10 Simplicity)
- Backend URL: `https://voice-backend.hungson175.com`
- API token: From environment or hardcoded
- Team: `command-center`
- Role: `PO`

---

## Notes for Team

**NEW PLATFORM:** This is the team's first Android native app. TL needs time to:
1. Study reference projects in `sample_codes/`
2. Understand Android architecture (Activity, Permissions, UI)
3. Learn Kotlin + Jetpack Compose patterns
4. Learn Retrofit HTTP client setup
5. Create comprehensive specs for FE (Android developer role)

**PRODUCT-ORIENTED APPROACH:**
- Sprint 10: Complete flow (manual button → backend) - USABLE PRODUCT ✅
- Sprint 11: Background operation (foreground service, wake lock)
- Sprint 12: Headphone buttons (media controls)
- Sprint 13: TTS feedback (voice responses)
- Sprint 14: Team/role selection + polish

**Focus:** Get complete flow working FIRST. Boss can use app after Sprint 10, not Sprint 12.
