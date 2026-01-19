#!/usr/bin/env python3
"""
Google Cloud TTS Demo

Demonstrates different voice types (Standard, WaveNet, Neural2) with
latency measurements and cost comparisons.

Usage:
    python demo.py
    python demo.py --text "Custom text" --language en-US
    python demo.py --voices standard neural2
"""

import argparse
import os
import time
from pathlib import Path

from google.cloud import texttospeech


def generate_speech(
    text: str,
    language_code: str,
    voice_name: str,
    output_path: str
) -> float:
    """
    Generate speech using Google Cloud TTS.

    Args:
        text: Text to synthesize
        language_code: Language code (e.g., "en-US", "vi-VN")
        voice_name: Voice name (e.g., "en-US-Standard-A")
        output_path: Path to save MP3 file

    Returns:
        Latency in milliseconds
    """
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
        pitch=0.0
    )

    start_time = time.time()
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    latency_ms = (time.time() - start_time) * 1000

    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    file_size_kb = len(response.audio_content) / 1024

    print(f"✓ Generated: {output_path}")
    print(f"  Voice: {voice_name}")
    print(f"  Latency: {latency_ms:.0f}ms")
    print(f"  Size: {file_size_kb:.1f}KB")
    print()

    return latency_ms


def estimate_cost(text: str, voice_type: str) -> float:
    """
    Estimate cost for generating TTS.

    Args:
        text: Input text
        voice_type: "standard", "neural2", or "wavenet"

    Returns:
        Cost in USD
    """
    char_count = len(text)

    price_per_million = {
        "standard": 4.0,
        "wavenet": 16.0,
        "neural2": 16.0,
    }

    price = price_per_million.get(voice_type.lower(), 16.0)
    cost = (char_count / 1_000_000) * price

    return cost


def run_demo(
    text: str,
    language_code: str,
    voice_types: list[str],
    output_dir: Path
):
    """
    Run TTS demo for specified voice types.

    Args:
        text: Text to synthesize
        language_code: Language code (e.g., "en-US")
        voice_types: List of voice types to test
        output_dir: Output directory for audio files
    """
    output_dir.mkdir(exist_ok=True)

    # Map voice types to actual voice names
    voice_map = {
        "standard": f"{language_code}-Standard-A",
        "wavenet": f"{language_code}-Wavenet-A",
        "neural2": f"{language_code}-Neural2-A",
    }

    print("=" * 70)
    print("Google Cloud TTS Demo")
    print("=" * 70)
    print(f"Text: {text}")
    print(f"Language: {language_code}")
    print(f"Character count: {len(text)}")
    print()

    results = {}

    for voice_type in voice_types:
        voice_name = voice_map.get(voice_type.lower())
        if not voice_name:
            print(f"⚠ Unknown voice type: {voice_type}")
            continue

        output_path = output_dir / f"{voice_type.lower()}_{language_code}.mp3"

        try:
            latency = generate_speech(
                text=text,
                language_code=language_code,
                voice_name=voice_name,
                output_path=str(output_path)
            )

            cost = estimate_cost(text, voice_type)
            results[voice_type] = {"latency": latency, "cost": cost}

        except Exception as e:
            print(f"✗ Error with {voice_type}: {e}")
            print()

    # Summary
    if results:
        print("=" * 70)
        print("Summary")
        print("=" * 70)

        for voice_type, data in results.items():
            print(f"{voice_type.upper()}")
            print(f"  Latency: {data['latency']:.0f}ms")
            print(f"  Cost: ${data['cost']:.6f} (for this text)")
            print(f"  Cost/1M chars: ${estimate_cost('x' * 1_000_000, voice_type):.2f}")
            print()

        # Comparison to OpenAI
        print("COMPARISON TO OPENAI TTS ($15/1M chars):")
        for voice_type, data in results.items():
            openai_cost = (len(text) / 1_000_000) * 15.0
            savings = ((openai_cost - data['cost']) / openai_cost) * 100
            print(f"  {voice_type.upper()}: {savings:+.0f}% vs OpenAI")
        print()

        print(f"Audio files saved to: {output_dir.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="Google Cloud TTS Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo.py
  python demo.py --text "Hello world" --language en-US
  python demo.py --voices standard neural2
  python demo.py --text "Xin chào" --language vi-VN
        """
    )

    parser.add_argument(
        "--text",
        default="Hello! This is a test of Google Cloud Text to Speech. "
                "We're comparing Standard, WaveNet, and Neural2 voices.",
        help="Text to synthesize"
    )

    parser.add_argument(
        "--language",
        default="en-US",
        help="Language code (e.g., en-US, vi-VN)"
    )

    parser.add_argument(
        "--voices",
        nargs="+",
        default=["standard", "wavenet", "neural2"],
        choices=["standard", "wavenet", "neural2"],
        help="Voice types to test"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./output"),
        help="Output directory for audio files"
    )

    args = parser.parse_args()

    # Check credentials
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("⚠ Warning: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Set it to your service account JSON key file:")
        print("   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        print()
        print("   Or use: gcloud auth application-default login")
        print()

    run_demo(
        text=args.text,
        language_code=args.language,
        voice_types=args.voices,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
