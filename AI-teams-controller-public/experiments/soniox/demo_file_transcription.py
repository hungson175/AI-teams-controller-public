"""
Soniox Demo: Transcribe Audio File (Short < 60 seconds)

Usage:
    export SONIOX_API_KEY=your_api_key
    python demo_file_transcription.py path/to/audio.mp3

Supports: MP3, WAV, FLAC, and other common formats
"""

import os
import sys
from soniox.speech_service import SpeechClient
from soniox.transcribe_file import transcribe_file_short


def transcribe_short_file(audio_path: str, model: str = "soniox_enhanced") -> str:
    """
    Transcribe a short audio file (< 60 seconds).

    Args:
        audio_path: Path to audio file
        model: Model to use. Options:
               - "soniox_enhanced" (default, best accuracy)
               - "en_v2" (English optimized)
               - "vi" (Vietnamese)

    Returns:
        Transcribed text
    """
    if not os.environ.get("SONIOX_API_KEY"):
        raise ValueError("SONIOX_API_KEY environment variable not set")

    with SpeechClient() as client:
        result = transcribe_file_short(
            audio_path,
            client,
            model=model,
        )

        # Extract text from words
        text = "".join(word.text for word in result.words)

        return text, result.words


def main():
    if len(sys.argv) < 2:
        print("Usage: python demo_file_transcription.py <audio_file>")
        print("Example: python demo_file_transcription.py audio.mp3")
        sys.exit(1)

    audio_path = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "soniox_enhanced"

    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}")
        sys.exit(1)

    print(f"Transcribing: {audio_path}")
    print(f"Model: {model}")
    print("-" * 50)

    text, words = transcribe_short_file(audio_path, model)

    print("\n=== TRANSCRIPTION ===")
    print(text)

    print("\n=== WORD TIMESTAMPS ===")
    for word in words[:20]:  # Show first 20 words
        print(f"  '{word.text}' @ {word.start_ms}ms (duration: {word.duration_ms}ms)")

    if len(words) > 20:
        print(f"  ... and {len(words) - 20} more words")


if __name__ == "__main__":
    main()
