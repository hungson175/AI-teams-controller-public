# GLM-4-Voice Real-time Speech Model Research

**Date:** 2024-12-10
**Purpose:** Evaluate GLM-4-Voice as alternative to GPT Realtime API for voice commands

---

## Executive Summary

GLM-4-Voice is an **open-source end-to-end speech model** from Zhipu AI (智谱AI), released October 2024. Key highlights:

- **Open source** - Full model weights available (Apache 2.0 license)
- **Self-hostable** - Can run on 12GB GPU (INT4 quantized)
- **Low latency** - Starts generation with as few as 10 tokens
- **Voice control** - Adjustable emotion, tone, speed, dialect
- **Languages** - Chinese and English (Vietnamese NOT supported for voice)

**Important:** GLM-4-Voice is NOT a traditional STT API - it's an end-to-end voice LLM that processes speech directly without text intermediary.

---

## 1. Company Background

**Zhipu AI (智谱AI)** - Chinese AI company, rebranded as **Z.ai** internationally in July 2025.

Notable:
- GLM series large language models
- Partnership with Samsung (Galaxy S25 integration)
- Open-source approach to AI models

---

## 2. GLM-4-Voice Architecture

### Three Components

| Component | Function |
|-----------|----------|
| **GLM-4-Voice-Tokenizer** | Converts speech to discrete tokens at 12.5 tokens/sec (175bps ultra-low bitrate) |
| **GLM-4-Voice-9B** | Base language model trained on speech modality (1 trillion tokens) |
| **GLM-4-Voice-Decoder** | Streaming speech decoder (CosyVoice-based) |

### Key Innovation
- **End-to-end processing** - No separate STT→LLM→TTS pipeline
- **Ultra-low bitrate** - 175bps tokenization enables efficient processing
- **Streaming** - Can start generating audio with only 10 tokens buffered

---

## 3. Features

### Voice Capabilities
- Direct speech understanding and generation
- Real-time conversation support
- Real-time interruption handling

### Voice Customization (Unique to GLM)
- **Emotion adjustment** - Gentle, excited, mournful
- **Speech rate control** - Multiple speed levels
- **Dialect generation** - Various Chinese dialects
- **Intonation variation** - Context-adaptive

### Language Support
| Language | Voice Support |
|----------|---------------|
| Chinese (Mandarin) | ✅ Full support + dialects |
| English | ✅ Full support |
| Vietnamese | ❌ NOT supported |

**Note:** Vietnamese is NOT supported for voice. This is a significant limitation for our use case.

---

## 4. Comparison: GLM-4-Voice vs OpenAI GPT Realtime API

| Feature | GLM-4-Voice | GPT-4o Realtime |
|---------|-------------|-----------------|
| **Latency** | ~10 tokens min | <200ms |
| **Cost** | Free (self-hosted) | $0.15/min |
| **Languages** | Chinese + English | Multilingual |
| **Vietnamese** | ❌ No | ✅ Yes |
| **Open Source** | ✅ Yes | ❌ No |
| **Self-hosting** | ✅ 12GB GPU | ❌ Cloud only |
| **Function Calling** | Limited | ✅ Advanced |
| **Voice Control** | ✅ Emotion/tone/dialect | Basic |
| **VAD** | ✅ Yes | ✅ Yes |
| **Interruption** | ✅ Yes | ✅ Yes |

### Cost Analysis

**OpenAI GPT Realtime:**
- $32/1M audio input tokens
- $64/1M audio output tokens
- ~$0.15/minute of conversation
- ~$9/hour

**GLM-4-Voice:**
- Self-hosted: Only GPU cost
- API pricing: Not publicly disclosed
- Text model pricing suggests 10-20x cheaper than OpenAI

---

## 5. Technical Requirements

### Self-Hosting Hardware
| Precision | VRAM Required |
|-----------|---------------|
| BFloat16 | ~20GB |
| INT4 | ~12GB (RTX 3060 compatible) |

### Software Requirements
- Python 3.10 (NOT 3.8/3.9/3.12)
- CUDA support
- ~10GB model download

---

## 6. Access Options

### Option A: Self-Hosted (Open Source)
```bash
# Clone and setup
git clone https://github.com/THUDM/GLM-4-Voice
conda create -n GLM-4-Voice python=3.10
pip install -r requirements.txt

# Download models from HuggingFace
# - THUDM/glm-4-voice-tokenizer
# - THUDM/glm-4-voice-9b
# - THUDM/glm-4-voice-decoder
```

### Option B: Zhipu AI API
- Platform: https://open.bigmodel.cn
- API docs: https://open.bigmodel.cn/dev/api/rtav/GLM-Realtime
- Pricing: Not publicly disclosed (requires account)

---

## 7. Limitations for Our Use Case

### Critical Issues
1. **No Vietnamese support** - Voice model only supports Chinese and English
2. **Not a pure STT API** - It's an end-to-end voice LLM, not transcription service
3. **Heavy requirements** - Need 12-20GB GPU for self-hosting
4. **Limited API docs** - Real-time API pricing/details behind login

### What GLM-4-Voice IS
- End-to-end voice conversation model
- Speaks and listens in single model
- Good for: Voice assistants, chatbots, voice AI agents

### What GLM-4-Voice IS NOT
- Pure Speech-to-Text API (like Whisper, Soniox)
- Transcription service
- Multi-language voice recognition

---

## 8. Recommendation for AI Controller

**NOT recommended** for our voice command use case because:

1. **No Vietnamese** - We need English/Vietnamese code-switching
2. **Overkill** - We only need STT, not full voice LLM
3. **Heavy** - Requires significant GPU resources
4. **Different paradigm** - End-to-end model vs STT→LLM→TTS pipeline

**Better alternatives for our use case:**
- **Soniox** - Pure STT with Vietnamese support (5.4% WER)
- **GPT Realtime API** - Current solution, works well
- **Whisper** - Self-hosted STT option

### When GLM-4-Voice WOULD be good
- Building Chinese voice assistant
- Need emotion/tone control in speech
- Want full voice AI without separate components
- Self-hosting requirement with GPU available

---

## 9. Demo Code Purpose

The demo code provided is for **educational purposes** to understand how GLM-4-Voice works, even though it's not suitable for our Vietnamese voice command use case.

---

## Sources

1. [GLM-4-Voice GitHub - THUDM](https://github.com/THUDM/GLM-4-Voice)
2. [GLM-4-Voice GitHub - zai-org](https://github.com/zai-org/GLM-4-Voice)
3. [Zhipu AI Releases GLM-4-Voice - MarkTechPost](https://www.marktechpost.com/2024/10/25/zhipu-ai-releases-glm-4-voice-a-new-open-source-end-to-end-speech-large-language-model/)
4. [GLM-4-Voice arXiv Paper](https://arxiv.org/abs/2412.02612)
5. [HuggingFace - glm-4-voice-9b](https://huggingface.co/zai-org/glm-4-voice-9b)
6. [Zhipu AI Open Platform](https://open.bigmodel.cn)
7. [OpenAI GPT Realtime API](https://openai.com/index/introducing-gpt-realtime/)
