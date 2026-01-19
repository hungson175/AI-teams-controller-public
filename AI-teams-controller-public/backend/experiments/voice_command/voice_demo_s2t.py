#!/usr/bin/env python3
"""
Voice Demo: Speech-to-Text with Stop Word Detection

This demo captures audio from the microphone, transcribes it using OpenAI Whisper,
and detects the stop word "SEND PLS" to trigger command extraction.

Requirements:
    uv sync

Usage:
    uv run python voice_demo_s2t.py

Press Ctrl+C to stop recording early.
"""

import os
import sys
import tempfile
import threading
from pathlib import Path

from dotenv import load_dotenv
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from openai import OpenAI

# Load environment variables from .env
load_dotenv()


# Configuration
# Multiple variations of stop word that Whisper might transcribe
STOP_WORDS = [
    "send please",
    "send pls",
    "send, please",
    "send it please",
    "sent please",
    "send please.",
    "send pls.",
]
SAMPLE_RATE = 16000  # 16kHz for Whisper
CHANNELS = 1
MAX_DURATION = 30  # Maximum recording duration in seconds


def record_audio(duration: int = MAX_DURATION) -> np.ndarray:
    """Record audio from microphone until stop or max duration."""
    print(f"\n🎤 Recording... (max {duration}s, press Ctrl+C to stop)")
    print(f"   Say 'send please' or 'send pls' to trigger command send\n")

    recording = []
    stop_event = threading.Event()

    def callback(indata, frames, time, status):
        if status:
            print(f"⚠️  {status}")
        recording.append(indata.copy())

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=np.float32,
            callback=callback,
        ):
            sd.sleep(duration * 1000)
    except KeyboardInterrupt:
        print("\n⏹️  Recording stopped by user")

    if not recording:
        return np.array([])

    return np.concatenate(recording, axis=0)


def save_audio(audio: np.ndarray, filepath: str) -> None:
    """Save audio array to WAV file."""
    # Convert float32 to int16
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(filepath, SAMPLE_RATE, audio_int16)


def transcribe_audio(filepath: str) -> str:
    """Transcribe audio file using OpenAI Whisper API."""
    client = OpenAI()

    print("🔄 Transcribing with Whisper...")

    with open(filepath, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en",
        )

    return transcription.text


def detect_stop_word(text: str) -> tuple[bool, str, str]:
    """
    Check for stop word and extract command.

    Returns:
        (triggered, command, matched_word) - triggered is True if stop word found
    """
    text_lower = text.lower()

    for stop_word in STOP_WORDS:
        if stop_word in text_lower:
            # Find the stop word and extract everything before it
            idx = text_lower.find(stop_word)
            command = text[:idx].strip()

            # Clean up common filler words at the end
            for filler in [",", ".", "and", "so", "then"]:
                if command.lower().endswith(filler):
                    command = command[: -len(filler)].strip()

            return True, command, stop_word

    return False, text, ""


def main():
    """Main demo function."""
    print("=" * 60)
    print("🎙️  Voice Demo: Speech-to-Text with Stop Word Detection")
    print("=" * 60)

    # Check API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Export your key: export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    print(f"\nStop words: {STOP_WORDS}")
    print("Example: 'Update the documentation for the API, send please'")

    # Record audio
    audio = record_audio()

    if len(audio) == 0:
        print("❌ No audio recorded")
        return

    print(f"✅ Recorded {len(audio) / SAMPLE_RATE:.1f} seconds of audio")

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
        save_audio(audio, temp_path)
        print(f"💾 Saved to: {temp_path}")

    try:
        # Transcribe
        text = transcribe_audio(temp_path)
        print(f"\n📝 Transcription:\n   '{text}'")

        # Detect stop word
        triggered, command, matched = detect_stop_word(text)

        print("\n" + "-" * 40)
        if triggered:
            print(f"✅ Stop word detected: '{matched}'")
            print(f"📤 Command to send:\n   '{command}'")
        else:
            print(f"⏳ No stop word detected")
            print(f"   Expected one of: {STOP_WORDS}")
            print(f"   Full text: '{text}'")
        print("-" * 40)

    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
