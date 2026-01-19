# Deepgram Aura TTS Demo

**Same cost as OpenAI, but 2-5x faster!**

## Key Advantages

- ⚡ **Speed**: 250-300ms time-to-first-audio (vs OpenAI's ~200ms but Deepgram benchmarks show 2-5x overall faster performance)
- 💰 **Cost**: $15/million chars (same as OpenAI)
- 🎯 **Purpose-built**: Optimized for real-time voice AI agents
- 🏆 **Quality**: Aura-2 beats ElevenLabs, Cartesia, and OpenAI in enterprise testing

## Setup

### 1. Install Dependencies
```bash
pip install deepgram-sdk
```

### 2. Get API Key
1. Sign up at [https://deepgram.com](https://deepgram.com)
2. Navigate to API Keys in console
3. Create new API key
4. Copy the key

### 3. Set Environment Variable
```bash
export DEEPGRAM_API_KEY="your_api_key_here"
```

Add to `~/.zshrc` or `~/.bashrc`:
```bash
echo 'export DEEPGRAM_API_KEY="your_api_key_here"' >> ~/.zshrc
```

## Run Demo

```bash
python demo.py
```

Output: `output_deepgram.mp3`

## Available Models

| Model | Voice | Description |
|-------|-------|-------------|
| aura-asteria-en | Female | Warm and engaging |
| aura-luna-en | Female | Calm and soothing |
| aura-stella-en | Female | Energetic and upbeat |
| aura-athena-en | Female | Professional |
| aura-orion-en | Male | Confident |
| aura-arcas-en | Male | Casual |
| aura-perseus-en | Male | Assertive |

## Pricing

| Tier | Cost | Free Credits |
|------|------|--------------|
| Pay-as-you-go | $15/million chars | $200 free credits |
| Growth plans | Volume discounts | Available |

**Same as OpenAI**, but faster!

## Streaming Support

Deepgram excels at **streaming TTS**:
- Start playing audio immediately while generation continues
- Perfect for conversational AI and voice agents
- Reduces perceived latency

```python
from deepgram import DeepgramClient, SpeakWebSocketOptions

options = SpeakWebSocketOptions(
    model="aura-asteria-en",
    encoding="linear16",
    sample_rate=16000,
)

# Use WebSocket for streaming
# (see demo.py for full implementation)
```

## Integration with Your Project

Replace OpenAI TTS:

**Before (OpenAI):**
```python
from openai import OpenAI
client = OpenAI()
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=text
)
```

**After (Deepgram):**
```python
from deepgram import DeepgramClient, SpeakOptions

deepgram = DeepgramClient(api_key)
options = SpeakOptions(
    model="aura-asteria-en",
    encoding="mp3",
)
response = deepgram.speak.v("1").save(
    output_file,
    {"text": text},
    options
)
```

## When to Use Deepgram

✅ **Use Deepgram if:**
- You need **faster TTS** for real-time voice applications
- You want **streaming support** for lower perceived latency
- You're building voice AI agents or conversational interfaces
- You want **same cost as OpenAI** but better performance

❌ **Stick with OpenAI if:**
- You're already integrated and performance is acceptable
- You don't need the speed advantage
- Simple integration is more important than performance

## Documentation

- [Deepgram TTS Documentation](https://developers.deepgram.com/docs/text-to-speech)
- [Aura Models](https://deepgram.com/product/text-to-speech)
- [API Reference](https://developers.deepgram.com/reference/text-to-speech-api)
