# Google Cloud Text-to-Speech Demo

**Cost Savings: 73% cheaper than OpenAI** ($4 vs $15 per million chars for Standard voices)

## Setup

### 1. Install Dependencies
```bash
pip install google-cloud-texttospeech
```

### 2. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable **Text-to-Speech API**

### 3. Create Service Account
1. Navigate to **IAM & Admin** → **Service Accounts**
2. Create service account
3. Grant role: **Text-to-Speech User**
4. Create key (JSON format)
5. Download the JSON key file

### 4. Set Environment Variable
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"
```

Add to your `~/.zshrc` or `~/.bashrc` for persistence:
```bash
echo 'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"' >> ~/.zshrc
```

## Run Demo

```bash
python demo.py
```

This will generate 3 audio files:
- `output_google_standard.mp3` - Standard voice ($4/million)
- `output_google_neural2.mp3` - Neural2 voice ($16/million)
- `output_google_vietnamese.mp3` - Vietnamese voice test

## Pricing

| Voice Type | Cost per 1M chars | vs OpenAI |
|------------|-------------------|-----------|
| Standard   | $4                | 73% cheaper |
| Neural2    | $16               | 7% more expensive |
| WaveNet    | $16               | 7% more expensive |

**Free Tier:**
- Standard: 4M chars/month
- Neural2/WaveNet: 1M chars/month

## Integration with Your Project

Replace OpenAI TTS calls:

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

**After (Google Cloud):**
```python
from google.cloud import texttospeech
client = texttospeech.TextToSpeechClient()
response = client.synthesize_speech(
    input=texttospeech.SynthesisInput(text=text),
    voice=texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Standard-C"  # or Neural2-C for better quality
    ),
    audio_config=texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
)
```

## Recommendations

- **For notifications/feedback** (your use case): Use **Standard voices** ($4/million)
- **For premium experiences**: Use **Neural2 voices** ($16/million, still cheaper setup than OpenAI when counting free tier)
- **Vietnamese support**: Full support with multiple voices

## Documentation

- [Google Cloud TTS Pricing](https://cloud.google.com/text-to-speech/pricing)
- [Python Client Library](https://cloud.google.com/text-to-speech/docs/libraries#client-libraries-install-python)
- [Voice List](https://cloud.google.com/text-to-speech/docs/voices)
