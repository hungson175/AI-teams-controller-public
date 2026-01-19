# Google Cloud TTS Demo

Demo for testing Google Cloud Text-to-Speech API as a cheaper alternative to OpenAI TTS.

## Cost Comparison

| Provider | Price/1M chars | Vietnamese Support |
|----------|---------------|-------------------|
| Google Standard | $4 | ✅ Yes |
| Google Neural2 | $16 | ✅ Yes |
| OpenAI TTS | $15 | ✅ Yes |

**Savings**: 73% cheaper with Standard, similar price with Neural2

## Setup

### 1. Install Dependencies

```bash
cd experiments/google-tts
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Credentials

**Option A: Service Account (Recommended for production)**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Text-to-Speech API:
   - Go to "APIs & Services" > "Library"
   - Search for "Cloud Text-to-Speech API"
   - Click "Enable"
4. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: `tts-demo`
   - Grant role: "Cloud Text-to-Speech User"
   - Click "Create Key" > "JSON"
   - Save the JSON file as `google-credentials.json` in this directory

5. Set environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/google-credentials.json"
```

**Option B: Application Default Credentials (for testing)**

```bash
gcloud auth application-default login
```

### 3. Run Demo

```bash
# Basic demo - generates audio for all voice types
python demo.py

# Compare specific voices
python demo.py --text "This is a test" --voices standard neural2 wavenet

# Vietnamese test
python demo.py --text "Xin chào, đây là bài kiểm tra" --language vi-VN

# Custom output directory
python demo.py --output-dir ./output
```

## Demo Scripts

### `demo.py`
Main demo script that:
- Tests Standard, WaveNet, and Neural2 voices
- Generates audio files for English and Vietnamese
- Measures latency for each voice type
- Outputs MP3 files to `output/` directory

### `compare_tts.py`
Comparison script (requires OpenAI API key):
- Side-by-side comparison of Google TTS vs OpenAI TTS
- Measures latency, cost, and file size
- Generates comparison report

## Voice Types

### Standard Voices ($4/1M chars)
- Basic quality, cheapest option
- 73% cheaper than OpenAI
- Example: `en-US-Standard-A`

### WaveNet Voices ($16/1M chars)
- High quality neural synthesis
- Natural intonation and emotion
- Example: `en-US-Wavenet-A`

### Neural2 Voices ($16/1M chars)
- Best quality available
- Similar to Custom Voice technology
- Example: `en-US-Neural2-A`

### Studio Voices ($160/1M chars)
- Ultra-premium, not recommended for most use cases
- 10x more expensive than OpenAI

## Available Voices

**English (US)**:
- Standard: A, B, C, D, E, F, G, H, I, J
- WaveNet: A, B, C, D, E, F, G, H, I, J
- Neural2: A, C, D, E, F, G, H, I, J
- Studio: M, O, Q

**Vietnamese**:
- Standard: A, B, C, D
- WaveNet: A, B, C, D
- Neural2: A

## Free Tier

- **Standard**: 4 million characters/month
- **WaveNet/Neural2**: 1 million characters/month

## Integration with AI Teams Controller

To integrate Google TTS into the backend:

1. Install dependency:
```bash
cd backend
uv add google-cloud-texttospeech
```

2. Update `backend/app/services/celery_tasks.py`:
```python
from google.cloud import texttospeech

def generate_tts_google(text: str, language: str = "en-US") -> bytes:
    client = texttospeech.TextToSpeechClient()

    # Use Standard for cost savings
    voice_name = f"{language}-Standard-A"

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        name=voice_name
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

3. Update `.env`:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-credentials.json
```

## References

- [Full Research Report](../../docs/research/tts-alternatives-research.md)
- [Google Cloud TTS Documentation](https://cloud.google.com/text-to-speech/docs)
- [Supported Voices](https://cloud.google.com/text-to-speech/docs/voices)
- [Pricing](https://cloud.google.com/text-to-speech/pricing)
