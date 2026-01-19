# -*- coding: utf-8 -*-
"""Tests for TTS caching layer.

TDD: Tests for file-based TTS cache with short text optimization.
Only texts ≤50 characters are cached to avoid caching unique dynamic content.
"""

import hashlib
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestTTSCache:
    """Tests for TTS caching functionality."""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """Create a temporary cache directory for testing."""
        cache_dir = tmp_path / "tts_cache"
        cache_dir.mkdir()
        return cache_dir

    @patch("app.services.tts_providers.TTSProviderFactory")
    def test_cache_hit_short_text(self, mock_factory, temp_cache_dir):
        """Should return cached audio for short text (≤50 chars) without calling TTS API."""
        from app.services.voice_feedback.audio import generate_tts, TTS_CACHE_DIR, MAX_CACHE_LENGTH

        short_text = "task complete"
        assert len(short_text) <= MAX_CACHE_LENGTH

        # Pre-populate cache
        text_hash = hashlib.md5(short_text.encode()).hexdigest()
        cache_path = temp_cache_dir / f"{text_hash}.mp3"
        cached_audio = "Y2FjaGVkX2F1ZGlv"  # base64 for "cached_audio"
        cache_path.write_text(cached_audio)

        with patch("app.services.voice_feedback.audio.TTS_CACHE_DIR", temp_cache_dir):
            result = generate_tts(short_text)

        # Should return cached audio
        assert result == cached_audio
        # TTS API should NOT be called
        mock_factory.create.assert_not_called()

    @patch("app.services.tts_providers.TTSProviderFactory")
    def test_cache_miss_short_text(self, mock_factory, temp_cache_dir):
        """Should call TTS API and cache result for short text on cache miss."""
        from app.services.voice_feedback.audio import generate_tts, MAX_CACHE_LENGTH

        short_text = "input on"
        assert len(short_text) <= MAX_CACHE_LENGTH

        mock_provider = MagicMock()
        mock_provider.generate_speech_base64.return_value = "bmV3X2F1ZGlv"  # base64 for "new_audio"
        mock_factory.create.return_value = mock_provider

        with patch("app.services.voice_feedback.audio.TTS_CACHE_DIR", temp_cache_dir):
            result = generate_tts(short_text)

        # Should return generated audio
        assert result == "bmV3X2F1ZGlv"
        # TTS API should be called
        mock_provider.generate_speech_base64.assert_called_once_with(short_text)

        # Should cache the result
        text_hash = hashlib.md5(short_text.encode()).hexdigest()
        cache_path = temp_cache_dir / f"{text_hash}.mp3"
        assert cache_path.exists()
        assert cache_path.read_text() == "bmV3X2F1ZGlv"

    @patch("app.services.tts_providers.TTSProviderFactory")
    def test_no_cache_long_text(self, mock_factory, temp_cache_dir):
        """Should NOT cache text longer than MAX_CACHE_LENGTH (50 chars)."""
        from app.services.voice_feedback.audio import generate_tts, MAX_CACHE_LENGTH

        long_text = "This is a very long dynamic summary that should not be cached because it is unique"
        assert len(long_text) > MAX_CACHE_LENGTH

        mock_provider = MagicMock()
        mock_provider.generate_speech_base64.return_value = "bG9uZ19hdWRpbw=="
        mock_factory.create.return_value = mock_provider

        with patch("app.services.voice_feedback.audio.TTS_CACHE_DIR", temp_cache_dir):
            result = generate_tts(long_text)

        # Should return generated audio
        assert result == "bG9uZ19hdWRpbw=="
        # TTS API should be called
        mock_provider.generate_speech_base64.assert_called_once_with(long_text)

        # Should NOT cache the result
        text_hash = hashlib.md5(long_text.encode()).hexdigest()
        cache_path = temp_cache_dir / f"{text_hash}.mp3"
        assert not cache_path.exists()

    @patch("app.services.tts_providers.TTSProviderFactory")
    def test_cache_exactly_50_chars(self, mock_factory, temp_cache_dir):
        """Should cache text that is exactly MAX_CACHE_LENGTH (50 chars)."""
        from app.services.voice_feedback.audio import generate_tts, MAX_CACHE_LENGTH

        exact_text = "x" * 50
        assert len(exact_text) == MAX_CACHE_LENGTH

        mock_provider = MagicMock()
        mock_provider.generate_speech_base64.return_value = "ZXhhY3RfYXVkaW8="
        mock_factory.create.return_value = mock_provider

        with patch("app.services.voice_feedback.audio.TTS_CACHE_DIR", temp_cache_dir):
            result = generate_tts(exact_text)

        # Should cache the result
        text_hash = hashlib.md5(exact_text.encode()).hexdigest()
        cache_path = temp_cache_dir / f"{text_hash}.mp3"
        assert cache_path.exists()

    @patch("app.services.tts_providers.TTSProviderFactory")
    def test_no_cache_51_chars(self, mock_factory, temp_cache_dir):
        """Should NOT cache text that is 51 chars (over limit)."""
        from app.services.voice_feedback.audio import generate_tts, MAX_CACHE_LENGTH

        over_limit_text = "x" * 51
        assert len(over_limit_text) > MAX_CACHE_LENGTH

        mock_provider = MagicMock()
        mock_provider.generate_speech_base64.return_value = "b3Zlcl9saW1pdA=="
        mock_factory.create.return_value = mock_provider

        with patch("app.services.voice_feedback.audio.TTS_CACHE_DIR", temp_cache_dir):
            result = generate_tts(over_limit_text)

        # Should NOT cache the result
        text_hash = hashlib.md5(over_limit_text.encode()).hexdigest()
        cache_path = temp_cache_dir / f"{text_hash}.mp3"
        assert not cache_path.exists()

    def test_cache_dir_created_if_not_exists(self, tmp_path):
        """Should create cache directory if it doesn't exist."""
        from app.services.voice_feedback.audio import _ensure_cache_dir

        new_cache_dir = tmp_path / "new_tts_cache"
        assert not new_cache_dir.exists()

        _ensure_cache_dir(new_cache_dir)

        assert new_cache_dir.exists()
        assert new_cache_dir.is_dir()

    @patch("app.services.tts_providers.TTSProviderFactory")
    def test_cache_hit_prevents_duplicate_calls(self, mock_factory, temp_cache_dir):
        """Calling generate_tts twice with same short text should only call API once."""
        from app.services.voice_feedback.audio import generate_tts, MAX_CACHE_LENGTH

        short_text = "recording started"
        assert len(short_text) <= MAX_CACHE_LENGTH

        mock_provider = MagicMock()
        mock_provider.generate_speech_base64.return_value = "cmVjb3JkaW5n"
        mock_factory.create.return_value = mock_provider

        with patch("app.services.voice_feedback.audio.TTS_CACHE_DIR", temp_cache_dir):
            result1 = generate_tts(short_text)
            result2 = generate_tts(short_text)

        # Both should return same audio
        assert result1 == result2 == "cmVjb3JkaW5n"
        # API should only be called ONCE (first call)
        assert mock_provider.generate_speech_base64.call_count == 1
