# Android App Research - Reference Projects
**Date:** 2026-01-03
**Purpose:** Identify high-quality reference implementations for hands-free voice Android app

---

## Executive Summary

**Goal:** Build native Android app (Kotlin) for hands-free voice control of AI teams with headphone button support and background operation.

**Research Scope:**
- Voice recording apps
- Foreground services (background operation)
- MediaSession API (headphone buttons)
- Voice assistant apps (combined features)
- Jetpack Compose UI (minimal UI)

**Top Recommendations:**
1. **Dicio** - Voice assistant with skill architecture
2. **Android-Wave-Recorder** - Low-level audio recording
3. **PlaylistCore** - MediaSession implementation
4. **Demo_CleanEmptyCompose** - Minimal Compose starter

---

## Recommended Projects to Clone

### 1. Voice Recording

#### **Android-Wave-Recorder** ⭐ PRIMARY CHOICE
**GitHub:** https://github.com/squti/Android-Wave-Recorder
**Stars:** 276 | **Last Update:** March 2025 | **Active:** ✅

**Why Clone This:**
- Uses AudioRecord API directly (more control than MediaRecorder)
- Built-in silence detection (critical for voice apps)
- Real-time amplitude monitoring
- Memory-efficient design
- Pure Kotlin library

**What to Extract:**
- Low-level audio recording implementation
- Silence detection patterns
- Real-time audio processing
- WAV format encoding

**Clone Command:**
```bash
cd sample_codes
git clone https://github.com/squti/Android-Wave-Recorder.git
```

---

#### **Dimowner/AudioRecorder** (Full App Reference)
**GitHub:** https://github.com/Dimowner/AudioRecorder
**Stars:** 904 | **Last Update:** October 2024 | **Active:** ✅

**Why Clone This:**
- Complete app architecture (Compose + Hilt + Room)
- Modern Android stack
- File storage handling (scoped storage)
- UI/UX patterns for recording apps

**What to Extract:**
- App architecture patterns
- Room database integration
- File management
- Jetpack Compose UI structure

**Clone Command:**
```bash
cd sample_codes
git clone https://github.com/Dimowner/AudioRecorder.git
```

---

### 2. Foreground Service (Background Operation)

#### **Background Audio Recording Pattern** ⭐ PRIMARY CHOICE
**Source:** https://gist.github.com/Venryx/e1f772b4c05b2da08e118ccd5cc162ff

**Why Use This:**
- Updated for Android 14+ (modern compliance)
- Uses `android:foregroundServiceType="microphone"`
- Correct permission model (FOREGROUND_SERVICE_MICROPHONE)
- Background recording with screen off

**What to Extract:**
- Manifest configuration for microphone service
- Required permissions for Android 14+
- `startForeground()` with service type flag
- Wake lock implementation

**Key Code Pattern:**
```kotlin
startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
```

**Required Permissions:**
```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
```

**Download:**
```bash
# Download as reference file
curl -o sample_codes/android-background-audio-pattern.kt \
  "https://gist.githubusercontent.com/Venryx/e1f772b4c05b2da08e118ccd5cc162ff/raw"
```

---

### 3. MediaSession API (Headphone Buttons)

#### **PlaylistCore** ⭐ PRIMARY CHOICE
**GitHub:** https://github.com/brianwernick/PlaylistCore
**Stars:** 89 | **Last Update:** September 2023 | **Active:** ✅

**Why Clone This:**
- Production-ready MediaSession implementation
- Full Bluetooth headset support
- Lock screen controls
- Comprehensive media button handling

**What to Extract:**
- `DefaultMediaSessionProvider.kt` - MediaSession setup
- Media button receiver patterns
- Notification controls
- Bluetooth device integration

**Clone Command:**
```bash
cd sample_codes
git clone https://github.com/brianwernick/PlaylistCore.git
```

---

### 4. Voice Assistant (Combined Features)

#### **Dicio Android** ⭐ PRIMARY CHOICE
**GitHub:** https://github.com/Stypox/dicio-android
**Stars:** Not specified | **Active:** ✅

**Why Clone This:**
- Skill-based architecture (maps to agent roles!)
- On-device voice processing (Vosk STT)
- Wake word system for hands-free
- Jetpack Compose UI
- Pattern matching for command routing (YAML)

**What to Extract:**
- Skill architecture pattern
- Wake word implementation
- On-device STT integration (Vosk)
- Command routing via YAML patterns
- Jetpack Compose voice UI

**Key Files to Study:**
```
app/src/main/kotlin/org/stypox/dicio/skills/ - Skill implementations
app/src/main/sentences/ - Voice command patterns (YAML)
StandardRecognizerSkill<T> - Base class for voice skills
```

**Clone Command:**
```bash
cd sample_codes
git clone https://github.com/Stypox/dicio-android.git
```

---

#### **Voice Panel Android** (Wake Lock Reference)
**GitHub:** https://github.com/thanksmister/voice-panel-android

**Why Clone This:**
- Wake lock management
- Persistent background service
- Multi-modal wake (voice + face detection)
- Home Assistant integration (similar to tmux routing)

**What to Extract:**
- Wake lock implementation
- Foreground service patterns
- MQTT publishing (message routing architecture)

**Clone Command:**
```bash
cd sample_codes
git clone https://github.com/thanksmister/voice-panel-android.git
```

---

### 5. Jetpack Compose UI

#### **Demo_CleanEmptyCompose** ⭐ PRIMARY CHOICE
**GitHub:** https://github.com/vinchamp77/Demo_CleanEmptyCompose

**Why Clone This:**
- Minimal Material 3 setup
- No unnecessary boilerplate
- Modern build configuration
- Clean starting point

**What to Extract:**
- Project structure
- Gradle setup
- Material 3 configuration

**Clone Command:**
```bash
cd sample_codes
git clone https://github.com/vinchamp77/Demo_CleanEmptyCompose.git
```

---

#### **ComposePrefs** (Settings UI)
**GitHub:** https://github.com/JamalMulla/ComposePrefs

**Why Clone This:**
- Ready-made preference components
- DropDownPref for TTS provider selection
- EditTextPref for API keys
- DataStore integration

**What to Extract:**
- Settings screen patterns
- Preference components
- DataStore persistence

**Clone Command:**
```bash
cd sample_codes
git clone https://github.com/JamalMulla/ComposePrefs.git
```

---

## Feature Mapping to Reference Projects

| Feature Needed | Reference Project | Specific Component |
|----------------|-------------------|-------------------|
| **Voice Recording** | Android-Wave-Recorder | AudioRecord wrapper, silence detection |
| **Background Service** | Background Audio Pattern (Gist) | Foreground service with microphone type |
| **Wake Lock** | Voice Panel Android | Wake lock manager |
| **Headphone Buttons** | PlaylistCore | MediaSession provider |
| **Command Routing** | Dicio | Skill architecture |
| **UI (Settings)** | ComposePrefs | Preference composables |
| **UI (Minimal)** | Demo_CleanEmptyCompose | Project template |
| **App Architecture** | Dimowner/AudioRecorder | Compose + Hilt + Room |

---

## Progressive Development Plan

### Phase 1: Foundation (Sprint 1)
**Goal:** Basic voice recording with screen off

**Reference Projects:**
- Android-Wave-Recorder (recording)
- Background Audio Pattern (foreground service)
- Demo_CleanEmptyCompose (UI base)

**Deliverables:**
- Project setup (Kotlin + Compose)
- Foreground service running
- Mic recording works with screen off
- Simple start/stop UI

---

### Phase 2: Headphone Buttons (Sprint 2)
**Goal:** Control recording with headphone buttons

**Reference Projects:**
- PlaylistCore (MediaSession)

**Deliverables:**
- MediaSession setup
- Play/pause button toggles recording
- Bluetooth headset support

---

### Phase 3: Backend Integration (Sprint 3)
**Goal:** Send audio to backend, receive TTS

**Reference Projects:**
- Dicio (command routing patterns)

**Deliverables:**
- POST audio to backend API
- WebSocket for TTS feedback
- Audio playback through headphones

---

### Phase 4: Team/Role Selection (Sprint 4)
**Goal:** UI for team and role selection

**Reference Projects:**
- ComposePrefs (dropdown UI)

**Deliverables:**
- Team dropdown
- Role dropdown
- Settings persistence

---

### Phase 5: Polish (Sprint 5)
**Goal:** Production-ready app

**Reference Projects:**
- Dimowner/AudioRecorder (production patterns)

**Deliverables:**
- Error handling
- Battery optimization
- Connection status
- Settings screen

---

## Technical Stack Summary

Based on research findings, recommended stack:

**Language:** 100% Kotlin
**UI:** Jetpack Compose (Material 3)
**DI:** Hilt (from Dimowner)
**Storage:** DataStore (from ComposePrefs)
**Audio:** AudioRecord API (from Wave-Recorder)
**Service:** Foreground Service with microphone type (from Gist pattern)
**Media:** MediaSession API (from PlaylistCore)
**HTTP:** Retrofit (standard)
**WebSocket:** OkHttp WebSocket (standard)

---

## Clone All Commands

```bash
# Create sample_codes directory if not exists
mkdir -p sample_codes
cd sample_codes

# Core references (clone these first)
git clone https://github.com/squti/Android-Wave-Recorder.git
git clone https://github.com/Stypox/dicio-android.git
git clone https://github.com/brianwernick/PlaylistCore.git
git clone https://github.com/vinchamp77/Demo_CleanEmptyCompose.git

# Additional references (clone if needed)
git clone https://github.com/Dimowner/AudioRecorder.git
git clone https://github.com/thanksmister/voice-panel-android.git
git clone https://github.com/JamalMulla/ComposePrefs.git

# Download gist pattern
curl -o android-background-audio-pattern.kt \
  "https://gist.githubusercontent.com/Venryx/e1f772b4c05b2da08e118ccd5cc162ff/raw"
```

---

## Key Insights

1. **Don't reinvent the wheel** - Use Android-Wave-Recorder for core recording logic
2. **Follow modern Android** - Android 14+ requires `FOREGROUND_SERVICE_MICROPHONE`
3. **Skill architecture works** - Dicio's approach maps perfectly to agent roles
4. **MediaSession is mature** - PlaylistCore shows production-ready patterns
5. **Keep UI minimal** - Demo_CleanEmptyCompose + ComposePrefs is enough

---

## Next Steps

1. ✅ Research complete (this document)
2. ⏳ Clone reference projects to sample_codes/
3. ⏳ Refine backlog item with concrete sprint plan
4. ⏳ Create Sprint 1 technical spec (foundation)
