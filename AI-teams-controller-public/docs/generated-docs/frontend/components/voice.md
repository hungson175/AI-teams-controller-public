# Voice Components

Voice command UI components.

## Overview

Components for voice recording, transcription, and feedback.

**Location:** `frontend/components/voice/`

## Components

| Component | Purpose |
|-----------|---------|
| `VoiceCommand.tsx` | Main mic button, transcript display |
| `VoiceInputToggle.tsx` | Voice recording toggle |
| `VoiceOutputToggle.tsx` | 3-mode feedback selector |
| `VoiceNotificationPanel.tsx` | Notification history sheet |
| `VoiceSettingsPanel.tsx` | Voice settings UI |
| `HandsFreeToggle.tsx` | Hands-free mode toggle |

## VoiceOutputToggle Modes

| Mode | Icon | Behavior |
|------|------|----------|
| Voice | Volume2 | Full TTS audio feedback |
| Off | VolumeX | Silent (no audio) |
| Tone | Bell | Cat meow notification sound |

Cycles: Voice → Off → Tone → Voice

## Usage

```tsx
<VoiceCommand
  teamId="command-center"
  roleId="pane-0"
/>
```

## Voice Command Flow

1. User clicks mic button → `startRecording()`
2. Audio streams to Soniox WebSocket
3. Real-time transcript displayed
4. Stop word detected → sends to backend for correction
5. Corrected command → sent to tmux
6. Claude completes → voice feedback plays

## Hands-Free Mode

When enabled:
- Recording restarts automatically after command sent
- Screen stays on (Wake Lock API)
- Ideal for continuous voice interaction

## Stop Word

Default: "thank you"

Customizable in Settings. When detected:
- Recording pauses
- Transcript sent for LLM correction
- Command sent to selected pane
