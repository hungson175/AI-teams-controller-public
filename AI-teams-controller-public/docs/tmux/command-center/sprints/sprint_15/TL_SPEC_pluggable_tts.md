# Technical Spec: Pluggable TTS Architecture - HD-TTS Provider

## Overview

Add HD-TTS as third TTS provider using SOLID principles. Refactor factory to support plugin registration without code modification.

## Architecture Changes

### 1. Provider Registry Pattern (Open-Closed Principle)

Replace hardcoded if/elif in factory with dynamic registry:

```python
# Providers self-register via decorator
@TTSProviderFactory.register("hdtts")
class HDTTSProvider(TTSProvider):
    ...
```

### 2. HD-TTS Provider Implementation

**File:** `backend/app/services/tts_providers.py`

**Config (env vars):**
- `HDTTS_API_URL` - Base URL (default: `https://hd-tts-backend.hungson175.com`)
- `HDTTS_API_KEY` - API key for authentication

**HD-TTS specific params (optional, with defaults):**
- gender: female, area: northern, quality: high

**Audio Format:** HD-TTS returns WAV. Provider MUST convert WAV→MP3 using pydub/ffmpeg to maintain consistent MP3 output across all providers.

### 3. Factory Refactor

```python
class TTSProviderFactory:
    _registry: dict[str, type[TTSProvider]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(provider_class):
            cls._registry[name] = provider_class
            return provider_class
        return decorator

    @classmethod
    def create(cls, provider_name: str = None) -> TTSProvider:
        name = (provider_name or os.getenv("TTS_PROVIDER", "openai")).lower()
        if name not in cls._registry:
            raise ValueError(f"Unknown provider: {name}. Available: {list(cls._registry.keys())}")
        return cls._registry[name]()
```

## Files to Modify

| File | Changes |
|------|---------|
| `backend/app/services/tts_providers.py` | Add registry, HDTTSProvider class, refactor factory |
| `backend/.env.example` | Add HDTTS_API_URL, HDTTS_API_KEY |

## Test Cases (TDD)

### Unit Tests (`test_tts_providers.py`)

1. **Registry tests:**
   - `test_register_provider` - decorator adds to registry
   - `test_create_registered_provider` - factory creates registered provider
   - `test_create_unknown_provider_raises` - ValueError for unknown

2. **HDTTSProvider tests:**
   - `test_hdtts_generate_speech` - calls API, returns MP3 bytes
   - `test_hdtts_auth_header` - X-API-Key header sent
   - `test_hdtts_default_params` - female, northern, high quality
   - `test_hdtts_missing_api_key_raises` - ValueError if no key
   - `test_hdtts_wav_to_mp3_conversion` - output is valid MP3 format

3. **Integration tests:**
   - `test_factory_creates_all_providers` - openai, google, hdtts all work
   - `test_provider_interface_compliance` - all implement abstract methods

## Code Coverage Requirements

**Backend:** 80% minimum coverage required
- Business logic (provider registry): 90%
- API integration (HDTTSProvider): 85%
- Factory pattern: 90%

## Work Items (Progressive)

| # | Work Item | Size | Description |
|---|-----------|------|-------------|
| 1 | Registry pattern refactor | S | Add _registry dict, register decorator, refactor create() |
| 2 | Migrate existing providers | XS | Add @register decorators to OpenAI and Google providers |
| 3 | HDTTSProvider implementation | M | New provider class with HTTP client, auth, params |
| 4 | Tests for all changes | M | TDD: registry tests, provider tests, integration tests |

## Acceptance Criteria (for QA)

1. `TTS_PROVIDER=hdtts` creates HDTTSProvider
2. HDTTSProvider.generate_speech() returns MP3 audio bytes (not WAV)
3. `TTS_PROVIDER=openai` still works (no regression)
4. `TTS_PROVIDER=google` still works (no regression)
5. Unknown provider raises clear ValueError with available providers list
6. All tests pass with 80%+ coverage

## Design Decisions

1. **Registry over if/elif** - Adding new provider = add class with decorator, no factory edits
2. **WAV→MP3 conversion required** - HD-TTS returns WAV; convert to MP3 for consistent output format across all providers (Boss requirement)
3. **Lazy imports** - Import HTTP client inside methods (consistent with existing pattern)
4. **Env var config** - Consistent with existing OpenAI/Google providers
