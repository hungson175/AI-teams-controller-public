# -*- coding: utf-8 -*-
"""Tests for TTS providers - Vietnamese language support.

TDD: Tests for mixed English/Vietnamese TTS using Google Cloud.
Vietnamese (vi-VN) is the default language for voice feedback.
"""

import io
import os
from unittest.mock import MagicMock, patch

import pytest


class TestGoogleCloudTTSProviderVietnamese:
    """Tests for Google Cloud TTS provider with Vietnamese language."""

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"})
    @patch("google.cloud.texttospeech.TextToSpeechClient")
    def test_default_language_is_vietnamese(self, mock_client):
        """Should use vi-VN as default language code."""
        from app.services.tts_providers import GoogleCloudTTSProvider

        provider = GoogleCloudTTSProvider()

        assert provider.language_code == "vi-VN"

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"})
    @patch("google.cloud.texttospeech.TextToSpeechClient")
    def test_default_voice_is_vietnamese_standard_a(self, mock_client):
        """Should use vi-VN-Standard-A as default voice."""
        from app.services.tts_providers import GoogleCloudTTSProvider

        provider = GoogleCloudTTSProvider()

        assert provider.get_default_voice() == "vi-VN-Standard-A"

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"})
    @patch("google.cloud.texttospeech.TextToSpeechClient")
    def test_available_voices_are_vietnamese(self, mock_client):
        """Should return Vietnamese voice options."""
        from app.services.tts_providers import GoogleCloudTTSProvider

        provider = GoogleCloudTTSProvider()
        voices = provider.get_available_voices()

        assert all("vi-VN" in voice for voice in voices)
        assert "vi-VN-Standard-A" in voices

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"})
    @patch("google.cloud.texttospeech.TextToSpeechClient")
    def test_generate_speech_uses_vietnamese_voice(self, mock_client):
        """Should use Vietnamese voice parameters when generating speech."""
        from app.services.tts_providers import GoogleCloudTTSProvider

        mock_response = MagicMock()
        mock_response.audio_content = b"fake_audio_bytes"
        mock_client.return_value.synthesize_speech.return_value = mock_response

        provider = GoogleCloudTTSProvider()
        result = provider.generate_speech("Xin chào, hello world!")

        assert result == b"fake_audio_bytes"

        # Verify voice params used Vietnamese
        call_args = mock_client.return_value.synthesize_speech.call_args
        voice_params = call_args.kwargs.get("voice") or call_args[1].get("voice")
        assert voice_params.language_code == "vi-VN"
        assert voice_params.name == "vi-VN-Standard-A"

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"})
    @patch("google.cloud.texttospeech.TextToSpeechClient")
    def test_mixed_language_text_handled(self, mock_client):
        """Should handle mixed English/Vietnamese text (Google auto-detects)."""
        from app.services.tts_providers import GoogleCloudTTSProvider

        mock_response = MagicMock()
        mock_response.audio_content = b"mixed_audio"
        mock_client.return_value.synthesize_speech.return_value = mock_response

        provider = GoogleCloudTTSProvider()

        # Mixed EN/VI text like actual voice feedback
        mixed_text = "Task completed successfully. Đã fix xong bug trong API endpoint."
        result = provider.generate_speech(mixed_text)

        assert result == b"mixed_audio"
        # Verify the text was passed to synthesize
        call_args = mock_client.return_value.synthesize_speech.call_args
        synthesis_input = call_args.kwargs.get("input") or call_args[1].get("input")
        assert synthesis_input.text == mixed_text


class TestTTSProviderFactory:
    """Tests for TTS provider factory."""

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"})
    @patch("google.cloud.texttospeech.TextToSpeechClient")
    def test_factory_creates_google_provider_by_default(self, mock_client):
        """Factory should create Google provider when TTS_PROVIDER=google."""
        from app.services.tts_providers import GoogleCloudTTSProvider, TTSProviderFactory

        with patch.dict(os.environ, {"TTS_PROVIDER": "google"}):
            provider = TTSProviderFactory.create()

        assert isinstance(provider, GoogleCloudTTSProvider)

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"})
    @patch("google.cloud.texttospeech.TextToSpeechClient")
    def test_google_provider_uses_vietnamese_defaults(self, mock_client):
        """Google provider from factory should use Vietnamese defaults."""
        from app.services.tts_providers import TTSProviderFactory

        with patch.dict(os.environ, {"TTS_PROVIDER": "google"}):
            provider = TTSProviderFactory.create()

        assert provider.language_code == "vi-VN"
        assert provider.get_default_voice() == "vi-VN-Standard-A"


class TestProviderRegistryOCP:
    """Tests for OCP compliance - registry-only provider creation (Sprint 6)."""

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"})
    @patch("google.cloud.texttospeech.TextToSpeechClient")
    def test_google_provider_via_registry(self, mock_client):
        """Google provider should be created via registry, not legacy fallback."""
        from app.services.tts_providers import GoogleCloudTTSProvider, TTSProviderFactory

        # Verify google is in registry
        assert "google" in TTSProviderFactory._registry

        # Create via factory
        provider = TTSProviderFactory.create("google")

        # Should be correct type from registry
        assert isinstance(provider, GoogleCloudTTSProvider)

    def test_unknown_provider_error_from_registry_only(self):
        """Unknown provider should raise error based on registry contents only."""
        from app.services.tts_providers import TTSProviderFactory

        with pytest.raises(ValueError) as exc_info:
            TTSProviderFactory.create("unknown_provider")

        error_msg = str(exc_info.value)
        # Error should mention the unknown provider
        assert "unknown_provider" in error_msg.lower()
        # Error should list available providers from registry
        assert "available" in error_msg.lower() or "unknown" in error_msg.lower()


class TestProviderRegistry:
    """Tests for provider registry pattern (TDD for Sprint 15)."""

    def test_register_provider_adds_to_registry(self):
        """Registry decorator should add provider to _registry dict."""
        from app.services.tts_providers import TTSProvider, TTSProviderFactory

        # Create a test provider
        @TTSProviderFactory.register("test_provider")
        class TestProvider(TTSProvider):
            def generate_speech(self, text: str, voice=None) -> bytes:
                return b"test"

            def get_available_voices(self) -> list[str]:
                return ["test_voice"]

            def get_default_voice(self) -> str:
                return "test_voice"

        # Verify it's in registry
        assert "test_provider" in TTSProviderFactory._registry
        assert TTSProviderFactory._registry["test_provider"] == TestProvider

    def test_create_registered_provider(self):
        """Factory should create instance of registered provider."""
        from app.services.tts_providers import TTSProvider, TTSProviderFactory

        # Register test provider
        @TTSProviderFactory.register("custom_tts")
        class CustomTTSProvider(TTSProvider):
            def generate_speech(self, text: str, voice=None) -> bytes:
                return b"custom_audio"

            def get_available_voices(self) -> list[str]:
                return ["custom_voice"]

            def get_default_voice(self) -> str:
                return "custom_voice"

        # Create via factory
        provider = TTSProviderFactory.create("custom_tts")

        # Verify correct type
        assert isinstance(provider, CustomTTSProvider)
        assert provider.generate_speech("test") == b"custom_audio"

    def test_create_unknown_provider_raises_error(self):
        """Factory should raise ValueError for unknown provider with helpful message."""
        from app.services.tts_providers import TTSProviderFactory

        with pytest.raises(ValueError) as exc_info:
            TTSProviderFactory.create("nonexistent_provider")

        # Error message should include provider name and available options
        error_msg = str(exc_info.value)
        assert "nonexistent_provider" in error_msg
        assert "Available" in error_msg or "Supported" in error_msg


class TestHDTTSProvider:
    """Tests for HD-TTS provider implementation (TDD for Sprint 15)."""

    @patch("pydub.AudioSegment")
    @patch("io.BytesIO")
    @patch("requests.post")
    @patch.dict(os.environ, {"HDTTS_API_KEY": "test_key_123"})
    def test_hdtts_generate_speech_calls_api(self, mock_post, mock_bytesio, mock_audio_segment):
        """HDTTSProvider should call HD-TTS API and return audio bytes."""
        from app.services.tts_providers import HDTTSProvider

        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake_wav_audio_bytes"
        mock_post.return_value = mock_response

        # Mock pydub conversion
        mock_segment = MagicMock()
        mock_audio_segment.from_wav.return_value = mock_segment

        # Mock BytesIO for both WAV and MP3 buffers
        mock_wav_buffer = MagicMock()
        mock_mp3_buffer = MagicMock()
        mock_mp3_buffer.getvalue.return_value = b"fake_mp3_bytes"
        mock_bytesio.side_effect = [mock_wav_buffer, mock_mp3_buffer]

        provider = HDTTSProvider()
        result = provider.generate_speech("Test text")

        # Verify API was called
        assert mock_post.called
        assert result == b"fake_mp3_bytes"

    @patch("pydub.AudioSegment")
    @patch("requests.post")
    @patch.dict(os.environ, {"HDTTS_API_KEY": "test_api_key"})
    def test_hdtts_sends_correct_auth_header(self, mock_post, mock_audio_segment):
        """HDTTSProvider should send X-API-Key header with API key."""
        from app.services.tts_providers import HDTTSProvider

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"audio"
        mock_post.return_value = mock_response

        # Mock pydub
        mock_segment = MagicMock()
        mock_segment.export.return_value.__enter__.return_value.read.return_value = b"mp3"
        mock_audio_segment.from_wav.return_value = mock_segment

        provider = HDTTSProvider()
        provider.generate_speech("Test")

        # Verify X-API-Key header was sent
        call_args = mock_post.call_args
        headers = call_args.kwargs.get("headers", {})
        assert "X-API-Key" in headers
        assert headers["X-API-Key"] == "test_api_key"

    @patch("pydub.AudioSegment")
    @patch("requests.post")
    @patch.dict(os.environ, {"HDTTS_API_KEY": "key123"})
    def test_hdtts_uses_default_params(self, mock_post, mock_audio_segment):
        """HDTTSProvider should use female, northern, high quality by default."""
        from app.services.tts_providers import HDTTSProvider

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"audio"
        mock_post.return_value = mock_response

        # Mock pydub
        mock_segment = MagicMock()
        mock_segment.export.return_value.__enter__.return_value.read.return_value = b"mp3"
        mock_audio_segment.from_wav.return_value = mock_segment

        provider = HDTTSProvider()
        provider.generate_speech("Xin chào")

        # Verify default params in request body
        call_args = mock_post.call_args
        json_data = call_args.kwargs.get("json", {})
        assert json_data.get("gender") == "female"
        assert json_data.get("area") == "northern"
        assert json_data.get("quality") == "high"

    def test_hdtts_missing_api_key_raises_error(self):
        """HDTTSProvider should raise ValueError if API key not set."""
        from app.services.tts_providers import HDTTSProvider

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                HDTTSProvider()

            assert "HDTTS_API_KEY" in str(exc_info.value)

    @patch("requests.post")
    @patch.dict(os.environ, {"HDTTS_API_KEY": "key123"})
    def test_hdtts_get_default_voice(self, mock_post):
        """HDTTSProvider should return descriptive default voice string."""
        from app.services.tts_providers import HDTTSProvider

        provider = HDTTSProvider()
        default_voice = provider.get_default_voice()

        # Should describe the default configuration
        assert "female" in default_voice.lower()
        assert "northern" in default_voice.lower()

    @patch("requests.post")
    @patch.dict(os.environ, {"HDTTS_API_KEY": "key123"})
    def test_hdtts_get_available_voices(self, mock_post):
        """HDTTSProvider should return list of voice configuration options."""
        from app.services.tts_providers import HDTTSProvider

        provider = HDTTSProvider()
        voices = provider.get_available_voices()

        # Should return list with gender/area combinations
        assert isinstance(voices, list)
        assert len(voices) > 0
        # At least have female/male and northern/southern/central
        assert any("female" in v.lower() for v in voices)
        assert any("male" in v.lower() for v in voices)

    @patch("pydub.AudioSegment")
    @patch("io.BytesIO")
    @patch("requests.post")
    @patch.dict(os.environ, {"HDTTS_API_KEY": "key123"})
    def test_hdtts_converts_wav_to_mp3(self, mock_post, mock_bytesio, mock_audio_segment):
        """HDTTSProvider should convert WAV response to MP3 format (TL spec update)."""
        from app.services.tts_providers import HDTTSProvider

        # Mock HD-TTS API returning WAV
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake_wav_bytes"
        mock_post.return_value = mock_response

        # Mock pydub conversion
        mock_segment = MagicMock()
        mock_audio_segment.from_wav.return_value = mock_segment

        # Mock BytesIO
        mock_wav_buffer = MagicMock()
        mock_mp3_buffer = MagicMock()
        mock_mp3_buffer.getvalue.return_value = b"fake_mp3_bytes"
        mock_bytesio.side_effect = [mock_wav_buffer, mock_mp3_buffer]

        provider = HDTTSProvider()
        result = provider.generate_speech("Test")

        # Verify conversion was called
        assert mock_audio_segment.from_wav.called
        mock_segment.export.assert_called_once()

        # Verify export format was MP3
        export_call_args = mock_segment.export.call_args
        assert export_call_args.kwargs.get("format") == "mp3"

        # Verify returns MP3 bytes
        assert result == b"fake_mp3_bytes"

    @patch("pydub.AudioSegment")
    @patch("requests.post")
    @patch.dict(os.environ, {"HDTTS_API_KEY": "key123"})
    def test_hdtts_speed_parameter_default(self, mock_post, mock_audio_segment):
        """HDTTSProvider should use speed=2.0 as default for testing."""
        from app.services.tts_providers import HDTTSProvider

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"audio"
        mock_post.return_value = mock_response

        mock_segment = MagicMock()
        mock_segment.export.return_value.__enter__.return_value.read.return_value = b"mp3"
        mock_audio_segment.from_wav.return_value = mock_segment

        provider = HDTTSProvider()
        provider.generate_speech("Test")

        # Verify speed parameter was sent
        call_args = mock_post.call_args
        json_data = call_args.kwargs.get("json", {})
        assert json_data.get("speed") == 2.0

    @patch("pydub.AudioSegment")
    @patch("requests.post")
    @patch.dict(os.environ, {"HDTTS_API_KEY": "key123", "HDTTS_SPEED": "0.5"})
    def test_hdtts_speed_env_override(self, mock_post, mock_audio_segment):
        """HDTTS_SPEED env var should override constructor default speed."""
        from app.services.tts_providers import HDTTSProvider

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"audio"
        mock_post.return_value = mock_response

        mock_segment = MagicMock()
        mock_segment.export.return_value.__enter__.return_value.read.return_value = b"mp3"
        mock_audio_segment.from_wav.return_value = mock_segment

        provider = HDTTSProvider()
        provider.generate_speech("Test")

        # Verify speed 0.5 was used (production setting)
        call_args = mock_post.call_args
        json_data = call_args.kwargs.get("json", {})
        assert json_data.get("speed") == 0.5

    @patch("pydub.AudioSegment")
    @patch("requests.post")
    @patch.dict(os.environ, {"HDTTS_API_KEY": "key123"})
    def test_hdtts_speed_range_validation(self, mock_post, mock_audio_segment):
        """HDTTSProvider should accept speed range 0.5-2.0."""
        from app.services.tts_providers import HDTTSProvider

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"audio"
        mock_post.return_value = mock_response

        mock_segment = MagicMock()
        mock_segment.export.return_value.__enter__.return_value.read.return_value = b"mp3"
        mock_audio_segment.from_wav.return_value = mock_segment

        # Test various speed values in valid range
        test_speeds = [0.5, 0.8, 1.0, 1.5, 2.0]
        for speed in test_speeds:
            provider = HDTTSProvider(speed=speed)
            provider.generate_speech("Test")

            call_args = mock_post.call_args
            json_data = call_args.kwargs.get("json", {})
            assert json_data.get("speed") == speed


class TestProviderIntegration:
    """Integration tests for all TTS providers (TDD for Sprint 15)."""

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"})
    @patch("google.cloud.texttospeech.TextToSpeechClient")
    @patch.dict(os.environ, {"HDTTS_API_KEY": "fake_hdtts_key"})
    @patch("requests.post")
    def test_factory_creates_all_providers(self, mock_requests, mock_google_client):
        """Factory should be able to create all registered providers."""
        from app.services.tts_providers import (
            GoogleCloudTTSProvider,
            HDTTSProvider,
            TTSProviderFactory,
        )

        # Mock HD-TTS response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"audio"
        mock_requests.return_value = mock_response

        # Test creating each provider
        google_provider = TTSProviderFactory.create("google")
        assert isinstance(google_provider, GoogleCloudTTSProvider)

        hdtts_provider = TTSProviderFactory.create("hdtts")
        assert isinstance(hdtts_provider, HDTTSProvider)

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"})
    @patch("google.cloud.texttospeech.TextToSpeechClient")
    @patch.dict(os.environ, {"HDTTS_API_KEY": "fake_hdtts_key"})
    @patch("requests.post")
    def test_all_providers_implement_interface(self, mock_requests, mock_google_client):
        """All providers should implement TTSProvider abstract methods."""
        from app.services.tts_providers import TTSProvider, TTSProviderFactory

        # Mock HD-TTS response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"audio"
        mock_requests.return_value = mock_response

        providers = [
            TTSProviderFactory.create("google"),
            TTSProviderFactory.create("hdtts"),
        ]

        for provider in providers:
            # Verify instance of base class
            assert isinstance(provider, TTSProvider)

            # Verify all abstract methods implemented
            assert hasattr(provider, "generate_speech")
            assert hasattr(provider, "get_available_voices")
            assert hasattr(provider, "get_default_voice")

            # Verify methods are callable
            assert callable(provider.generate_speech)
            assert callable(provider.get_available_voices)
            assert callable(provider.get_default_voice)

    def test_unknown_provider_raises_error(self):
        """Factory should raise ValueError for unknown TTS provider (AC5)."""
        from app.services.tts_providers import TTSProviderFactory

        with pytest.raises(ValueError, match="Unknown TTS provider: unknown"):
            TTSProviderFactory.create("unknown")

    def test_validate_provider_raises_for_unknown(self):
        """validate_provider should raise ValueError for unknown provider (AC5)."""
        from app.services.tts_providers import TTSProviderFactory

        with pytest.raises(ValueError, match="Unknown TTS provider: unknown"):
            TTSProviderFactory.validate_provider("unknown")

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"})
    @patch("google.cloud.texttospeech.TextToSpeechClient")
    def test_validate_provider_passes_for_known(self, mock_client):
        """validate_provider should pass for known provider."""
        from app.services.tts_providers import TTSProviderFactory

        # Should not raise
        TTSProviderFactory.validate_provider("google")
