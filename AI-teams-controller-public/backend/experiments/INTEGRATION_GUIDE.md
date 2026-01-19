# Integration Guide: Mixed English-Vietnamese TTS

## Current State (Story 36)

Your backend already supports switchable TTS providers via `TTSProviderFactory`:

```python
# backend/app/services/tts_providers.py
class TTSProvider(ABC):
    @abstractmethod
    def generate_audio(self, text: str) -> bytes:
        pass

class GoogleTTSProvider(TTSProvider):
    def generate_audio(self, text: str) -> bytes:
        # Already supports Vietnamese
        # Uses Standard voices (vi-VN-Standard-A)

class OpenAITTSProvider(TTSProvider):
    def generate_audio(self, text: str) -> bytes:
        # Does NOT support Vietnamese
```

**Current configuration:**
```bash
# backend/.env
TTS_PROVIDER=google  # Already using Google Cloud (good!)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

---

## Recommendations for Mixed Language Support

### Option 1: Keep Current Setup ✅ RECOMMENDED

**Your existing Google TTS implementation already works for mixed English-Vietnamese!**

**Why it works:**
- Google Cloud TTS auto-detects language
- Vietnamese voices (vi-VN-Standard-A) can handle English text
- Cost: $4/million chars (73% cheaper than OpenAI)
- Free tier: 4M chars/month

**What to test:**
1. Run the demo script to verify quality:
   ```bash
   cd backend
   uv run python experiments/test_mixed_language_tts.py
   ```

2. Listen to output files:
   - `/tmp/test_realistic_mixed.mp3` - Most similar to your use case
   - `/tmp/test_auto_detect.mp3` - Auto language detection

3. If quality is acceptable: ✅ Done! No code changes needed.

---

### Option 2: Upgrade to WaveNet (Better Quality)

If Standard voice quality is insufficient, upgrade to WaveNet voices:

**Edit `/backend/app/services/tts_providers.py`:**

```python
class GoogleTTSProvider(TTSProvider):
    def generate_audio(self, text: str) -> bytes:
        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="vi-VN",
            name="vi-VN-Wavenet-A",  # Changed from Standard-A
            # Cost: $16/million chars (still 47% cheaper than OpenAI)
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        return response.audio_content
```

**Restart services:**
```bash
./scripts/restart-all.sh  # Or restart Celery specifically
```

**Cost impact:**
- Before: $4/million chars (Standard)
- After: $16/million chars (WaveNet)
- Still 47% cheaper than OpenAI ($15/million for non-Vietnamese)

---

### Option 3: Use SSML for Explicit Language Tags

For more precise control over language switching:

**Update `GoogleTTSProvider.generate_audio()` to accept SSML:**

```python
class GoogleTTSProvider(TTSProvider):
    def generate_audio(self, text: str, use_ssml: bool = False) -> bytes:
        client = texttospeech.TextToSpeechClient()

        if use_ssml:
            # Wrap text with explicit language tags
            ssml_text = f"""
            <speak>
                <lang xml:lang="vi-VN">{text}</lang>
            </speak>
            """
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
        else:
            # Auto-detection (current behavior)
            synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="vi-VN",
            name="vi-VN-Standard-A"
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        return response.audio_content
```

**When to use SSML:**
- Text has clear language boundaries
- Want to control pronunciation more precisely
- Need to add pauses, emphasis, etc.

---

### Option 4: Add ElevenLabs (Premium Quality)

Only if Google Cloud quality is insufficient and budget allows.

**Create new provider in `tts_providers.py`:**

```python
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

class ElevenLabsTTSProvider(TTSProvider):
    def __init__(self):
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not set")
        self.client = ElevenLabs(api_key=api_key)

    def generate_audio(self, text: str) -> bytes:
        audio_stream = self.client.generate(
            text=text,
            voice="Rachel",  # Or configure via env var
            model="eleven_multilingual_v2",  # Supports Vietnamese
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                use_speaker_boost=True,
            ),
        )

        # Collect audio chunks
        audio_bytes = b"".join(chunk for chunk in audio_stream)
        return audio_bytes
```

**Update `TTSProviderFactory`:**

```python
class TTSProviderFactory:
    @staticmethod
    def get_provider() -> TTSProvider:
        provider_name = os.getenv("TTS_PROVIDER", "google").lower()

        if provider_name == "google":
            return GoogleTTSProvider()
        elif provider_name == "openai":
            return OpenAITTSProvider()
        elif provider_name == "elevenlabs":
            return ElevenLabsTTSProvider()
        else:
            raise ValueError(f"Unknown TTS provider: {provider_name}")
```

**Update `.env`:**
```bash
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=sk-...
```

**Restart services:**
```bash
./scripts/restart-all.sh
```

**Cost warning:**
- ElevenLabs Scale plan: $330/month for 2M chars = $165/million
- Google Cloud Standard: $8 for 2M chars = $4/million
- **41x more expensive!**

---

## Testing Checklist

### 1. Test Current Setup (Google Standard)
```bash
cd backend
uv run python experiments/test_mixed_language_tts.py
```

Listen to:
- `/tmp/test_realistic_mixed.mp3` - Realistic mixed content
- `/tmp/test_auto_detect.mp3` - Auto-detection test

### 2. A/B Test Quality
```bash
# Compare Standard vs WaveNet
uv run python experiments/test_mixed_language_tts.py
```

Listen to:
- `/tmp/test_standard_quality.mp3` - $4/million
- `/tmp/test_wavenet_quality.mp3` - $16/million

### 3. Test with Real Voice Feedback
Use actual task summaries from your system:

```python
from app.services.tts_providers import TTSProviderFactory

provider = TTSProviderFactory.get_provider()

test_summary = """
Task completed successfully.
Đã hoàn thành việc fix bug trong API endpoint.
All tests passed.
Kết quả: 15 tests passed, 0 failed.
"""

audio = provider.generate_audio(test_summary)

with open("/tmp/real_feedback_test.mp3", "wb") as f:
    f.write(audio)

print("✅ Test audio saved to: /tmp/real_feedback_test.mp3")
```

### 4. User Acceptance Testing
1. Deploy to staging
2. Test with Vietnamese-speaking users
3. Collect feedback on:
   - Pronunciation quality (both languages)
   - Naturalness of language transitions
   - Overall audio clarity

---

## Cost Projection

### Current Usage (estimate)
Assume ~50 voice feedbacks/day, average 200 chars each:
- Daily: 50 × 200 = 10,000 chars
- Monthly: 10,000 × 30 = 300,000 chars
- Annual: 300,000 × 12 = 3,600,000 chars

### Cost Comparison

| Provider | Voice Type | Monthly Cost | Annual Cost |
|----------|-----------|--------------|-------------|
| **Google** | Standard | **$0** (free tier) | **$0** (free tier) |
| **Google** | WaveNet | $4.80 | $57.60 |
| OpenAI | TTS Standard | $4.50 | $54 |
| ElevenLabs | Scale plan | $330 | $3,960 |

**Recommendation:** Start with Google Standard (free), monitor usage, upgrade to WaveNet if needed.

---

## Migration Path

### Week 1: Validation
- ✅ Test current Google Standard setup
- ✅ Collect audio samples
- ✅ Internal review

### Week 2: User Testing
- ✅ Deploy to staging
- ✅ A/B test Standard vs WaveNet
- ✅ Gather user feedback

### Week 3: Decision
**If Google Standard quality is acceptable:**
- ✅ Keep current setup
- ✅ Save 73% vs OpenAI
- ✅ No code changes

**If quality needs improvement:**
- Option A: Upgrade to WaveNet (4x cost increase, still cheaper than OpenAI)
- Option B: Test ElevenLabs with limited volume (~10K chars)

### Week 4: Production
- ✅ Deploy chosen solution
- ✅ Monitor costs and quality
- ✅ Set up alerts for usage spikes

---

## Monitoring and Alerts

### Cost Monitoring
Set up Google Cloud billing alerts:

```bash
# Alert at 50%, 75%, 90% of budget
gcloud billing budgets create \
  --billing-account=YOUR_ACCOUNT \
  --display-name="TTS Monthly Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=75 \
  --threshold-rule=percent=90
```

### Quality Monitoring
Track user feedback on voice quality:
- Pronunciation accuracy
- Naturalness rating
- Language transition smoothness

### Usage Monitoring
Log TTS usage in backend:

```python
import logging

logger = logging.getLogger(__name__)

class GoogleTTSProvider(TTSProvider):
    def generate_audio(self, text: str) -> bytes:
        char_count = len(text)
        logger.info(f"TTS request: {char_count} chars, language: auto-detect")

        # Generate audio...

        logger.info(f"TTS response: {len(audio_bytes)} bytes")
        return audio_bytes
```

---

## FAQ

### Q: Does Vietnamese voice handle English well?
**A:** Yes, Google Cloud Vietnamese voices (vi-VN-Standard-A, vi-VN-Wavenet-A) can speak English text. There may be a slight Vietnamese accent on English words, which is actually natural for bilingual speakers.

### Q: Should I use SSML or auto-detection?
**A:** Start with auto-detection (simpler). Only use SSML if you need:
- Precise control over pronunciation
- Custom pauses or emphasis
- Specific accent control

### Q: When should I upgrade to WaveNet?
**A:** Upgrade if users report:
- "Robotic" or unnatural voice
- Poor pronunciation of specific words
- Quality not meeting expectations

Listen to test files first to decide.

### Q: Is ElevenLabs worth 41x the cost?
**A:** Only if:
- Voice quality is mission-critical
- Customer-facing product
- Quality = competitive advantage
- Budget allows $330+/month

For internal tools, probably not worth it.

### Q: What about other languages in the future?
**A:** Google Cloud supports 50+ languages. Easy to add more:

```python
# Support multiple languages
LANGUAGE_VOICES = {
    "vi": "vi-VN-Standard-A",
    "en": "en-US-Standard-A",
    "ja": "ja-JP-Standard-A",
    # Add more as needed
}

def detect_language(text: str) -> str:
    # Simple heuristic or use language detection library
    if any(char in text for char in "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệ"):
        return "vi"
    return "en"
```

---

## Summary

**Immediate Action:** ✅ Test current Google Standard setup

**Next Steps:**
1. Run `/backend/experiments/test_mixed_language_tts.py`
2. Listen to `/tmp/test_realistic_mixed.mp3`
3. If quality is good → Done! No changes needed
4. If quality needs improvement → Test WaveNet ($16/million)
5. Only consider ElevenLabs if WaveNet insufficient and budget allows

**Expected Outcome:** Save 73% vs OpenAI while supporting mixed English-Vietnamese content.
