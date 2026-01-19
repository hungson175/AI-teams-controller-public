# Voice Command Integration - Research & Design

**Date**: 2024-12-09
**Status**: Research Complete

---

## Overview

This document outlines OpenAI technologies for implementing voice command integration in the AI Teams Controller app.

### User Flow
1. **Speech-to-Text (S2T)**: User speaks command, stop word "SEND PLS" triggers send
2. **Text-to-Text (T2T)**: LLM rewrites/translates command based on context
3. **Text-to-Speech (T2S)**: When task done, summarize output and speak to user

---

## OpenAI API Options

### Option A: Traditional Pipeline (Recommended for v1)

```
[Microphone] → Whisper API (S2T) → GPT-4o (T2T) → TTS API (T2S) → [Speaker]
```

**Pros:**
- More cost-effective at scale
- Fine-grained control over each step
- Easier to debug
- Can detect stop word in transcribed text

**Cons:**
- Higher latency (3 API calls)
- More complex integration

### Option B: Realtime API

```
[Microphone] → GPT-4o Realtime API (unified) → [Speaker]
```

**Pros:**
- Ultra-low latency (~500ms)
- Single API endpoint
- Native interruption handling

**Cons:**
- More expensive (~$0.18/min vs ~$0.02/min)
- Less control over individual steps
- Overkill for command-based workflow

### Recommendation

**Use Option A (Traditional Pipeline)** for v1:
- We need stop word detection → requires text processing between S2T and send
- Cost matters for frequent use
- Easier to implement and debug

---

## API Details

### 1. Speech-to-Text: Whisper API

**Models:**
| Model | Price | Best For |
|-------|-------|----------|
| whisper-1 | $0.006/min | General use |
| gpt-4o-transcribe | $0.006/min | Higher accuracy |
| gpt-4o-mini-transcribe | $0.003/min | Cost optimization |

**Key Features:**
- 99+ languages supported
- 25MB max file size
- Formats: mp3, mp4, wav, webm, m4a

**Python Example:**
```python
from openai import OpenAI

client = OpenAI()

with open("audio.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="en"
    )
print(transcription.text)
```

**Real-time Streaming (WebSocket):**
```python
# For live microphone input
# Endpoint: wss://api.openai.com/v1/realtime?intent=transcription
# Requires: OpenAI-Beta: realtime=v1 header
```

### 2. Text Processing: GPT-4o

**Purpose:** Rewrite user's spoken command into proper agent instruction

**Example Prompt:**
```
You are a command translator for an AI agent team.

Current pane state:
{pane_output}

User said: "{user_speech}"

Rewrite this as a clear, actionable command for the agent.
Keep it concise. Output only the command, nothing else.
```

**Pricing:**
- GPT-4o: $5/1M input, $20/1M output tokens
- GPT-4o-mini: $0.15/1M input, $0.60/1M output tokens

### 3. Text-to-Speech: TTS API

**Models:**
| Model | Price | Latency | Best For |
|-------|-------|---------|----------|
| tts-1 | $15/1M chars | ~0.5s | Real-time |
| tts-1-hd | $30/1M chars | Higher | Quality |

**Voices:** alloy, echo, fable, onyx, nova, shimmer

**Formats:** mp3, opus, aac, flac, wav, pcm

**Python Example:**
```python
from openai import OpenAI

client = OpenAI()

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Task completed. The agent processed your request successfully."
)

response.stream_to_file("output.mp3")
```

**Streaming:** Supports chunk transfer encoding for real-time playback

---

## Implementation Architecture

### Phase 1: Speech-to-Text with Stop Word

```
Browser Microphone → WebSocket → Backend → Whisper API
                                    ↓
                              Detect "SEND PLS"
                                    ↓
                              Extract command
                                    ↓
                              GPT-4o rewrite
                                    ↓
                              Send to tmux pane
```

### Phase 2: Task Completion Summary

```
Claude Code Stop Hook → Backend API (TaskDoneListener)
                              ↓
                        Get tmux pane output
                              ↓
                        GPT-4o summarize
                              ↓
                        TTS API → Audio
                              ↓
                        WebSocket → Browser → Play audio
```

---

## Stop Word Detection

The stop word "SEND PLS" will be detected in the transcribed text:

```python
def process_transcription(text: str) -> tuple[bool, str]:
    """Check for stop word and extract command."""
    stop_word = "SEND PLS"

    if stop_word.lower() in text.lower():
        # Remove stop word and return command
        command = text.lower().replace(stop_word.lower(), "").strip()
        return True, command

    return False, text
```

---

## Claude Code Stop Hook

To detect when a task is done, use Claude Code hooks:

```bash
# ~/.claude/hooks.json
{
  "Stop": [
    {
      "matcher": ".*",
      "command": "curl -X POST http://localhost:17061/api/task-done -H 'Content-Type: application/json' -d '{\"session\": \"$TMUX_SESSION\", \"pane\": \"$TMUX_PANE\"}'"
    }
  ]
}
```

---

## Cost Estimate

For a typical interaction (30 seconds speech, 500 char response):

| Step | Cost |
|------|------|
| Whisper (30s) | $0.003 |
| GPT-4o-mini (rewrite) | ~$0.0001 |
| GPT-4o-mini (summarize) | ~$0.0005 |
| TTS (500 chars) | $0.0075 |
| **Total** | **~$0.011** |

**Monthly estimate (100 interactions/day):** ~$33/month

---

## Dependencies

```toml
# Backend (pyproject.toml)
openai = ">=1.0.0"
sounddevice = ">=0.4.0"  # For audio capture
numpy = ">=1.24.0"
```

```json
// Frontend (package.json)
// Uses Web Audio API (built-in)
```

---

## Demo Files

1. `scripts/voice_demo_s2t.py` - Speech-to-Text with stop word detection
2. `scripts/voice_demo_t2s.py` - Text-to-Speech for summaries
3. `scripts/voice_demo_full.py` - Full pipeline demo

---

## Sources

- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI TTS API](https://platform.openai.com/docs/guides/text-to-speech)
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)
- [OpenAI API Pricing](https://openai.com/api/pricing/)
