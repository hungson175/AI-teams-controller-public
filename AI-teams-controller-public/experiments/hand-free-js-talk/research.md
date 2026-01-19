# GPT Realtime API for Browser Speech-to-Text

## Overview

OpenAI's Realtime API enables real-time voice interactions via WebSocket. For browser apps, we use WebSocket with ephemeral tokens from a backend relay.

## Key Requirements

| Requirement | Value |
|-------------|-------|
| Audio Format | PCM16 |
| Sample Rate | 24kHz |
| Channels | 1 (mono) |
| Protocol | WebSocket |
| Auth | Ephemeral token (from backend) |

## Architecture

```
Browser                    Backend                   OpenAI
   |                          |                         |
   |-- GET /api/token ------->|                         |
   |                          |-- POST /v1/realtime/sessions -->|
   |                          |<-- ephemeral token -----|
   |<-- ephemeral token ------|                         |
   |                                                    |
   |------------- WebSocket (with token) -------------->|
   |<------------ Transcriptions -----------------------|
```

## WebSocket Connection

```javascript
const ws = new WebSocket(
  "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17",
  ["realtime", `openai-insecure-api-key.${ephemeralToken}`, "openai-beta.realtime-v1"]
);
```

## Session Configuration

```javascript
ws.send(JSON.stringify({
  type: "session.update",
  session: {
    modalities: ["text"],  // text-only for transcription
    input_audio_transcription: { model: "whisper-1" },
    turn_detection: {
      type: "server_vad",
      threshold: 0.5,
      prefix_padding_ms: 300,
      silence_duration_ms: 5000  // 5 seconds silence
    }
  }
}));
```

## Audio Capture & Sending

```javascript
// Get microphone
const stream = await navigator.mediaDevices.getUserMedia({
  audio: { channelCount: 1, sampleRate: 24000 }
});

// Process audio
const audioContext = new AudioContext({ sampleRate: 24000 });
const source = audioContext.createMediaStreamSource(stream);
const processor = audioContext.createScriptProcessor(4096, 1, 1);

processor.onaudioprocess = (e) => {
  const float32 = e.inputBuffer.getChannelData(0);
  const int16 = convertFloat32ToInt16(float32);
  const base64 = arrayBufferToBase64(int16.buffer);

  ws.send(JSON.stringify({
    type: "input_audio_buffer.append",
    audio: base64
  }));
};
```

## Key Events

| Event | Description |
|-------|-------------|
| `input_audio_buffer.speech_started` | User started speaking |
| `input_audio_buffer.speech_stopped` | Silence detected |
| `conversation.item.input_audio_transcription.completed` | Transcription ready |

## VAD (Voice Activity Detection)

Server-side VAD with `silence_duration_ms: 5000` will:
1. Detect when user starts speaking
2. After 5 seconds of silence, trigger `speech_stopped`
3. Process and return transcription

## Security

**NEVER expose API key in browser!** Use backend to generate ephemeral tokens:

```javascript
// Backend generates ephemeral token
const response = await fetch('https://api.openai.com/v1/realtime/sessions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${OPENAI_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ model: 'gpt-4o-realtime-preview-2024-12-17' })
});
const { client_secret } = await response.json();
// Return client_secret.value as ephemeral token
```

## Pricing (2025)

- Input audio: $0.032 per minute (~$32/1M tokens)
- Output audio: $0.064 per minute (~$64/1M tokens)

## Sources

- [OpenAI Realtime API](https://openai.com/index/introducing-the-realtime-api/)
- [VAD Guide](https://platform.openai.com/docs/guides/realtime-vad)
- [Realtime Transcription](https://platform.openai.com/docs/guides/realtime-transcription)
