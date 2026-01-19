# OpenAI Realtime API - Python Speech-to-Speech Demo

This demo showcases the OpenAI Realtime API for speech-to-speech communication in Python. It's designed as a proof-of-concept for adding voice capabilities to the AI Teams Controller.

## Overview

The OpenAI Realtime API enables low-latency, natural voice conversations with AI. Unlike traditional pipelines (STT → LLM → TTS), the Realtime API processes audio directly through a single model, achieving ~300ms latency.

### Key Features

- **Real-time voice conversation** - Talk naturally with AI
- **Voice Activity Detection (VAD)** - Automatic speech detection
- **Function calling** - Trigger actions via voice commands
- **Multiple voices** - alloy, echo, shimmer, cedar, marin

## Quick Start

### 1. Prerequisites

- Python 3.10+
- macOS: Install PortAudio for audio support
  ```bash
  brew install portaudio
  ```

### 2. Install Dependencies

```bash
cd backend/experiments/speech2speech
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 3. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 4. Run a Demo

```bash
# Simple voice chat (VAD mode)
python demo_simple.py

# Push-to-talk mode (more control)
python demo_push_to_talk.py

# With function calling (simulates team commands)
python demo_with_tools.py
```

## Demo Descriptions

### `demo_simple.py` - Basic Voice Chat

The simplest demo. Just speak and the AI responds. Uses server-side Voice Activity Detection (VAD) to automatically detect when you stop speaking.

**Best for**: Quick testing, understanding the basic flow.

### `demo_push_to_talk.py` - Push-to-Talk Mode

Interactive demo with keyboard controls:
- `SPACE` - Start/stop recording
- `M` - Mute/unmute
- `C` - Cancel current response
- `Q` - Quit

**Best for**: Controlled conversations, noisy environments.

### `demo_with_tools.py` - Function Calling Demo

Shows how to use voice commands to trigger actions. Simulates the AI Teams Controller use case where you can:

- "Tell the developer to start working on the login feature"
- "What is the PM working on?"
- "Give me a team status update"

**Best for**: Understanding how voice + actions work together.

## Project Structure

```
speech2speech/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── .env.example           # API key template
├── audio_utils.py         # Audio format conversion utilities
├── audio_handler.py       # Microphone/speaker I/O
├── realtime_client.py     # OpenAI Realtime API WebSocket client
├── demo_simple.py         # Basic voice chat demo
├── demo_push_to_talk.py   # Push-to-talk demo
└── demo_with_tools.py     # Function calling demo
```

## Technical Details

### Audio Format

OpenAI Realtime API requires:
- **Format**: PCM16 (16-bit signed integer)
- **Sample Rate**: 24kHz
- **Channels**: Mono
- **Encoding**: Base64 for WebSocket transmission

### Architecture

```
┌─────────────────┐      WebSocket       ┌────────────────────┐
│  AudioHandler   │ ◄─────────────────►  │  OpenAI Realtime   │
│  (sounddevice)  │                      │       API          │
└─────────────────┘                      └────────────────────┘
        │                                         │
        │ PCM16 Audio                             │ Events
        ▼                                         ▼
┌─────────────────┐                      ┌────────────────────┐
│ RealtimeClient  │ ◄──────────────────► │  Function Calls    │
│   (websockets)  │                      │   (Your Actions)   │
└─────────────────┘                      └────────────────────┘
```

### Event Flow

1. **Audio Input**: Microphone → sounddevice → PCM16 → Base64 → WebSocket
2. **Processing**: OpenAI processes audio, generates response
3. **Audio Output**: WebSocket → Base64 → PCM16 → sounddevice → Speaker
4. **Function Calls**: API requests function → Execute → Return result

## API Reference

### `RealtimeClient`

```python
from realtime_client import RealtimeClient, SessionConfig

config = SessionConfig(
    voice="alloy",  # Voice to use
    instructions="You are a helpful assistant.",
    tools=[...],    # Function definitions
)

async with RealtimeClient(api_key="sk-...", config=config) as client:
    await client.send_audio(audio_pcm16)
    await client.send_text("Hello!")
    await client.commit_audio()  # Trigger response
```

### `AudioHandler`

```python
from audio_handler import AudioHandler

handler = AudioHandler()
handler.start()  # Start recording and playback

# Get audio from microphone
audio = await handler.get_audio_chunk_async()

# Play audio to speaker
handler.play_audio(audio_pcm16)

handler.stop()
```

### `audio_utils`

```python
from audio_utils import (
    float32_to_pcm16,
    pcm16_to_float32,
    audio_to_base64,
    base64_to_audio,
    resample_audio,
)

# Convert formats
pcm16 = float32_to_pcm16(float_audio)
base64_str = audio_to_base64(pcm16)

# Resample to 24kHz
audio_24k = resample_audio(audio, original_rate=16000)
```

## Costs

OpenAI Realtime API pricing (as of 2025):
- **Audio Input**: ~$0.06/minute
- **Audio Output**: ~$0.24/minute

A typical 1-minute conversation costs approximately **$0.30**.

## Troubleshooting

### No audio input detected

1. Check microphone permissions
2. Verify correct audio device:
   ```python
   from audio_handler import AudioHandler
   AudioHandler.list_devices()
   ```

### Audio sounds robotic/slow

Ensure sample rate matches (24kHz). The Realtime API is strict about audio format.

### WebSocket connection fails

1. Check API key is valid
2. Ensure `OPENAI_API_KEY` is set in `.env`
3. Check internet connection

### High latency

- Use wired headphones (Bluetooth adds latency)
- Close other audio applications
- Check network connection

## Next Steps

To integrate this into AI Teams Controller:

1. **Backend**: Create FastAPI endpoint that proxies to Realtime API
2. **Frontend**: Use WebRTC for browser audio (see `docs/speech-2-speech.md`)
3. **Tools**: Replace simulated functions with real tmux commands

## Resources

- [OpenAI Realtime API Documentation](https://platform.openai.com/docs/guides/realtime)
- [OpenAI Python SDK - Realtime](https://github.com/openai/openai-python)
- [Full Research Document](../../../docs/speech-2-speech.md)

## Sources

This demo was built based on research from:

1. [OpenAI Realtime API Python Guide 2025](https://skywork.ai/blog/agent/openai-realtime-api-python-guide-2025-complete-code/)
2. [OpenAI Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
3. [python-sounddevice Documentation](https://python-sounddevice.readthedocs.io/)
4. [Conversing via Local Microphone using Realtime API](https://medium.com/@m_sea_bass/conversing-via-local-microphone-and-speaker-using-realtime-api-6660877cda18)
5. [OpenAI Python SDK Examples](https://github.com/openai/openai-python/blob/main/examples/realtime/push_to_talk_app.py)
