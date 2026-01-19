# TTS Providers

Switchable text-to-speech provider system.

## Overview

Factory pattern enables switching TTS providers via environment variable without code changes.

**Location:** `backend/app/services/tts_providers.py`

## Usage

```python
from app.services.tts_providers import TTSProviderFactory

# Use environment variable (TTS_PROVIDER)
tts = TTSProviderFactory.create()
audio_bytes = tts.generate_speech("Task completed")

# Or specify provider explicitly
tts = TTSProviderFactory.create("google")
```

## Supported Providers

| Provider | Cost | Quality | Free Tier |
|----------|------|---------|-----------|
| **Google Cloud Standard** | $4/million chars | Good | 4M chars/month |
| **HD-TTS** (self-hosted) | Free | Excellent | Unlimited |

## Configuration

### Google Cloud TTS (Default)

```bash
TTS_PROVIDER=google
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### HD-TTS (Self-hosted)

```bash
TTS_PROVIDER=hdtts
HDTTS_API_KEY=your-key
HDTTS_API_URL=https://your-hdtts-server.com
```

## Provider Interface

```python
class TTSProvider(ABC):
    @abstractmethod
    def generate_speech(self, text: str, voice: Optional[str] = None) -> bytes:
        """Generate MP3 audio from text."""
        pass

    @abstractmethod
    def get_available_voices(self) -> list[str]:
        """Return available voice names."""
        pass

    @abstractmethod
    def get_default_voice(self) -> str:
        """Return default voice."""
        pass
```

## Adding New Providers

```python
@TTSProviderFactory.register("myProvider")
class MyTTSProvider(TTSProvider):
    def generate_speech(self, text, voice=None):
        # Implementation
        return mp3_bytes
```
