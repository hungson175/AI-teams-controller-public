# Speech-to-Speech Integration for AI Teams Controller

## Executive Summary

This document outlines the research findings for implementing voice-based communication with the AI Teams Controller. Instead of typing commands and reading outputs, users will be able to **talk to their AI teams** using real-time speech-to-speech technology.

**Recommended Solution**: OpenAI GPT Realtime API with WebRTC for the Coordinator Tab, enabling natural voice conversations with sub-300ms latency.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [OpenAI GPT Realtime API Overview](#openai-gpt-realtime-api-overview)
3. [Architecture Options](#architecture-options)
4. [Implementation Guide for Next.js](#implementation-guide-for-nextjs)
5. [Alternative Solutions](#alternative-solutions)
6. [Cost Analysis](#cost-analysis)
7. [Recommended Approach](#recommended-approach)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Sources](#sources)

---

## Problem Statement

Currently, the AI Teams Controller requires users to:
- Type commands to send messages to roles/teams
- Read text output from each role's tmux pane
- Manually refresh to see updates

**Desired State**: Voice-based interaction where users can:
- Speak commands to the Coordinator (and optionally to individual roles)
- Hear responses spoken back
- Have natural, interruptible conversations with AI agents

---

## OpenAI GPT Realtime API Overview

### What Is It?

The **GPT-4 Realtime API** (now branded as `gpt-realtime`) is OpenAI's speech-to-speech AI model that enables low-latency, natural voice conversations. Unlike traditional voice pipelines that chain STT → LLM → TTS, the Realtime API **processes and generates audio directly through a single model**.

### Key Features

| Feature | Description |
|---------|-------------|
| **Native Audio Processing** | Single model handles speech input/output directly |
| **Low Latency** | 232-320ms average response time |
| **Interruption Handling** | Advanced VAD automatically handles interruptions |
| **Function Calling** | Trigger actions during voice conversations |
| **Multiple Voices** | Cedar, Marin (new), Alloy, Echo, Shimmer |
| **WebRTC Support** | Direct client-to-server audio streaming |

### Technical Specifications

- **Token window**: 32,768 tokens maximum
- **Max response tokens**: 4,096
- **Session duration**: Up to 60 minutes
- **Audio format**: PCM16, 24kHz, mono, little-endian
- **Protocols**: WebSocket, WebRTC, SIP

### Available Voices

**New Premium Voices** (Realtime API exclusive):
- **Marin**: Professional and clear
- **Cedar**: Natural and conversational

**Standard Voices**:
- **Alloy**: Neutral and balanced
- **Echo**: Warm and engaging
- **Shimmer**: Energetic and expressive

**Voice Customization**: The model can follow instructions like "speak quickly and professionally" or "speak empathetically in a French accent".

---

## Architecture Options

### Option 1: Integrated Speech-to-Speech (Recommended)

```
┌─────────────┐     WebRTC      ┌──────────────────┐
│   Browser   │ ◄─────────────► │ OpenAI Realtime  │
│ (Mic/Audio) │                 │      API         │
└─────────────┘                 └──────────────────┘
       │                                │
       │ Control Messages               │ Function Calls
       ▼                                ▼
┌─────────────┐                 ┌──────────────────┐
│  Next.js    │ ◄─────────────► │   tmux/Claude    │
│  Backend    │                 │   Code CLI       │
└─────────────┘                 └──────────────────┘
```

**Pros**:
- Lowest latency (~300ms)
- Single integration point
- Native audio understanding (tone, emotion)
- Natural conversation flow

**Cons**:
- Higher cost with long conversations
- Vendor lock-in

### Option 2: Hybrid Pipeline (STT → LLM → TTS)

```
┌─────────────┐    Audio    ┌──────────┐   Text   ┌─────────┐
│   Browser   │ ──────────► │ Deepgram │ ───────► │  GPT-4  │
│ (Mic/Audio) │             │   STT    │          │   LLM   │
└─────────────┘             └──────────┘          └─────────┘
       ▲                                                │
       │ Audio                                     Text │
       │                                                ▼
┌──────────────┐                              ┌─────────────┐
│  ElevenLabs  │ ◄──────────────────────────  │   Response  │
│     TTS      │                              │   Handler   │
└──────────────┘                              └─────────────┘
```

**Pros**:
- More control over each component
- Better voice quality (ElevenLabs)
- Constant costs (no context accumulation)

**Cons**:
- Higher latency (~510ms)
- More complex integration
- Multiple vendor relationships

---

## Implementation Guide for Next.js

### 1. Project Structure

```
/app
  /api
    /realtime
      /token/route.ts      # Generate ephemeral tokens
  /components
    /voice
      VoiceAssistant.tsx   # Main voice UI component
      AudioVisualizer.tsx  # Waveform display
      VoiceButton.tsx      # Push-to-talk or toggle
/lib
  /realtime
    client.ts              # OpenAI Realtime client wrapper
    audio.ts               # Audio utilities
```

### 2. Backend: Token Generation (Critical for Security)

**Never expose API keys to the browser.** Create a Next.js API route to generate ephemeral tokens:

```typescript
// app/api/realtime/token/route.ts
import { NextResponse } from 'next/server';

export async function POST() {
  const response = await fetch('https://api.openai.com/v1/realtime/sessions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'gpt-4o-realtime-preview',
      voice: 'cedar',
    }),
  });

  const data = await response.json();
  return NextResponse.json({
    client_secret: data.client_secret
  });
}
```

### 3. Client-Side: WebRTC Connection

```typescript
// lib/realtime/client.ts
export class RealtimeClient {
  private pc: RTCPeerConnection | null = null;
  private dataChannel: RTCDataChannel | null = null;

  async connect(ephemeralToken: string) {
    // Create peer connection
    this.pc = new RTCPeerConnection();

    // Set up audio output
    this.pc.ontrack = (event) => {
      const audioEl = document.createElement('audio');
      audioEl.srcObject = event.streams[0];
      audioEl.autoplay = true;
    };

    // Capture microphone
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: true
    });
    this.pc.addTrack(stream.getTracks()[0]);

    // Create data channel for events
    this.dataChannel = this.pc.createDataChannel('oai-events');
    this.dataChannel.onmessage = this.handleMessage.bind(this);

    // Create and set offer
    const offer = await this.pc.createOffer();
    await this.pc.setLocalDescription(offer);

    // Send offer to OpenAI
    const response = await fetch(
      'https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${ephemeralToken}`,
          'Content-Type': 'application/sdp',
        },
        body: offer.sdp,
      }
    );

    const answerSdp = await response.text();
    await this.pc.setRemoteDescription({
      type: 'answer',
      sdp: answerSdp,
    });
  }

  private handleMessage(event: MessageEvent) {
    const message = JSON.parse(event.data);
    // Handle different event types
    switch (message.type) {
      case 'response.audio.delta':
        // Audio is handled automatically via ontrack
        break;
      case 'response.function_call_arguments.done':
        // Handle function calls (e.g., send command to tmux)
        this.handleFunctionCall(message);
        break;
    }
  }

  sendMessage(text: string) {
    this.dataChannel?.send(JSON.stringify({
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [{ type: 'input_text', text }],
      },
    }));
    this.dataChannel?.send(JSON.stringify({
      type: 'response.create',
    }));
  }
}
```

### 4. React Component: Voice Assistant

```tsx
// components/voice/VoiceAssistant.tsx
'use client';

import { useState, useRef, useCallback } from 'react';
import { RealtimeClient } from '@/lib/realtime/client';

export function VoiceAssistant() {
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const clientRef = useRef<RealtimeClient | null>(null);

  const connect = useCallback(async () => {
    // Get ephemeral token from backend
    const res = await fetch('/api/realtime/token', { method: 'POST' });
    const { client_secret } = await res.json();

    // Initialize client
    clientRef.current = new RealtimeClient();
    await clientRef.current.connect(client_secret);
    setIsConnected(true);
    setIsListening(true);
  }, []);

  const disconnect = useCallback(() => {
    clientRef.current?.disconnect();
    setIsConnected(false);
    setIsListening(false);
  }, []);

  return (
    <div className="flex flex-col items-center gap-4 p-4">
      {!isConnected ? (
        <button
          onClick={connect}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg"
        >
          Start Voice Assistant
        </button>
      ) : (
        <>
          <div className={`w-16 h-16 rounded-full ${
            isListening ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
          }`} />
          <p className="text-sm text-gray-600">
            {isListening ? 'Listening...' : 'Processing...'}
          </p>
          <button
            onClick={disconnect}
            className="px-4 py-2 bg-red-600 text-white rounded-lg"
          >
            End Session
          </button>
        </>
      )}
    </div>
  );
}
```

### 5. Function Calling for Team Commands

Configure the Realtime API to call functions that interact with your tmux sessions:

```typescript
// Configure session with tools
const sessionConfig = {
  type: 'session.update',
  session: {
    instructions: `You are the Coordinator for an AI development team.
    You can send commands to team members (PM, Developer, Code Reviewer)
    via tmux. When the user asks to do something, use the appropriate
    function to send commands to the right team member.`,
    tools: [
      {
        type: 'function',
        name: 'send_to_role',
        description: 'Send a command or message to a specific team role',
        parameters: {
          type: 'object',
          properties: {
            role: {
              type: 'string',
              enum: ['pm', 'developer', 'code_reviewer'],
              description: 'The team role to send the message to',
            },
            message: {
              type: 'string',
              description: 'The message or command to send',
            },
          },
          required: ['role', 'message'],
        },
      },
      {
        type: 'function',
        name: 'get_role_status',
        description: 'Get the current output/status of a team role',
        parameters: {
          type: 'object',
          properties: {
            role: {
              type: 'string',
              enum: ['pm', 'developer', 'code_reviewer'],
            },
          },
          required: ['role'],
        },
      },
    ],
  },
};
```

---

## Alternative Solutions

### Comparison Table

| Solution | Latency | Cost/Min | Best For |
|----------|---------|----------|----------|
| **OpenAI Realtime** | 232-320ms | $0.06-0.24 | Production, short conversations |
| **Moshi (OSS)** | 160-200ms | Free | Self-hosting, experimentation |
| **Deepgram + GPT-4o + ElevenLabs** | ~510ms | $0.07-0.10 | Quality-focused, long conversations |
| **Azure Speech** | 500-1000ms | $0.02-0.03 | Enterprise, regulated industries |

### When to Choose Alternatives

**Choose Hybrid Pipeline (Deepgram + LLM + ElevenLabs) if**:
- Conversations are typically long (>5 minutes)
- Voice quality is paramount
- You need more control over components
- Cost predictability is important

**Choose Moshi (Open Source) if**:
- You want to self-host
- Zero API costs are required
- Experimenting with voice AI

---

## Cost Analysis

### OpenAI Realtime API Pricing

| Component | Price |
|-----------|-------|
| Audio Input | $32 per 1M tokens (~$0.06/min) |
| Audio Output | $64 per 1M tokens (~$0.24/min) |
| Cached Input | $0.40 per 1M tokens |

### Example Scenarios

**Quick Command (30 seconds)**:
- User speaks: 15 sec → $0.015
- AI responds: 15 sec → $0.06
- **Total: ~$0.08**

**Extended Session (5 minutes)**:
- User speaks: 2 min → $0.12
- AI responds: 3 min → $0.72
- **Total: ~$0.84**

### Cost Optimization Tips

1. **Use Voice Activity Detection (VAD)** - Silence still counts if streaming continuously
2. **Implement push-to-talk** - Only stream when user is speaking
3. **Set conversation limits** - Truncate history to reduce context tokens
4. **Use cached inputs** - Reuse system prompts

---

## Recommended Approach

### For AI Teams Controller

**Primary Recommendation**: OpenAI Realtime API with WebRTC

**Reasoning**:
1. **Use Case Fit**: Coordinator interactions are typically short commands
2. **Latency Critical**: Real-time control requires sub-500ms response
3. **Function Calling**: Native support for triggering tmux commands
4. **Simplicity**: Single integration point vs. managing multiple services

### Implementation Strategy

**Phase 1: Voice-Enabled Coordinator (MVP)**
- Add voice input/output to Coordinator Tab only
- Push-to-talk mode initially
- Function calling for team commands

**Phase 2: Enhanced Voice Features**
- Voice Activity Detection (auto-detect speech end)
- Audio visualization (waveforms)
- Voice settings (select voice, adjust speed)

**Phase 3: Role-Level Voice (Optional)**
- Voice input to individual roles (fire-and-forget)
- Text-to-speech for role outputs (read aloud)

---

## Implementation Roadmap

### Phase 1: Foundation (MVP)

1. **Backend Setup**
   - Create `/api/realtime/token` endpoint
   - Configure OPENAI_API_KEY environment variable
   - Set up session configuration with team tools

2. **Client Integration**
   - Install OpenAI SDK or implement WebRTC client
   - Create VoiceAssistant component
   - Integrate with Coordinator Tab

3. **Function Calling**
   - Define `send_to_role` function
   - Define `get_role_status` function
   - Connect to existing tmux API routes

### Phase 2: UX Enhancements

1. **Audio Visualization**
   - Use `react-voice-visualizer` for waveforms
   - Show speaking/listening indicators

2. **VAD Integration**
   - Install `@ricky0123/vad-react`
   - Auto-detect speech boundaries
   - Eliminate need for push-to-talk

3. **Settings & Preferences**
   - Voice selection
   - Volume controls
   - Input device selection

### Phase 3: Advanced Features

1. **Conversation History**
   - Display transcript alongside voice
   - Allow replay of responses

2. **Multi-Modal Support**
   - Voice + text input together
   - Screen sharing with voice

---

## Key Libraries & Resources

### Essential Libraries

```bash
# OpenAI SDK
pnpm add openai

# Voice Activity Detection
pnpm add @ricky0123/vad-react

# Audio Visualization
pnpm add react-voice-visualizer
```

### Reference Implementations

- [openai-realtime-api-nextjs](https://github.com/cameronking4/openai-realtime-api-nextjs) - Next.js 15 starter with WebRTC
- [openai-realtime-agents](https://github.com/openai/openai-realtime-agents) - Official multi-agent example
- [openai-realtime-console](https://github.com/openai/openai-realtime-api-beta) - React reference client

### Documentation

- [OpenAI Realtime API Guide](https://platform.openai.com/docs/guides/realtime)
- [OpenAI Realtime API Reference](https://platform.openai.com/docs/api-reference/realtime)
- [WebRTC Integration Guide](https://developers.openai.com/blog/realtime-api/)

---

## Sources

### Official Documentation
- [Introducing gpt-realtime and Realtime API updates](https://openai.com/index/introducing-gpt-realtime/)
- [Developer notes on the Realtime API](https://developers.openai.com/blog/realtime-api/)
- [OpenAI Realtime API Guide](https://platform.openai.com/docs/guides/realtime)

### Implementation Guides
- [Build Voice AI Next.js Apps with OpenAI Realtime API](https://dev.to/cameronking4/build-voice-ai-nextjs-apps-with-openai-realtime-api-beta-webrtc-shadcnui-330a)
- [Build Your Own Realtime AI Voice Assistant with Next.js](https://medium.com/@matthias.vimbert/build-your-own-realtime-ai-voice-assistant-with-next-js-and-openai-1a09e11c7ace)
- [OpenAI Voice Agents Quickstart](https://openai.github.io/openai-agents-js/guides/voice-agents/quickstart/)

### Alternative Solutions
- [Cerebrium: Alternative to OpenAI Realtime API](https://www.cerebrium.ai/blog/an-alternative-to-openai-realtime-api-for-voice-capabilities)
- [AssemblyAI: Best Real-Time Speech Recognition APIs](https://www.assemblyai.com/blog/best-api-models-for-real-time-speech-recognition-and-transcription)
- [Softcery: How to Choose STT and TTS for Voice Agents](https://softcery.com/lab/how-to-choose-stt-tts-for-ai-voice-agents-in-2025-a-comprehensive-guide)

### Security & Best Practices
- [How To Protect Your API Key In Production With Next.js](https://www.smashingmagazine.com/2021/12/protect-api-key-production-nextjs-api-route/)
- [Keeping Your Next.js API Key Secure](https://nextnative.dev/blog/api-key-secure)

### Voice UI/UX
- [VAD for React Documentation](https://docs.vad.ricky0123.com/user-guide/react/)
- [react-voice-visualizer](https://github.com/YZarytskyi/react-voice-visualizer)
- [Using React Speech Recognition Hook](https://blog.logrocket.com/using-the-react-speech-recognition-hook-for-voice-assistance/)
