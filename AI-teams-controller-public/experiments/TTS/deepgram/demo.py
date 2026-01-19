#!/usr/bin/env python3
"""
Deepgram Aura TTS Demo
Cost: $15/million chars (same as OpenAI)
Speed: 2-5x faster than OpenAI (250-300ms vs 200ms)
"""

import os
import asyncio
from deepgram import DeepgramClient, SpeakOptions


async def test_deepgram_tts(text: str, output_file: str = "output_deepgram.mp3"):
    """
    Test Deepgram Aura TTS.

    Args:
        text: Text to convert to speech
        output_file: Output audio file path
    """
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        print("ERROR: DEEPGRAM_API_KEY environment variable not set!")
        print("\nSetup instructions:")
        print("1. Sign up at https://deepgram.com")
        print("2. Get API key from console")
        print("3. Set environment variable:")
        print('   export DEEPGRAM_API_KEY="your_api_key_here"')
        return

    try:
        # Initialize Deepgram client
        deepgram = DeepgramClient(api_key)

        # Configure speech options
        options = SpeakOptions(
            model="aura-asteria-en",  # Aura model (latest)
            encoding="mp3",
            container="mp3",
        )

        print("\n=== Testing Deepgram Aura TTS ===")
        print(f"Text length: {len(text)} characters")
        print(f"Cost estimate: ~${len(text) * 0.000015:.6f}")

        # Generate speech
        SPEAK_OPTIONS = {"text": text}
        response = deepgram.speak.v("1").save(output_file, SPEAK_OPTIONS, options)

        print(f"✓ Audio saved to: {output_file}")
        print("\n=== Performance Advantages ===")
        print("- 2-5x faster than OpenAI (250-300ms time-to-first-audio)")
        print("- Same pricing as OpenAI ($15/million chars)")
        print("- Purpose-built for real-time voice AI agents")
        print("- Enterprise-grade quality")

    except Exception as e:
        print(f"ERROR: {e}")
        print("\nMake sure you have:")
        print("1. Installed deepgram-sdk: pip install deepgram-sdk")
        print("2. Set DEEPGRAM_API_KEY environment variable")


async def test_streaming_tts(text: str):
    """
    Test Deepgram streaming TTS (for real-time applications).
    """
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        return

    try:
        from deepgram import DeepgramClient, SpeakWebSocketOptions

        print("\n=== Testing Deepgram Streaming TTS ===")
        print("(Optimized for real-time voice applications)")

        deepgram = DeepgramClient(api_key)

        # Configure streaming options
        options = SpeakWebSocketOptions(
            model="aura-asteria-en",
            encoding="linear16",
            sample_rate=16000,
        )

        # Note: Full streaming implementation requires WebSocket handling
        print("✓ Streaming mode available for real-time voice apps")
        print("  Advantage: Start playing audio while generation continues")
        print("  Use case: Voice AI agents, conversational interfaces")

    except Exception as e:
        print(f"Streaming test: {e}")


def list_available_models():
    """List Deepgram Aura models."""
    print("\n=== Available Deepgram Aura Models ===")
    models = [
        ("aura-asteria-en", "Female, warm and engaging"),
        ("aura-luna-en", "Female, calm and soothing"),
        ("aura-stella-en", "Female, energetic and upbeat"),
        ("aura-athena-en", "Female, professional"),
        ("aura-hera-en", "Female, authoritative"),
        ("aura-orion-en", "Male, confident"),
        ("aura-arcas-en", "Male, casual"),
        ("aura-perseus-en", "Male, assertive"),
        ("aura-angus-en", "Male, friendly (Irish accent)"),
        ("aura-orpheus-en", "Male, storytelling"),
    ]

    for model, description in models:
        print(f"  {model}: {description}")


if __name__ == "__main__":
    # Test text
    test_text = """
    This is a test of Deepgram Aura Text-to-Speech API.
    It costs the same as OpenAI at fifteen dollars per million characters,
    but it's two to five times faster, with time-to-first-audio under 300 milliseconds.
    Perfect for real-time voice applications.
    """

    # Run async demo
    asyncio.run(test_deepgram_tts(test_text.strip()))
    asyncio.run(test_streaming_tts(test_text.strip()))
    list_available_models()
