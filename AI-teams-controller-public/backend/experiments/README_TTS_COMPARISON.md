# TTS Provider Comparison: Mixed English-Vietnamese Support

## Executive Summary

**RECOMMENDATION: Google Cloud TTS Standard** ($4/million chars)

- ✅ **73% cheaper** than OpenAI TTS ($15/million)
- ✅ **Vietnamese support confirmed**
- ✅ **Auto-detects mixed languages**
- ✅ **4M free chars/month**
- ✅ **Already integrated** in backend (Story 36)

**Alternative:** ElevenLabs if budget allows (20-40x more expensive, but industry-leading quality)

---

## Detailed Comparison

### Cost per Million Characters (2025 Pricing)

| Provider | Voice Type | Cost/Million | Free Tier | Vietnamese |
|----------|-----------|--------------|-----------|------------|
| **Google Cloud** | Standard | **$4** ⭐ | 4M/month | ✅ Yes |
| **Google Cloud** | WaveNet/Neural2 | **$16** | 1M/month | ✅ Yes |
| OpenAI | TTS Standard | $15 | None | ❌ No |
| OpenAI | TTS HD | $30 | None | ❌ No |
| Azure | Neural | ~$15 | 0.5M/month | ✅ Yes |
| Amazon Polly | Neural | $19.20 | 1M (12mo) | ❓ Unknown |
| **ElevenLabs** | Multilingual v2 | **$165+** | 10K/month | ✅ Yes (70+ langs) |
| ElevenLabs | Turbo 2.5 | ~$82.50 | 10K/month | ✅ Yes (32 langs) |
| PlayHT | Unlimited | $99/month | 12.5K/month | ✅ Yes (142 langs) |
| Deepgram | Aura-2 | $30 | $200 credit | ❌ No (yet) |

---

## Cost Comparison: 5M chars/month scenario

| Provider | Monthly Cost | Annual Savings vs Google |
|----------|-------------|--------------------------|
| **Google Standard** | **$20** | **Baseline** |
| Google WaveNet | $64 | -$528 |
| OpenAI Standard | $75 | -$660 |
| Azure Neural | $75 | -$660 |
| Amazon Polly Neural | $96 | -$912 |
| ElevenLabs Scale | $825 | -$9,660 |
| PlayHT Unlimited | $99 | -$948 |
| Deepgram Aura-2 | $150 | -$1,560 |

**Google Cloud saves $660-9,660/year vs alternatives**

---

## Mixed-Language Capabilities

### Google Cloud TTS
- ✅ **Auto language detection** - detects predominant language
- ✅ **SSML language tags** - explicit control: `<lang xml:lang="vi-VN">...</lang>`
- ✅ **Multilingual voices** - can speak both languages
- ⚠️ Quality: English with Vietnamese voice may have slight accent

### ElevenLabs
- ✅ **Seamless auto-detection** - industry-leading naturalness
- ✅ **Best-in-class code-switching** - most natural language transitions
- ✅ **Voice cloning across languages** - same voice personality in both languages
- ✅ Quality: Excellent for both languages

### Azure Cognitive Services
- ✅ **Multilingual voices** with auto-detect
- ✅ **SSML support** for language control
- ✅ **HD voices** (LLM-based) - detect emotions and adjust tone
- ⚠️ More complex API than Google Cloud

---

## Test Results

### Setup
Run the demo scripts in `/backend/experiments/`:

```bash
# Google Cloud TTS tests
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
python experiments/test_mixed_language_tts.py

# ElevenLabs tests (optional - for comparison)
export ELEVENLABS_API_KEY=your_key
python experiments/test_elevenlabs_tts.py
```

### Test Cases

1. **Auto-detection test** - Mixed text without language tags
2. **SSML explicit tags** - Using `<lang>` for precise control
3. **Realistic scenario** - Actual voice feedback with technical terms
4. **Quality comparison** - Standard vs WaveNet vs ElevenLabs

### Expected Outputs

- `/tmp/test_auto_detect.mp3` - Auto language detection
- `/tmp/test_ssml_tags.mp3` - Explicit SSML language tags
- `/tmp/test_realistic_mixed.mp3` - Realistic mixed content
- `/tmp/test_standard_quality.mp3` - Standard voice ($4/million)
- `/tmp/test_wavenet_quality.mp3` - WaveNet voice ($16/million)
- `/tmp/test_elevenlabs_mixed.mp3` - ElevenLabs comparison ($165/million)

---

## Integration with Existing System

### Current Setup (Story 36)
You already have Google Cloud TTS integrated via `TTSProvider` abstraction:

```python
# backend/app/services/tts_providers.py
class GoogleTTSProvider(TTSProvider):
    def generate_audio(self, text: str) -> bytes:
        # Already supports Vietnamese
        # Uses Standard voices by default ($4/million)
```

### Switching to WaveNet (if needed)
Edit `backend/app/services/tts_providers.py`:

```python
voice = texttospeech.VoiceSelectionParams(
    language_code="vi-VN",
    name="vi-VN-Wavenet-A",  # Change from Standard-A
)
```

### Adding ElevenLabs (if needed)
Create new provider implementation:

```python
class ElevenLabsTTSProvider(TTSProvider):
    def generate_audio(self, text: str) -> bytes:
        # See test_elevenlabs_tts.py for implementation
```

Update `.env`:
```bash
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_key
```

---

## Decision Matrix

### Choose Google Cloud Standard if:
- ✅ Cost efficiency is important (73% cheaper than OpenAI)
- ✅ Good quality is sufficient
- ✅ Want generous free tier (4M chars/month)
- ✅ Prefer pay-as-you-go pricing
- ✅ Already integrated in system

### Upgrade to Google Cloud WaveNet if:
- ✅ Need better quality than Standard
- ✅ Still want cost savings vs OpenAI (47% cheaper)
- ✅ User feedback indicates quality issues with Standard

### Choose ElevenLabs if:
- ✅ Voice quality is **mission-critical**
- ✅ Customer-facing product where quality = competitive advantage
- ✅ Budget allows $165-330/month (Scale plan)
- ✅ Willing to pay 20-40x more for premium naturalness
- ⚠️ Be prepared for high costs at scale

---

## Recommendations

### Phase 1: Start with Google Cloud Standard
1. Use existing integration (already done in Story 36)
2. Test with Vietnamese users
3. Collect quality feedback
4. Cost: ~$4 per million chars (after free tier)

### Phase 2: Upgrade if needed
**If quality feedback is positive:**
- ✅ Keep using Standard voices
- ✅ Save 73% vs OpenAI

**If quality feedback indicates issues:**
- Option A: Upgrade to Google WaveNet ($16/million) - Still 47% cheaper
- Option B: Test ElevenLabs with small volume (~100K chars)
- Compare quality vs cost trade-off

### Phase 3: Scale decision
**Once you hit >25M chars/month:**
- Re-evaluate pricing
- Consider PlayHT Unlimited ($99/month flat rate)
- Or negotiate Google Cloud volume discounts

---

## Sources

1. [ElevenLabs Pricing](https://elevenlabs.io/pricing)
2. [ElevenLabs Vietnamese Support](https://elevenlabs.io/blog/introducing-vietnamese-norwegian-and-hungarian)
3. [Azure Speech Services Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/)
4. [Amazon Polly Pricing](https://aws.amazon.com/polly/pricing/)
5. [Google Cloud TTS Pricing](https://cloud.google.com/text-to-speech/pricing)
6. [PlayHT Pricing](https://play.ht/pricing/)
7. [Deepgram Aura-2 Pricing](https://deepgram.com/pricing)
8. [TTS Cost Comparison](https://daisy.org/news-events/articles/ai-text-to-speech-cost-comparison/)
9. [Best TTS APIs 2025](https://www.speechmatics.com/company/articles-and-news/best-tts-apis-in-2025-top-12-text-to-speech-services-for-developers)
10. [ElevenLabs vs OpenAI](https://vapi.ai/blog/elevenlabs-vs-openai)
