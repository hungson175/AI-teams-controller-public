# -*- coding: utf-8 -*-
"""Tests for voice_feedback.audio module.

TDD: Tests for TTS audio generation.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestGenerateTTS:
    """Tests for generate_tts function."""

    @patch("app.services.voice_feedback.audio._get_cached_audio", return_value=None)
    @patch("app.services.voice_feedback.audio._cache_audio")
    @patch("app.services.tts_providers.TTSProviderFactory")
    def test_tts_success(self, mock_factory, mock_cache, mock_get_cache):
        """Should generate TTS audio successfully."""
        from app.services.voice_feedback.audio import generate_tts

        mock_provider = MagicMock()
        mock_provider.generate_speech_base64.return_value = "base64audiodata"
        mock_factory.create.return_value = mock_provider

        result = generate_tts("Hello world")

        assert result == "base64audiodata"
        mock_provider.generate_speech_base64.assert_called_once_with("Hello world")

    @patch("app.services.voice_feedback.audio._get_cached_audio", return_value=None)
    @patch("app.services.tts_providers.TTSProviderFactory")
    def test_tts_provider_error(self, mock_factory, mock_get_cache):
        """Should raise ValueError on provider configuration error (AC5)."""
        from app.services.voice_feedback.audio import generate_tts

        mock_factory.create.side_effect = ValueError("Unknown TTS provider: unknown")

        # AC5: Unknown provider should raise error, not silently succeed
        with pytest.raises(ValueError, match="Unknown TTS provider"):
            generate_tts("Test text")

    @patch("app.services.voice_feedback.audio._get_cached_audio", return_value=None)
    @patch("app.services.tts_providers.TTSProviderFactory")
    def test_tts_generation_error(self, mock_factory, mock_get_cache):
        """Should return empty string on TTS generation error."""
        from app.services.voice_feedback.audio import generate_tts

        mock_provider = MagicMock()
        mock_provider.generate_speech_base64.side_effect = Exception("API error")
        mock_factory.create.return_value = mock_provider

        result = generate_tts("Test text")

        assert result == ""

    @patch("app.services.voice_feedback.audio._get_cached_audio", return_value=None)
    @patch("app.services.voice_feedback.audio._cache_audio")
    @patch("app.services.tts_providers.TTSProviderFactory")
    def test_tts_empty_text(self, mock_factory, mock_cache, mock_get_cache):
        """Should handle empty text input."""
        from app.services.voice_feedback.audio import generate_tts

        mock_provider = MagicMock()
        mock_provider.generate_speech_base64.return_value = ""
        mock_factory.create.return_value = mock_provider

        result = generate_tts("")

        assert result == ""
        mock_provider.generate_speech_base64.assert_called_once_with("")

    @patch("app.services.voice_feedback.audio._get_cached_audio", return_value=None)
    @patch("app.services.voice_feedback.audio._cache_audio")
    @patch("app.services.tts_providers.TTSProviderFactory")
    def test_tts_uses_factory(self, mock_factory, mock_cache, mock_get_cache):
        """Should use TTSProviderFactory.create()."""
        from app.services.voice_feedback.audio import generate_tts

        mock_provider = MagicMock()
        mock_provider.generate_speech_base64.return_value = "audio"
        mock_factory.create.return_value = mock_provider

        generate_tts("text")

        mock_factory.create.assert_called_once()
