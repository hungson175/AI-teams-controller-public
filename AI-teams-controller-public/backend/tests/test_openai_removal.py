# -*- coding: utf-8 -*-
"""Tests for OpenAI code removal (TDD verification).

These tests verify expected behavior AFTER OpenAI code removal:
1. /token endpoint should return 404 (removed)
2. /token/soniox should still work
3. TTSProviderFactory.create('openai') should raise ValueError
4. Default TTS provider should be 'google'
"""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


class TestOpenAIEndpointRemoval:
    """Verify /token endpoint is removed."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from app.main import app

        return TestClient(app)

    def test_token_endpoint_returns_404(self, client):
        """POST /api/voice/token should return 404 (endpoint removed)."""
        response = client.post("/api/voice/token")
        assert response.status_code == 404, "OpenAI /token endpoint should be removed"

    def test_soniox_endpoint_still_works(self, client):
        """POST /api/voice/token/soniox should still work."""
        with patch.dict(os.environ, {"SONIOX_API_KEY": "test_soniox_key"}):
            response = client.post("/api/voice/token/soniox")
            # Should return 200 OK, not 404
            assert response.status_code == 200
            # Should return Soniox API key
            data = response.json()
            assert "api_key" in data
            assert data["api_key"] == "test_soniox_key"


class TestOpenAITTSProviderRemoval:
    """Verify OpenAITTSProvider is removed from factory."""

    def test_openai_provider_raises_value_error(self):
        """TTSProviderFactory.create('openai') should raise ValueError."""
        from app.services.tts_providers import TTSProviderFactory

        with pytest.raises(ValueError) as exc_info:
            TTSProviderFactory.create("openai")

        error_msg = str(exc_info.value).lower()
        assert "openai" in error_msg or "unknown" in error_msg, \
            "Error should mention OpenAI provider is unknown"

    def test_default_provider_is_google(self):
        """Default TTS provider should be 'google' (not 'openai')."""
        from app.services.tts_providers import TTSProviderFactory

        # Don't set TTS_PROVIDER env var (should use default "google")
        # Mock google credentials
        with patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/fake/path.json"}):
            with patch("google.cloud.texttospeech.TextToSpeechClient"):
                # Should default to google, not openai
                provider = TTSProviderFactory.create()
                # Verify it's Google provider
                from app.services.tts_providers import GoogleCloudTTSProvider
                assert isinstance(provider, GoogleCloudTTSProvider), \
                    "Default provider should be GoogleCloudTTSProvider"

    def test_openai_not_in_legacy_list(self):
        """OpenAI should not be in legacy support list in validate_provider."""
        from app.services.tts_providers import TTSProviderFactory

        # Calling validate with 'openai' should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            TTSProviderFactory.validate_provider("openai")

        error_msg = str(exc_info.value).lower()
        assert "openai" in error_msg or "unknown" in error_msg, \
            "validate_provider should reject 'openai' as unknown"


class TestOpenAISchemasRemoval:
    """Verify OpenAI schemas are removed."""

    def test_ephemeral_token_response_removed(self):
        """EphemeralTokenResponse should not be importable."""
        with pytest.raises(ImportError):
            from app.models.voice_schemas import EphemeralTokenResponse

    def test_client_secret_removed(self):
        """ClientSecret should not be importable."""
        with pytest.raises(ImportError):
            from app.models.voice_schemas import ClientSecret

    def test_soniox_token_response_still_exists(self):
        """SonioxTokenResponse should still be importable."""
        from app.models.voice_schemas import SonioxTokenResponse

        # Should not raise ImportError
        assert SonioxTokenResponse is not None
