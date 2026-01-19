#!/usr/bin/env python3
"""
Compare Google Cloud TTS vs OpenAI TTS

Side-by-side comparison of latency, quality, and cost.

Requirements:
    - GOOGLE_APPLICATION_CREDENTIALS set
    - OPENAI_API_KEY set

Usage:
    python compare_openai.py
    python compare_openai.py --text "Custom text"
"""

import argparse
import os
import time
from pathlib import Path

try:
    from google.cloud import texttospeech
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠ google-cloud-texttospeech not installed")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠ openai not installed (pip install openai)")


def generate_google_tts(text: str, voice_type: str, output_path: str) -> dict:
    """Generate speech with Google Cloud TTS."""
    client = texttospeech.TextToSpeechClient()

    voice_map = {
        "standard": "en-US-Standard-A",
        "neural2": "en-US-Neural2-A",
    }

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_map[voice_type]
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
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

    return {
        "latency_ms": latency_ms,
        "size_bytes": len(response.audio_content),
        "file": output_path
    }


def generate_openai_tts(text: str, output_path: str) -> dict:
    """Generate speech with OpenAI TTS."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    start_time = time.time()
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    latency_ms = (time.time() - start_time) * 1000

    response.stream_to_file(output_path)

    size_bytes = os.path.getsize(output_path)

    return {
        "latency_ms": latency_ms,
        "size_bytes": size_bytes,
        "file": output_path
    }


def compare_tts(text: str, output_dir: Path):
    """Run comparison between Google and OpenAI TTS."""
    output_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("Google Cloud TTS vs OpenAI TTS Comparison")
    print("=" * 70)
    print(f"Text: {text}")
    print(f"Character count: {len(text)}")
    print()

    results = {}

    # Test Google Cloud Standard
    if GOOGLE_AVAILABLE:
        try:
            print("Testing Google Cloud Standard...")
            results["google_standard"] = generate_google_tts(
                text=text,
                voice_type="standard",
                output_path=str(output_dir / "google_standard.mp3")
            )
            print(f"✓ Latency: {results['google_standard']['latency_ms']:.0f}ms")
            print()
        except Exception as e:
            print(f"✗ Error: {e}\n")

    # Test Google Cloud Neural2
    if GOOGLE_AVAILABLE:
        try:
            print("Testing Google Cloud Neural2...")
            results["google_neural2"] = generate_google_tts(
                text=text,
                voice_type="neural2",
                output_path=str(output_dir / "google_neural2.mp3")
            )
            print(f"✓ Latency: {results['google_neural2']['latency_ms']:.0f}ms")
            print()
        except Exception as e:
            print(f"✗ Error: {e}\n")

    # Test OpenAI
    if OPENAI_AVAILABLE:
        try:
            print("Testing OpenAI TTS...")
            results["openai"] = generate_openai_tts(
                text=text,
                output_path=str(output_dir / "openai.mp3")
            )
            print(f"✓ Latency: {results['openai']['latency_ms']:.0f}ms")
            print()
        except Exception as e:
            print(f"✗ Error: {e}\n")

    # Summary
    if results:
        print("=" * 70)
        print("Summary")
        print("=" * 70)

        # Calculate costs
        char_count = len(text)
        costs = {
            "google_standard": (char_count / 1_000_000) * 4.0,
            "google_neural2": (char_count / 1_000_000) * 16.0,
            "openai": (char_count / 1_000_000) * 15.0,
        }

        # Print comparison table
        print(f"{'Provider':<20} {'Latency':<15} {'Size':<15} {'Cost':<15}")
        print("-" * 70)

        for provider, data in results.items():
            latency = f"{data['latency_ms']:.0f}ms"
            size = f"{data['size_bytes'] / 1024:.1f}KB"
            cost = f"${costs[provider]:.6f}"
            print(f"{provider:<20} {latency:<15} {size:<15} {cost:<15}")

        print()

        # Cost comparison
        if "openai" in results and "google_standard" in results:
            openai_cost = costs["openai"]
            google_cost = costs["google_standard"]
            savings = ((openai_cost - google_cost) / openai_cost) * 100
            print(f"Google Standard saves {savings:.0f}% vs OpenAI")

        if "openai" in results and "google_neural2" in results:
            openai_cost = costs["openai"]
            google_cost = costs["google_neural2"]
            diff = ((google_cost - openai_cost) / openai_cost) * 100
            print(f"Google Neural2 costs {diff:+.0f}% vs OpenAI")

        print()
        print(f"Cost for 1M characters:")
        print(f"  Google Standard: $4.00 (73% cheaper)")
        print(f"  Google Neural2:  $16.00 (7% more expensive)")
        print(f"  OpenAI:          $15.00 (baseline)")

        print()
        print(f"Audio files saved to: {output_dir.absolute()}")


def main():
    parser = argparse.ArgumentParser(description="Compare Google TTS vs OpenAI TTS")

    parser.add_argument(
        "--text",
        default="This is a comparison test between Google Cloud Text to Speech "
                "and OpenAI Text to Speech. We're measuring latency and quality.",
        help="Text to synthesize"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./comparison"),
        help="Output directory"
    )

    args = parser.parse_args()

    # Check credentials
    if not GOOGLE_AVAILABLE:
        print("Install Google Cloud TTS: pip install google-cloud-texttospeech")
        return

    if not OPENAI_AVAILABLE:
        print("Install OpenAI: pip install openai")
        return

    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("⚠ GOOGLE_APPLICATION_CREDENTIALS not set")

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠ OPENAI_API_KEY not set")

    compare_tts(text=args.text, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
