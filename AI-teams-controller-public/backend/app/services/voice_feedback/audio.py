# -*- coding: utf-8 -*-
"""Audio generation for voice feedback.

Single Responsibility: Generate TTS audio from text.

Caching Strategy (Story: TTS Caching):
    - Only cache SHORT texts (≤50 chars) to avoid caching unique dynamic content
    - Short texts like "input on", "task complete", "recording started" repeat often
    - Long dynamic summaries are unique and not worth caching
    - Uses MD5 hash of text as cache key
    - File-based cache in backend/cache/tts/
"""

import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Cache configuration
MAX_CACHE_LENGTH = 50  # Only cache texts ≤50 characters
TTS_CACHE_DIR = Path(__file__).parent.parent.parent.parent / "cache" / "tts"


def _ensure_cache_dir(cache_dir: Path = TTS_CACHE_DIR) -> None:
    """Ensure cache directory exists."""
    cache_dir.mkdir(parents=True, exist_ok=True)


def _get_cache_path(text: str) -> Path:
    """Get cache file path for given text."""
    text_hash = hashlib.md5(text.encode()).hexdigest()
    return TTS_CACHE_DIR / f"{text_hash}.mp3"


def _get_cached_audio(text: str) -> str | None:
    """Get cached audio for text if it exists.

    Returns:
        Base64-encoded audio string if cached, None otherwise.
    """
    if len(text) > MAX_CACHE_LENGTH:
        return None

    cache_path = _get_cache_path(text)
    if cache_path.exists():
        logger.info(f"[AUDIO] TTS cache HIT: {text[:30]}...")
        return cache_path.read_text()
    return None


def _cache_audio(text: str, audio_base64: str) -> None:
    """Cache audio for text if eligible (≤50 chars)."""
    if len(text) > MAX_CACHE_LENGTH:
        return

    _ensure_cache_dir()
    cache_path = _get_cache_path(text)
    cache_path.write_text(audio_base64)
    logger.info(f"[AUDIO] TTS cached: {text[:30]}...")


def generate_tts(text: str, speed: float = 1.0) -> str:
    """Generate TTS audio using configured TTS provider.

    Caching (for short texts ≤50 chars):
    - Check cache first (by MD5 hash of text)
    - If cache HIT, return cached audio (skip API call)
    - If cache MISS, call TTS API and cache result

    Provider is selected via TTS_PROVIDER environment variable:
    - "openai": OpenAI TTS ($15/million, 200ms)
    - "google": Google Cloud TTS Standard ($4/million, 200ms) - DEFAULT
    - "hdtts": HD-TTS API (Vietnamese-specialized)

    Args:
        text: Text to convert to speech
        speed: Speech speed (0.5-2.0, default 1.0 = normal)

    Returns:
        Base64-encoded audio (MP3 format), empty string on error
    """
    from app.services.tts_providers import TTSProviderFactory

    # Check cache first (only for short texts)
    cached_audio = _get_cached_audio(text)
    if cached_audio is not None:
        return cached_audio

    try:
        # Create provider from environment variable with speed parameter
        tts_provider = TTSProviderFactory.create(speed=speed)

        # Generate speech and return as base64
        audio_base64 = tts_provider.generate_speech_base64(text)

        logger.info(f"[AUDIO] TTS generated: {len(audio_base64)} chars (base64)")

        # Cache the result (only for short texts)
        _cache_audio(text, audio_base64)

        return audio_base64

    except ValueError as e:
        # Provider configuration error (e.g., unknown provider, missing API key)
        # Re-raise to propagate error to API endpoint (AC5)
        logger.error(f"[AUDIO] TTS provider error: {e}")
        raise
    except Exception as e:
        # TTS generation failed
        logger.error(f"[AUDIO] TTS generation failed: {e}")
        return ""
