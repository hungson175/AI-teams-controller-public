"""
TTS Provider Abstraction - Switchable TTS Providers

Architecture based on proven provider pattern (90% cost reduction success story):
- Abstract base class defines common interface
- Provider-specific implementations handle API differences
- Factory pattern enables switching via environment variable
- No code changes needed when switching providers

Supported Providers:
- OpenAI TTS (tts-1): $15/million chars, 200ms latency
- Google Cloud TTS Standard: $4/million chars (73% cheaper), 200ms latency

Usage:
    from app.services.tts_providers import TTSProviderFactory

    # Create provider from environment variable (TTS_PROVIDER)
    tts = TTSProviderFactory.create()
    audio_bytes = tts.generate_speech("Hello world")

    # Or create specific provider
    tts = TTSProviderFactory.create("google")
"""

import base64
import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class TTSProvider(ABC):
    """Abstract base class for TTS providers.

    All TTS providers must implement these methods to ensure
    consistent interface regardless of underlying service.
    """

    @abstractmethod
    def generate_speech(self, text: str, voice: Optional[str] = None) -> bytes:
        """Generate speech audio from text.

        Args:
            text: Text to convert to speech
            voice: Voice name (provider-specific), uses default if None

        Returns:
            Audio data as bytes (MP3 format)
        """
        pass

    @abstractmethod
    def get_available_voices(self) -> list[str]:
        """Return list of available voice names for this provider."""
        pass

    @abstractmethod
    def get_default_voice(self) -> str:
        """Return default voice name for this provider."""
        pass

    def generate_speech_base64(self, text: str, voice: Optional[str] = None) -> str:
        """Generate speech and return as base64-encoded string.

        Convenience method for APIs that need base64 audio.
        """
        audio_bytes = self.generate_speech(text, voice)
        return base64.b64encode(audio_bytes).decode()


class TTSProviderFactory:
    """Factory for creating TTS provider instances.

    Enables switching providers via configuration without code changes.
    Uses registry pattern for extensibility (Open-Closed Principle).
    """

    _registry: dict[str, type[TTSProvider]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a TTS provider class.

        Example:
            @TTSProviderFactory.register("hdtts")
            class HDTTSProvider(TTSProvider):
                ...
        """

        def decorator(provider_class: type[TTSProvider]):
            cls._registry[name] = provider_class
            return provider_class

        return decorator

    @staticmethod
    def create(provider_name: Optional[str] = None, speed: float = 2.0) -> TTSProvider:
        """Create TTS provider from name or environment variable.

        Args:
            provider_name: Provider name (e.g., "openai", "google", "hdtts")
                         If None, uses TTS_PROVIDER env var (default: "openai")
            speed: Speech speed for HD-TTS provider (0.5-2.0, ignored for other providers)

        Returns:
            Initialized TTS provider instance

        Raises:
            ValueError: If provider name is unknown

        Example:
            # Use environment variable
            os.environ["TTS_PROVIDER"] = "google"
            tts = TTSProviderFactory.create()

            # Or specify explicitly with speed
            tts = TTSProviderFactory.create("hdtts", speed=0.7)
        """
        provider = (provider_name or os.getenv("TTS_PROVIDER", "google")).lower()

        logger.info(f"[TTS] Creating provider: {provider}")

        # Sprint 6 - OCP fix: Use registry only (removed legacy hardcoded fallback)
        if provider not in TTSProviderFactory._registry:
            available_providers = list(TTSProviderFactory._registry.keys())
            raise ValueError(
                f"Unknown TTS provider: {provider}. "
                f"Available: {available_providers}"
            )

        # HD-TTS needs speed parameter
        if provider == "hdtts":
            return TTSProviderFactory._registry[provider](speed=speed)
        else:
            return TTSProviderFactory._registry[provider]()

    @staticmethod
    def create_from_config(config: dict) -> TTSProvider:
        """Create TTS provider from configuration dictionary.

        Args:
            config: Configuration dict with 'provider' key

        Example:
            config = {"provider": "google", "voice_type": "Standard"}
            tts = TTSProviderFactory.create_from_config(config)
        """
        provider_name = config.get("provider", "google")
        return TTSProviderFactory.create(provider_name)

    @staticmethod
    def validate_provider(provider_name: Optional[str] = None) -> None:
        """Validate that TTS provider is configured correctly.

        This is an EAGER validation method to be called at API entry points
        BEFORE queueing async tasks. Raises ValueError immediately if provider
        is unknown or misconfigured.

        Args:
            provider_name: Provider name to validate (uses TTS_PROVIDER env if None)

        Raises:
            ValueError: If provider is unknown or misconfigured

        Example:
            # At API endpoint before queueing Celery task
            TTSProviderFactory.validate_provider()  # Raises if TTS_PROVIDER is invalid
        """
        provider = (provider_name or os.getenv("TTS_PROVIDER", "google")).lower()

        # Check if provider exists in registry
        if provider not in TTSProviderFactory._registry:
            # Legacy support check (google not yet migrated to registry)
            if provider not in ["google"]:
                available_providers = list(TTSProviderFactory._registry.keys()) + ["google"]
                raise ValueError(
                    f"Unknown TTS provider: {provider}. "
                    f"Available: {available_providers}"
                )

        # Try creating instance (will fail if API keys missing, etc.)
        try:
            _ = TTSProviderFactory.create(provider_name)
        except ValueError:
            # Re-raise provider configuration errors
            raise
        except Exception as e:
            # Wrap other errors as ValueError for consistency
            raise ValueError(f"TTS provider '{provider}' misconfigured: {str(e)[:100]}")


@TTSProviderFactory.register("google")
class GoogleCloudTTSProvider(TTSProvider):
    """Google Cloud TTS implementation (Standard voices).

    Cost: $4/million characters (73% cheaper than OpenAI)
    Free tier: 4 million characters/month
    Quality: Decent, acceptable for notifications
    Speed: ~200ms latency

    Default: Vietnamese (vi-VN) for mixed EN/VI voice feedback.
    Google Cloud TTS automatically handles mixed English/Vietnamese text.
    Available voices: vi-VN-Standard-A through D, vi-VN-Wavenet-A through D
    Using Standard voices by default for cost savings.
    """

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        language_code: str = "vi-VN",
        voice_type: str = "Standard"
    ):
        """Initialize Google Cloud TTS provider.

        Args:
            credentials_path: Path to service account JSON key
                            (uses GOOGLE_APPLICATION_CREDENTIALS env var if None)
            language_code: Language code (default: "en-US")
            voice_type: Voice type "Standard" ($4/million) or "Neural2" ($16/million)
        """
        from google.cloud import texttospeech

        # Set credentials if provided
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        elif not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            raise ValueError(
                "GOOGLE_APPLICATION_CREDENTIALS not set. "
                "Set env var or pass credentials_path parameter."
            )

        self.client = texttospeech.TextToSpeechClient()
        self.language_code = language_code
        self.voice_type = voice_type

        # Google-specific audio config
        self.audio_encoding = texttospeech.AudioEncoding.MP3
        self.sample_rate = 24000  # 24kHz for better quality

        logger.info(
            f"[TTS] Initialized Google Cloud TTS provider "
            f"(lang={language_code}, type={voice_type})"
        )

    def generate_speech(self, text: str, voice: Optional[str] = None) -> bytes:
        """Generate speech using Google Cloud TTS API."""
        from google.cloud import texttospeech

        voice_name = voice or self.get_default_voice()

        logger.info(
            f"[TTS] Google Cloud generating speech: "
            f"{len(text)} chars, voice={voice_name}"
        )

        # Configure synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Configure voice parameters
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=self.language_code,
            name=voice_name
        )

        # Configure audio output
        audio_config = texttospeech.AudioConfig(
            audio_encoding=self.audio_encoding,
            sample_rate_hertz=self.sample_rate
        )

        # Generate speech
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )

        return response.audio_content

    def get_available_voices(self) -> list[str]:
        """Return commonly used Google Cloud voices.

        Note: Google has many more voices. These are the most commonly used.
        Full list: https://cloud.google.com/text-to-speech/docs/voices
        """
        if self.voice_type == "Neural2":
            # Neural2 voices (premium, $16/million)
            return [
                f"{self.language_code}-Neural2-A",  # Female
                f"{self.language_code}-Neural2-C",  # Female
                f"{self.language_code}-Neural2-D",  # Male
                f"{self.language_code}-Neural2-F",  # Female
            ]
        else:
            # Standard voices (cheap, $4/million)
            return [
                f"{self.language_code}-Standard-A",  # Male
                f"{self.language_code}-Standard-B",  # Male
                f"{self.language_code}-Standard-C",  # Female
                f"{self.language_code}-Standard-D",  # Male
            ]

    def get_default_voice(self) -> str:
        """Return default Google Cloud voice.

        Using Standard-A for Vietnamese (vi-VN-Standard-A is female voice).
        """
        if self.voice_type == "Neural2":
            return f"{self.language_code}-Neural2-A"
        else:
            return f"{self.language_code}-Standard-A"


@TTSProviderFactory.register("hdtts")
class HDTTSProvider(TTSProvider):
    """HD-TTS provider implementation.

    Cost: TBD (self-hosted)
    Quality: High quality Vietnamese TTS
    Output: MP3 format (converts from WAV)
    Speed: ~2.5-5s depending on quality setting

    Default configuration:
    - Gender: female
    - Area: northern (Vietnamese accent)
    - Quality: high (NFE=32)

    Note: HD-TTS API returns WAV format. This provider automatically
    converts to MP3 for consistency with other providers.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        gender: str = "female",
        area: str = "northern",
        quality: str = "high",
        speed: float = 2.0,  # MAX SPEED - testing speed param
        emotion: str = "neutral",  # Fixed emotion for consistency
        group: str = "news",  # Fixed group for consistency
    ):
        """Initialize HD-TTS provider.

        Args:
            api_key: HD-TTS API key (uses HDTTS_API_KEY env var if None)
            api_url: HD-TTS API base URL (uses HDTTS_API_URL env var if None)
            gender: Voice gender ("male" or "female")
            area: Voice accent ("northern", "southern", "central")
            quality: Quality setting ("high" or "fast")
            speed: Speech speed 0.5-2.0 (default 2.0, MAX SPEED for testing)
            emotion: Voice emotion (neutral/happy/sad/angry/surprised/serious)
            group: Voice style (story/news/audiobook/interview/review)
        """
        self.api_key = api_key or os.getenv("HDTTS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "HDTTS_API_KEY not set. "
                "Set env var or pass api_key parameter."
            )

        self.api_url = api_url or os.getenv(
            "HDTTS_API_URL", "https://hd-tts-backend.hungson175.com"
        )
        self.gender = gender
        self.area = area
        self.quality = quality
        self.speed = speed  # Request parameter takes precedence
        self.emotion = emotion  # Fixed emotion
        self.group = group  # Fixed group

        logger.info(
            f"[TTS] Initialized HD-TTS provider "
            f"(gender={gender}, area={area}, quality={quality}, speed={self.speed}, "
            f"emotion={emotion}, group={group})"
        )

    def generate_speech(self, text: str, voice: Optional[str] = None) -> bytes:
        """Generate speech using HD-TTS API.

        Args:
            text: Text to convert to speech
            voice: Not used (HD-TTS uses gender/area/quality params)

        Returns:
            Audio data as MP3 bytes
        """
        import io

        import requests
        from pydub import AudioSegment

        logger.info(f"[TTS] HD-TTS generating speech: {len(text)} chars")

        # Prepare request - API key as query parameter (not header)
        url = f"{self.api_url}/synthesize?api_key={self.api_key}"
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "gender": self.gender,
            "area": self.area,
            "quality": self.quality,
            "speed": self.speed,
            "emotion": self.emotion,  # Fixed emotion for consistency
            "group": self.group,  # Fixed group for consistency
        }

        # Call HD-TTS API
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        # Convert WAV to MP3 (HD-TTS returns WAV, we need MP3 for consistency)
        wav_bytes = response.content
        audio_segment = AudioSegment.from_wav(io.BytesIO(wav_bytes))

        # Export to MP3
        mp3_buffer = io.BytesIO()
        audio_segment.export(mp3_buffer, format="mp3")
        mp3_bytes = mp3_buffer.getvalue()

        logger.info(f"[TTS] HD-TTS conversion: WAV {len(wav_bytes)} bytes → MP3 {len(mp3_bytes)} bytes")

        return mp3_bytes

    def get_available_voices(self) -> list[str]:
        """Return list of voice configuration options.

        HD-TTS doesn't use traditional "voices" but combinations of:
        - Gender: male, female
        - Area: northern, southern, central
        - Quality: high, fast
        """
        voices = []
        for gender in ["female", "male"]:
            for area in ["northern", "southern", "central"]:
                voices.append(f"{gender}-{area}")
        return voices

    def get_default_voice(self) -> str:
        """Return default voice configuration string."""
        return f"{self.gender}-{self.area} (quality: {self.quality})"
