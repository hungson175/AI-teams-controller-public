# Voice Input Feature - State Management

## Executive Summary: The Problem & Solution

### BEFORE: 660 lines of spaghetti

```
State Soup:
├── VoiceState.status (8 values)
├── VoiceState.isSpeaking (redundant - just VAD feedback)
├── VoiceState.feedbackSummary (belongs to VoiceFeedbackContext!)
├── VoiceState.isPlayingFeedback (belongs to VoiceFeedbackContext!)
└── isHandsFree (separate useState - but it's just "status !== idle"!)

Mutex Hell (5 refs to fix race conditions):
├── isHandsFreeRef      ← stale closure workaround
├── isSendingRef        ← mutex #1
├── isTransitioningRef  ← mutex #2
├── pendingStopRef      ← queued action
└── reconnectAttemptsRef

All these refs exist because the state design is broken.
```

### AFTER: 300 lines with proper FSM

```
Clean FSM:
├── 7 states (idle, connecting, listening, processing, correcting, sent, error)
├── 10 events (START, CONNECTED, TRANSCRIPT, STOP_WORD_DETECTED, etc.)
├── Pure reducer function (no side effects in transitions)
└── 0 mutex refs needed

Derived state (computed, not stored):
├── isRecording = state !== "idle" && state !== "error"
├── canRecord = state === "idle" || state === "error"
└── canClear = transcript.length > 0 && state === "listening"
```

---

## FSM State Diagram

```
                              ┌─────────────────────────────────────────┐
                              │                                         │
                              ▼                                         │
    ┌──────┐  START    ┌────────────┐  CONNECTED   ┌───────────┐       │
    │ IDLE │──────────►│ CONNECTING │─────────────►│ LISTENING │       │
    └──────┘           └────────────┘              └───────────┘       │
        ▲                    │                          │              │
        │                    │ ERROR                    │ STOP_WORD    │
        │                    ▼                          ▼              │
        │              ┌─────────┐              ┌────────────┐         │
        │              │  ERROR  │              │ PROCESSING │         │
        │              └─────────┘              └────────────┘         │
        │                    │                          │              │
        │ STOP               │ START                    │ LLM_TOKEN    │
        │                    │                          ▼              │
        │                    │                  ┌────────────┐         │
        └────────────────────┴──────────────────│ CORRECTING │         │
        │                                       └────────────┘         │
        │                                              │               │
        │ STOP                                         │ COMMAND_SENT  │
        │                                              ▼               │
        │                                       ┌──────────┐           │
        └───────────────────────────────────────│   SENT   │───────────┘
                                                └──────────┘
                                                RETURN_TO_LISTENING
```

---

## State Definitions

### FSM State (7 states)

| State | Description | Valid Events |
|-------|-------------|--------------|
| `idle` | Not recording | START |
| `connecting` | Connecting to Soniox | CONNECTED, ERROR, STOP |
| `listening` | Recording, waiting for stop word | TRANSCRIPT, STOP_WORD_DETECTED, STOP, ERROR, CLEAR_TRANSCRIPT |
| `processing` | Stop word detected, sending | LLM_TOKEN, COMMAND_SENT, ERROR |
| `correcting` | Streaming LLM tokens | LLM_TOKEN, COMMAND_SENT, ERROR |
| `sent` | Command delivered | RETURN_TO_LISTENING, STOP |
| `error` | Error occurred | START, STOP |

### Context (Extended State)

```typescript
interface VoiceContext {
  state: VoiceState
  teamId: string | null
  roleId: string | null
  transcript: string
  correctedCommand: string
  error: string | null
  reconnectAttempts: number
}
```

### Events (10 events)

| Event | Payload | Description |
|-------|---------|-------------|
| `START` | teamId, roleId | User clicks mic button |
| `CONNECTED` | - | Soniox WebSocket connected |
| `TRANSCRIPT` | text | Real-time transcription update |
| `STOP_WORD_DETECTED` | command | Stop word found in transcript |
| `LLM_TOKEN` | token | Backend streams correction token |
| `COMMAND_SENT` | command, routedToBacklog? | Command delivered to tmux |
| `RETURN_TO_LISTENING` | - | Timer fires after sent state |
| `STOP` | - | User clicks mic again |
| `ERROR` | message | Any error occurred |
| `CLEAR_TRANSCRIPT` | - | User clears current transcript |

---

## Transition Table

| Current State | Event | Next State | Action |
|--------------|-------|------------|--------|
| idle | START | connecting | Connect to Soniox, request wake lock |
| error | START | connecting | Connect to Soniox, request wake lock |
| connecting | CONNECTED | listening | Reset reconnect counter |
| connecting | ERROR | error | Store error message |
| connecting | STOP | idle | Cleanup resources |
| listening | TRANSCRIPT | listening | Update transcript |
| listening | STOP_WORD_DETECTED | processing | Clear transcript, send command |
| listening | STOP | idle | Disconnect Soniox |
| listening | ERROR | error | Store error message |
| listening | CLEAR_TRANSCRIPT | listening | Reset transcript |
| processing | LLM_TOKEN | correcting | Append token |
| processing | COMMAND_SENT | sent | Store final command |
| processing | ERROR | error | Store error message |
| correcting | LLM_TOKEN | correcting | Append token |
| correcting | COMMAND_SENT | sent | Store final command |
| correcting | ERROR | error | Store error message |
| sent | RETURN_TO_LISTENING | listening | Clear corrected command |
| sent | STOP | idle | Cleanup resources |

---

## What Got Removed

### Redundant State

| Removed | Why |
|---------|-----|
| `VoiceState.isSpeaking` | VAD feedback - UI concern, not core state |
| `VoiceState.feedbackSummary` | Belongs to VoiceFeedbackContext |
| `VoiceState.isPlayingFeedback` | Belongs to VoiceFeedbackContext |
| `isHandsFree` useState | Derived: `state !== "idle" && state !== "error"` |

### Mutex Refs (All 5 gone!)

| Removed | Why Not Needed |
|---------|----------------|
| `isHandsFreeRef` | No stale closures - useReducer dispatch is stable |
| `isSendingRef` | FSM state guards: can only send in listening state |
| `isTransitioningRef` | FSM guards: START only valid from idle/error |
| `pendingStopRef` | STOP event always valid, reducer handles it |

### Complexity

| Before | After |
|--------|-------|
| 660 lines | ~300 lines |
| 5 mutex refs | 0 mutex refs |
| Scattered state updates | Pure reducer |
| Race condition workarounds | Impossible by design |

---

## Code Comparison

### BEFORE: Mutex Spaghetti

```typescript
// 5 refs to handle race conditions
const isTransitioningRef = useRef<boolean>(false)
const pendingStopRef = useRef<boolean>(false)
const isSendingRef = useRef<boolean>(false)
const isHandsFreeRef = useRef<boolean>(false)

const startRecording = useCallback(async () => {
  // Mutex guard
  if (isTransitioningRef.current) {
    console.log("Transition in progress, skipping")
    return
  }
  isTransitioningRef.current = true

  try {
    // ... 100 lines of setup
  } finally {
    isTransitioningRef.current = false
  }
}, [/* 10 dependencies */])

const stopRecording = useCallback(() => {
  // Another mutex guard
  if (isTransitioningRef.current) {
    pendingStopRef.current = true  // Queue it!
    return
  }
  // ... cleanup
}, [/* dependencies */])

// Sync ref with state to avoid stale closure
useEffect(() => {
  isHandsFreeRef.current = isHandsFree
}, [isHandsFree])
```

### AFTER: Clean FSM

```typescript
// Pure state transitions
function voiceReducer(ctx: VoiceContext, event: VoiceEvent): VoiceContext {
  switch (event.type) {
    case "START":
      // Guard is just a check, not a mutex
      if (ctx.state !== "idle" && ctx.state !== "error") return ctx
      return { ...initialContext, state: "connecting", teamId: event.teamId }

    case "STOP":
      if (ctx.state === "idle") return ctx
      return { ...initialContext }

    // ... other transitions
  }
}

// No mutex needed - dispatch is always valid
const startRecording = useCallback(async (teamId, roleId) => {
  dispatch({ type: "START", teamId, roleId })
  // ... side effects
}, [/* minimal dependencies */])

const stopRecording = useCallback(() => {
  dispatch({ type: "STOP" })
  // ... cleanup
}, [])
```

---

## Files

| File | Purpose |
|------|---------|
| `/frontend/hooks/useVoiceRecorderFSM.ts` | **NEW** - Clean FSM implementation |
| `/frontend/hooks/useVoiceRecorder.ts` | OLD - 660 lines of mess (to be replaced) |

---

## Migration Path

1. **Test new hook**: Import `useVoiceRecorderFSM` in `TmuxController.tsx`
2. **Verify behavior**: All existing functionality should work
3. **Remove old hook**: Delete `useVoiceRecorder.ts`
4. **Rename**: `useVoiceRecorderFSM.ts` → `useVoiceRecorder.ts`

---

## Why FSM > Ad-hoc State

1. **Impossible States Are Impossible**: Can't be "connecting" and "listening" simultaneously
2. **Self-Documenting**: State diagram IS the specification
3. **No Race Conditions**: Transitions are atomic
4. **Testable**: Pure reducer, no mocks needed
5. **Debuggable**: Log events, replay state
