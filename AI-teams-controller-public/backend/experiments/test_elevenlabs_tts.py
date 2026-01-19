#!/usr/bin/env python3
"""
Demo: Mixed English-Vietnamese TTS with ElevenLabs
For comparison with Google Cloud TTS (premium quality alternative)

Requirements:
    pip install elevenlabs
    export ELEVENLABS_API_KEY=your_api_key_here

Pricing: $165-330/month for 2M chars (Scale plan)
         vs Google Cloud: $8 for 2M chars (Standard)
         = 20x-40x more expensive
"""

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import os


def test_elevenlabs_mixed_language():
    """
    Test ElevenLabs Multilingual v2 with mixed English-Vietnamese

    ElevenLabs strengths:
    - Auto-detects language seamlessly
    - Industry-leading voice quality
    - Supports 70+ languages including Vietnamese
    - Natural code-switching between languages

    Weaknesses:
    - 20-40x more expensive than Google Cloud
    - Subscription model (not pay-as-you-go)
    """

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ Error: ELEVENLABS_API_KEY not set")
        print("   export ELEVENLABS_API_KEY=your_key")
        return

    client = ElevenLabs(api_key=api_key)

    # Mixed English-Vietnamese text (same as Google Cloud test)
    mixed_text = """
    Hello, xin chào! I'm testing Vietnamese TTS.
    Tôi đang thử nghiệm text-to-speech với ElevenLabs.
    This is a realistic example with task completed.
    Đã hoàn thành API endpoint successfully.
    """

    # Use Multilingual v2 model (supports Vietnamese)
    audio = client.generate(
        text=mixed_text,
        voice="Rachel",  # Or any multilingual voice
        model="eleven_multilingual_v2",  # Supports Vietnamese
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Save audio
    output_path = "/tmp/test_elevenlabs_mixed.mp3"
    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    print(f"✅ ElevenLabs test saved to: {output_path}")
    print("\n💰 Cost comparison:")
    print("   ElevenLabs Scale plan: $330/month for 2M chars")
    print("   Google Cloud Standard: $8 for 2M chars")
    print("   Difference: 41x more expensive")
    print("\n🎧 Compare audio quality with Google Cloud output to decide if worth it")


def list_elevenlabs_voices():
    """
    List available ElevenLabs voices that support multilingual
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return

    client = ElevenLabs(api_key=api_key)

    voices = client.voices.get_all()

    print("\n📋 ElevenLabs Multilingual Voices:")
    print("-" * 60)
    for voice in voices.voices:
        # Check if voice supports multilingual
        print(f"Name: {voice.name}")
        print(f"  Voice ID: {voice.voice_id}")
        print(f"  Labels: {voice.labels}")
        print()


def compare_elevenlabs_models():
    """
    Compare Multilingual v2 (1 credit/char) vs Turbo 2.5 (0.5 credits/char)

    Multilingual v2: Higher quality, slower, 1 credit/char
    Turbo 2.5: 3x faster, 0.5 credits/char, still good quality
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return

    client = ElevenLabs(api_key=api_key)

    test_text = "Xin chào! This is a quality test. Đây là bài kiểm tra chất lượng."

    # Test Multilingual v2
    print("Generating Multilingual v2 audio...")
    audio_v2 = client.generate(
        text=test_text,
        voice="Rachel",
        model="eleven_multilingual_v2",
    )
    with open("/tmp/elevenlabs_multilingual_v2.mp3", "wb") as f:
        for chunk in audio_v2:
            f.write(chunk)
    print("✅ Multilingual v2 saved to: /tmp/elevenlabs_multilingual_v2.mp3")
    print("   Cost: 1 credit/char = ~$165/million chars (Scale plan)")

    # Test Turbo 2.5
    print("\nGenerating Turbo 2.5 audio...")
    audio_turbo = client.generate(
        text=test_text,
        voice="Rachel",
        model="eleven_turbo_v2_5",  # 3x faster, 0.5 credits
    )
    with open("/tmp/elevenlabs_turbo_v2_5.mp3", "wb") as f:
        for chunk in audio_turbo:
            f.write(chunk)
    print("✅ Turbo 2.5 saved to: /tmp/elevenlabs_turbo_v2_5.mp3")
    print("   Cost: 0.5 credits/char = ~$82.50/million chars (Scale plan)")

    print("\n🎧 Compare both ElevenLabs models with Google Cloud:")
    print("   ElevenLabs Multilingual v2: ~$165/million (highest quality)")
    print("   ElevenLabs Turbo 2.5:        ~$82.50/million (fast, good quality)")
    print("   Google Cloud WaveNet:        $16/million (very good quality)")
    print("   Google Cloud Standard:       $4/million (good quality)")


if __name__ == "__main__":
    print("🚀 Testing ElevenLabs TTS with Mixed English-Vietnamese\n")
    print("⚠️  WARNING: ElevenLabs is 20-40x more expensive than Google Cloud!")
    print("   Only use if voice quality is mission-critical.\n")

    list_elevenlabs_voices()

    print("\n" + "=" * 60)
    print("Running synthesis tests...")
    print("=" * 60 + "\n")

    test_elevenlabs_mixed_language()
    compare_elevenlabs_models()

    print("\n✨ Tests complete!")
    print("\n🤔 Decision matrix:")
    print("   Choose ElevenLabs if:")
    print("     - Voice quality is mission-critical (customer-facing)")
    print("     - Budget allows $165-330/month")
    print("     - Need industry-leading naturalness")
    print()
    print("   Choose Google Cloud if:")
    print("     - Cost efficiency matters (73% cheaper than OpenAI)")
    print("     - Good quality is sufficient")
    print("     - Want pay-as-you-go pricing")
    print("     - Already integrated in system")
