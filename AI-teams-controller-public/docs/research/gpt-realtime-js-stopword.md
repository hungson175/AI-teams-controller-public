# GPT Realtime API - JavaScript Browser Client Transcription & Stop Word Detection

## Overview

This document covers how to properly implement real-time speech transcription with stop word detection using OpenAI's GPT Realtime API in a JavaScript/TypeScript browser client.

## The Problem

Our current implementation has the stop word detection not triggering because transcription events are not being received properly.

## Key Finding: The Working Python Implementation

Looking at our working experiment (`backend/experiments/voice_command/exp_full_voice_2_command.py`), the Python implementation uses:

```python
# Session configuration - PYTHON (WORKING)
await ws.send(json.dumps({
    "type": "session.update",
    "session": {
        "modalities": ["text"],  # NOTE: text only!
        "instructions": "Transcribe exactly what the user says.",
        "input_audio_format": "pcm16",
        "input_audio_transcription": {"model": "whisper-1"},
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 800,
        },
    },
}))
```

**Key observation**: The Python version uses `modalities: ["text"]` (NOT `["text", "audio"]`) and it WORKS!

## Critical Configuration Requirements

### 1. `input_audio_transcription` is MANDATORY

The most common reason transcription events don't fire is missing `input_audio_transcription` configuration:

```javascript
input_audio_transcription: {
  model: "whisper-1"  // REQUIRED for transcription events
}
```

Without this, `conversation.item.input_audio_transcription.completed` will NEVER fire.

### 2. The Correct Event to Listen For

```javascript
// This is THE event for user speech transcription
case 'conversation.item.input_audio_transcription.completed':
  console.log('User said:', data.transcript);
  // Check for stop words here
  break;
```

Event structure:
```json
{
  "type": "conversation.item.input_audio_transcription.completed",
  "item_id": "<item_id>",
  "content_index": 0,
  "transcript": "Hello how are you go go"
}
```

### 3. Audio Format Requirements

The Realtime API is STRICT about audio format:

| Parameter | Required Value |
|-----------|---------------|
| Sample Rate | 24000 Hz |
| Channels | 1 (mono) |
| Bit Depth | 16-bit signed |
| Encoding | PCM (little-endian) |
| Transport | Base64 encoded |

### 4. Buffer Size for ScriptProcessor

**CRITICAL BUG WE HIT**: `createScriptProcessor` requires buffer size to be a power of 2!

```javascript
// WRONG - will throw IndexSizeError
const processor = audioContext.createScriptProcessor(1200, 1, 1);

// CORRECT - power of 2
const processor = audioContext.createScriptProcessor(2048, 1, 1);
```

Valid values: 256, 512, 1024, 2048, 4096, 8192, 16384, or 0 (browser chooses)

## Complete Working Configuration

Based on the Python experiment and research:

```javascript
const sessionConfig = {
  type: 'session.update',
  session: {
    // For transcription-only, "text" is sufficient
    // For voice responses, use ["text", "audio"]
    modalities: ["text", "audio"],

    instructions: "Transcribe exactly what the user says.",

    input_audio_format: "pcm16",

    // CRITICAL: This enables transcription events
    input_audio_transcription: {
      model: "whisper-1"
    },

    // Server-side VAD for automatic speech detection
    turn_detection: {
      type: "server_vad",
      threshold: 0.5,
      prefix_padding_ms: 300,
      silence_duration_ms: 800  // 800ms silence = end of utterance
    }
  }
};
```

## Stop Word Detection Implementation

### The Python Implementation (Reference)

```python
STOP_WORDS = ["go go go", "go go"]

def detect_stop_word(text: str) -> tuple[bool, str, str]:
    """Check for stop word and extract command."""
    text_lower = text.lower()

    for stop_word in STOP_WORDS:
        if stop_word in text_lower:
            idx = text_lower.find(stop_word)
            command = text[:idx].strip()

            # Remove trailing fillers
            for filler in [",", ".", "and", "so", "then"]:
                if command.lower().endswith(filler):
                    command = command[: -len(filler)].strip()

            return True, command, stop_word

    return False, text, ""
```

### JavaScript Implementation

```typescript
const STOP_WORDS = ['go go go', 'go go'];

function detectStopWord(text: string): { triggered: boolean; command: string; matchedStopWord: string } {
  const textLower = text.toLowerCase();

  for (const stopWord of STOP_WORDS) {
    if (textLower.includes(stopWord)) {
      const idx = textLower.indexOf(stopWord);
      let command = text.slice(0, idx).trim();

      // Remove trailing fillers
      const fillers = [',', '.', 'and', 'so', 'then'];
      for (const filler of fillers) {
        if (command.toLowerCase().endsWith(filler)) {
          command = command.slice(0, -filler.length).trim();
        }
      }

      return { triggered: true, command, matchedStopWord: stopWord };
    }
  }

  return { triggered: false, command: text, matchedStopWord: '' };
}
```

### Where to Call Stop Word Detection

```javascript
ws.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'conversation.item.input_audio_transcription.completed') {
    const transcript = data.transcript;

    // Accumulate transcript
    fullTranscript = (fullTranscript + ' ' + transcript).trim();

    console.log('[Voice] Transcript:', fullTranscript);

    // Check for stop word
    const result = detectStopWord(fullTranscript);
    console.log('[Voice] Stop word check:', result);

    if (result.triggered) {
      console.log('[Voice] STOP WORD DETECTED! Command:', result.command);
      // Send command to backend
      sendCommandToBackend(result.command);
      // Reset transcript
      fullTranscript = '';
    }
  }
});
```

## Common Pitfalls

### 1. Transcription Events Never Fire

**Causes:**
- Missing `input_audio_transcription` in session config
- Audio buffer never committed (in manual mode)
- Wrong audio format

**Solution:**
```javascript
// Ensure this is in your session.update
input_audio_transcription: { model: "whisper-1" }
```

### 2. Audio Buffer Not Committed

With `turn_detection.type: "server_vad"`, the server automatically commits the buffer when it detects speech end.

With `turn_detection: null` or `type: "none"`, you must manually commit:
```javascript
ws.send(JSON.stringify({
  type: 'input_audio_buffer.commit'
}));
```

### 3. Transcription Arrives Asynchronously

The transcription event can arrive BEFORE or AFTER other response events. Don't assume ordering.

### 4. Transcript May Differ from Model's Understanding

The `input_audio_transcription` runs on Whisper, while the main model may interpret the audio differently. The transcript is a "rough guide" only.

## Debugging Checklist

1. **Check session configuration:**
   - [ ] `input_audio_transcription.model` is set to `"whisper-1"`
   - [ ] `turn_detection.type` is `"server_vad"` (or manual commit)
   - [ ] `input_audio_format` is `"pcm16"`

2. **Check audio capture:**
   - [ ] Sample rate is exactly 24000 Hz
   - [ ] Mono channel (1 channel)
   - [ ] 16-bit PCM
   - [ ] Buffer size is power of 2 (for ScriptProcessor)
   - [ ] Audio is Base64 encoded before sending

3. **Check event handling:**
   - [ ] Listening for `conversation.item.input_audio_transcription.completed`
   - [ ] Also listening for `.failed` event for errors
   - [ ] Accumulating transcript across multiple events

4. **Check stop word detection:**
   - [ ] Case-insensitive comparison
   - [ ] Stop words ordered by length (longer first)
   - [ ] Console logging to verify detection

## Audio Capture Code (Correct Implementation)

```typescript
async function startAudioCapture(ws: WebSocket) {
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      channelCount: 1,
      sampleRate: 24000,
      echoCancellation: true,
      noiseSuppression: true
    }
  });

  const audioContext = new AudioContext({ sampleRate: 24000 });
  const source = audioContext.createMediaStreamSource(stream);

  // CRITICAL: Buffer size MUST be power of 2
  const processor = audioContext.createScriptProcessor(2048, 1, 1);

  processor.onaudioprocess = (event) => {
    const inputData = event.inputBuffer.getChannelData(0);

    // Convert Float32 to Int16
    const int16Data = new Int16Array(inputData.length);
    for (let i = 0; i < inputData.length; i++) {
      const s = Math.max(-1, Math.min(1, inputData[i]));
      int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }

    // Convert to Base64
    const base64Audio = btoa(
      String.fromCharCode(...new Uint8Array(int16Data.buffer))
    );

    // Send to WebSocket
    ws.send(JSON.stringify({
      type: 'input_audio_buffer.append',
      audio: base64Audio
    }));
  };

  source.connect(processor);
  processor.connect(audioContext.destination);
}
```

## References

1. [OpenAI Realtime API Guide](https://platform.openai.com/docs/guides/realtime)
2. [OpenAI Realtime WebSocket Documentation](https://platform.openai.com/docs/guides/realtime-websocket)
3. [Azure OpenAI Realtime Audio Reference](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/realtime-audio-reference)
4. [Community: input_audio_transcription not firing](https://community.openai.com/t/getting-no-response-event-for-input-audio-transcription-in-realtime-ws/984306)
5. Working experiment: `backend/experiments/voice_command/exp_full_voice_2_command.py`

## Summary

The key issues for stop word detection:

1. **Must have `input_audio_transcription: { model: "whisper-1" }`** in session config
2. **Audio buffer size must be power of 2** (use 2048, not calculated values like 1200)
3. **Listen for `conversation.item.input_audio_transcription.completed`** event
4. **Accumulate transcripts** across multiple events before checking stop words
5. **Use `server_vad` turn detection** for automatic speech end detection
