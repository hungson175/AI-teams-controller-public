"""
Audio utilities for OpenAI Realtime API.

Handles:
- Audio format conversion (PCM16 <-> float32)
- Sample rate conversion (any rate -> 24kHz)
- Base64 encoding/decoding for WebSocket transmission
"""

import base64
import numpy as np

# OpenAI Realtime API audio requirements
SAMPLE_RATE = 24000  # 24kHz
CHANNELS = 1         # Mono
DTYPE = np.int16     # PCM16


def float32_to_pcm16(audio_float32: np.ndarray) -> np.ndarray:
    """
    Convert float32 audio [-1.0, 1.0] to PCM16 int16.

    Args:
        audio_float32: NumPy array of float32 audio samples

    Returns:
        NumPy array of int16 PCM samples
    """
    # Clip to valid range and scale
    clipped = np.clip(audio_float32, -1.0, 1.0)
    return (clipped * 32767).astype(np.int16)


def pcm16_to_float32(audio_pcm16: np.ndarray) -> np.ndarray:
    """
    Convert PCM16 int16 to float32 [-1.0, 1.0].

    Args:
        audio_pcm16: NumPy array of int16 PCM samples

    Returns:
        NumPy array of float32 audio samples
    """
    return audio_pcm16.astype(np.float32) / 32768.0


def audio_to_base64(audio_pcm16: np.ndarray) -> str:
    """
    Encode PCM16 audio to base64 string for WebSocket transmission.

    Args:
        audio_pcm16: NumPy array of int16 PCM samples

    Returns:
        Base64 encoded string
    """
    return base64.b64encode(audio_pcm16.tobytes()).decode('utf-8')


def base64_to_audio(audio_base64: str) -> np.ndarray:
    """
    Decode base64 string to PCM16 audio.

    Args:
        audio_base64: Base64 encoded audio string

    Returns:
        NumPy array of int16 PCM samples
    """
    audio_bytes = base64.b64decode(audio_base64)
    return np.frombuffer(audio_bytes, dtype=np.int16)


def resample_audio(audio: np.ndarray, original_rate: int, target_rate: int = SAMPLE_RATE) -> np.ndarray:
    """
    Resample audio to target sample rate using high-quality soxr resampler.

    Args:
        audio: NumPy array of audio samples
        original_rate: Original sample rate
        target_rate: Target sample rate (default: 24000)

    Returns:
        Resampled audio as NumPy array
    """
    if original_rate == target_rate:
        return audio

    try:
        import soxr
        return soxr.resample(audio, original_rate, target_rate)
    except ImportError:
        # Fallback to simple linear interpolation (lower quality)
        ratio = target_rate / original_rate
        new_length = int(len(audio) * ratio)
        indices = np.linspace(0, len(audio) - 1, new_length)
        return np.interp(indices, np.arange(len(audio)), audio).astype(audio.dtype)


def ensure_mono(audio: np.ndarray) -> np.ndarray:
    """
    Convert stereo audio to mono by averaging channels.

    Args:
        audio: NumPy array of audio samples (1D or 2D)

    Returns:
        Mono audio as 1D NumPy array
    """
    if audio.ndim == 1:
        return audio
    elif audio.ndim == 2:
        return np.mean(audio, axis=1).astype(audio.dtype)
    else:
        raise ValueError(f"Unexpected audio shape: {audio.shape}")
