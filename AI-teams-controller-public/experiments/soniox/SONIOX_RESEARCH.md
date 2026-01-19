# Soniox Speech-to-Text API Research

**Date:** 2024-12-10
**Purpose:** Evaluate Soniox as alternative to GPT Realtime API for voice commands

---

## Executive Summary

Soniox is a speech AI company offering real-time transcription and translation across 60+ languages. Key highlights:

- **Vietnamese WER: 5.4%** (vs English 6.5%) - excellent for our use case
- **Cost: $0.10-0.12/hour** - significantly cheaper than OpenAI (~$0.38/hour)
- **Real-time WebSocket API** with token-level streaming
- **Built-in features:** Speaker diarization, language detection, translation

---

## 1. Overview & Features

### What is Soniox?
- Self-described as "world's first universal speech API"
- 60+ production-ready languages
- Real-time and async transcription
- SOC 2 Type II certified, HIPAA-compliant

### Core Capabilities
| Feature | Soniox | GPT Realtime API |
|---------|--------|------------------|
| Vietnamese support | Yes (5.4% WER) | Yes |
| English support | Yes (6.5% WER) | Yes |
| Real-time streaming | WebSocket | WebSocket |
| Speaker diarization | Built-in | No |
| Translation | 60+ languages | No |
| Language detection | Automatic | Manual |
| Pricing | $0.10-0.12/hr | ~$0.38/hr |

### Language Support
Both **Vietnamese** and **English** are fully supported with:
- Real-time streaming and async processing
- Automatic language detection
- Code-switching (mid-sentence language changes)
- Speaker-aware diarization

---

## 2. Technical Integration

### Authentication
```bash
export SONIOX_API_KEY=<YOUR_API_KEY>
```
- Get API key from https://console.soniox.com
- Free tier available (no credit card required)
- Temporary keys available for client-side apps

### SDKs Available
| Platform | Package |
|----------|---------|
| Python | `pip install soniox` |
| JavaScript (Browser) | `@soniox/speech-to-text-web` |
| Node.js | `soniox_node` |
| C# | Available |

### API Options

**WebSocket API (Real-time):**
- Endpoint: `wss://stt-rt.soniox.com/transcribe-websocket`
- Token-level streaming (milliseconds latency)
- Max 60 minutes per stream
- $0.12/hour

**REST API (Async):**
- For pre-recorded files
- Better accuracy for speaker diarization
- $0.10/hour

### Audio Format Support
- Auto-detected: MP3, FLAC, WAV, etc.
- Raw PCM formats (various bit depths)
- Companded formats (mulaw, alaw)

---

## 3. Comparison with Competitors

### Accuracy (Soniox Claims)
| Provider | English WER | Vietnamese WER |
|----------|-------------|----------------|
| **Soniox** | 6.5% | 5.4% |
| OpenAI | 10.5% | N/A |
| Azure | 13-14% | N/A |
| Deepgram | 9.3% | N/A |

**Caveat:** These are Soniox's own benchmarks. Independent tests show different results in some scenarios.

### Cost Comparison
| Provider | Cost/Hour |
|----------|-----------|
| **Soniox** | $0.10-0.12 |
| OpenAI Realtime | ~$0.38 |
| Azure | $0.24-0.48 |
| Deepgram | $0.20-0.40 |

### Rate Limits
| Limit | Value |
|-------|-------|
| Requests/minute | 100 (can increase) |
| Concurrent connections | 10 (can increase) |
| Stream duration | 300 min (fixed) |

---

## 4. Unique Selling Points

1. **All-in-One API** - Transcription + translation + diarization in single call
2. **60+ Language Translation** - Real-time any-to-any translation
3. **Code-Switching** - Handles mid-sentence language changes
4. **Domain Adaptation** - Custom vocabulary for industry terms
5. **Compliance** - SOC 2, HIPAA, GDPR ready

---

## 5. Considerations for Our Use Case

### Pros for AI Controller Voice Commands
- Excellent Vietnamese support (5.4% WER)
- Much cheaper than OpenAI ($0.12 vs $0.38/hr)
- Automatic language detection (no need to specify)
- Handles English/Vietnamese code-switching naturally

### Cons / Risks
- Less community feedback (newer provider)
- Independent benchmarks show mixed results in noisy environments
- No "stop word" detection like GPT Realtime API's VAD
- May need custom silence detection implementation

### Migration Considerations
Current architecture uses GPT Realtime API with:
- Ephemeral tokens from backend
- Frontend direct WebSocket connection
- 5-second silence timeout for auto-send

Soniox would require:
- Different WebSocket protocol
- Custom silence/endpoint detection
- Different token format

---

## 6. Recommendation

**Worth experimenting with** for these reasons:
1. 70% cost savings potential
2. Better Vietnamese accuracy (per vendor benchmarks)
3. Built-in language detection

**Suggested approach:**
1. Create proof-of-concept with Soniox WebSocket API
2. Test with mixed English/Vietnamese speech
3. Measure latency and accuracy in real conditions
4. Compare with current GPT Realtime API experience

---

## Sources

1. [Soniox Official Website](https://soniox.com/)
2. [Soniox Documentation](https://soniox.com/docs)
3. [Soniox Pricing](https://soniox.com/pricing/)
4. [Soniox Benchmarks](https://soniox.com/benchmarks)
5. [Vietnamese STT](https://soniox.com/speech-to-text/vietnamese)
6. [WebSocket API Docs](https://soniox.com/docs/stt/api-reference/websocket-api)
7. [Web SDK GitHub](https://github.com/soniox/speech-to-text-web)
8. [Soniox Examples](https://github.com/soniox/soniox_examples)
