# Voice Hooks

React hooks for voice recording and STT.

## useVoiceRecorder

Main hook for hands-free voice recording with Soniox STT.

**Location:** `frontend/hooks/useVoiceRecorder.ts`

```tsx
const {
  state,           // VoiceState
  isRecording,     // boolean
  startRecording,  // (teamId, roleId) => Promise<void>
  stopRecording,   // () => void
  clearTranscript, // () => void
  canRecord,       // boolean
  canClear,        // boolean
} = useVoiceRecorder()
```

## VoiceState

```typescript
interface VoiceState {
  status: VoiceStatus
  transcript: string
  correctedCommand: string
  error: string | null
  isSpeaking: boolean
  feedbackSummary: string
  isPlayingFeedback: boolean
}

type VoiceStatus =
  | "idle"        // Not recording
  | "connecting"  // Getting token / connecting WebSocket
  | "listening"   // Recording and streaming audio
  | "processing"  // Stop word detected, sending to backend
  | "correcting"  // Backend LLM correction in progress
  | "sent"        // Command sent to tmux
  | "speaking"    // Playing voice feedback audio
  | "error"       // Error state
```

## Features

| Feature | Description |
|---------|-------------|
| **Soniox STT** | WebSocket streaming transcription |
| **Hands-free** | Stays listening after command sent |
| **Stop Word** | "thank you" triggers send (configurable) |
| **Wake Lock** | Keeps screen on during recording |
| **Debouncing** | Prevents duplicate sends (500ms) |
| **Auto-reconnect** | Reconnects on disconnect |

## Audio Configuration

```typescript
const AUDIO_CONFIG = {
  sampleRate: 16000,  // Required by Soniox
  channelCount: 1,    // Mono
  format: "pcm16",
  chunkSizeMs: 64,
}
```

## Soniox Connection

```typescript
// WebSocket URL
wss://stt-rt.soniox.com/transcribe-websocket

// Configuration sent on connect
{
  api_key: "...",
  include_nonfinal: true,
  speech_context: {
    phrases: ["tmux", "pane", ...]
  }
}
```

## Usage Example

```tsx
function VoiceButton({ teamId, roleId }) {
  const { isRecording, startRecording, stopRecording } = useVoiceRecorder()

  return (
    <button onClick={() =>
      isRecording ? stopRecording() : startRecording(teamId, roleId)
    }>
      {isRecording ? 'Stop' : 'Record'}
    </button>
  )
}
```
