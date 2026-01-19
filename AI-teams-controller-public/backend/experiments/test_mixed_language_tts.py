#!/usr/bin/env python3
"""
Demo: Mixed English-Vietnamese TTS with Google Cloud
Demonstrates auto-detection and SSML language tags for code-switching

Requirements:
    pip install google-cloud-texttospeech
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
"""

from google.cloud import texttospeech
import os


def test_auto_detection():
    """
    Test 1: Auto language detection
    Google Cloud TTS will automatically detect and handle the predominant language.
    """
    client = texttospeech.TextToSpeechClient()

    # Mixed English-Vietnamese text (auto-detection)
    mixed_text = "Hello, xin chào! I'm testing Vietnamese TTS. Tôi đang thử nghiệm text-to-speech."

    # Configure synthesis
    synthesis_input = texttospeech.SynthesisInput(text=mixed_text)

    # Use Vietnamese voice - it will handle English portions too
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",
        name="vi-VN-Wavenet-A",  # WaveNet voice (higher quality)
        # Alternative: "vi-VN-Standard-A" (cheaper, $4/million chars)
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
        pitch=0.0,
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Save audio
    output_path = "/tmp/test_auto_detect.mp3"
    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    print(f"✅ Auto-detection test saved to: {output_path}")
    return output_path


def test_ssml_explicit_tags():
    """
    Test 2: Explicit language tags with SSML
    Use <lang> tags to explicitly control language switching for better pronunciation.
    """
    client = texttospeech.TextToSpeechClient()

    # SSML with explicit language tags
    ssml_text = """
    <speak>
        <lang xml:lang="en-US">Hello, this is English.</lang>
        <lang xml:lang="vi-VN">Xin chào, đây là tiếng Việt.</lang>
        <lang xml:lang="en-US">Back to English.</lang>
        <lang xml:lang="vi-VN">Và lại tiếng Việt.</lang>
    </speak>
    """

    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

    # Use a multilingual voice that supports both languages
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",  # Base language
        name="vi-VN-Wavenet-A",
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    output_path = "/tmp/test_ssml_tags.mp3"
    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    print(f"✅ SSML explicit tags test saved to: {output_path}")
    return output_path


def test_realistic_scenario():
    """
    Test 3: Realistic mixed-language scenario
    Simulates actual voice feedback with technical terms in English and Vietnamese.
    """
    client = texttospeech.TextToSpeechClient()

    # Realistic mixed content (like your voice feedback summaries)
    realistic_text = """
    Task completed successfully.
    Đã hoàn thành task về API endpoint.
    The /api/teams endpoint is now working properly.
    Kết quả test: all tests passed.
    """

    synthesis_input = texttospeech.SynthesisInput(text=realistic_text)

    # Use Standard voice for cost efficiency ($4/million vs $16/million)
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",
        name="vi-VN-Standard-A",  # Cheaper option
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    output_path = "/tmp/test_realistic_mixed.mp3"
    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    print(f"✅ Realistic scenario test saved to: {output_path}")
    return output_path


def list_available_vietnamese_voices():
    """
    Utility: List all available Vietnamese voices
    """
    client = texttospeech.TextToSpeechClient()

    response = client.list_voices(language_code="vi-VN")

    print("\n📋 Available Vietnamese voices:")
    print("-" * 60)
    for voice in response.voices:
        print(f"Name: {voice.name}")
        print(f"  Language: {', '.join(voice.language_codes)}")
        print(f"  Gender: {texttospeech.SsmlVoiceGender(voice.ssml_gender).name}")
        print(f"  Sample rate: {voice.natural_sample_rate_hertz} Hz")
        print()


def compare_standard_vs_wavenet():
    """
    Test 4: Quality comparison - Standard vs WaveNet
    Generates same text with both voice types for A/B testing.
    """
    client = texttospeech.TextToSpeechClient()

    test_text = "Xin chào! This is a test of voice quality. Đây là bài kiểm tra chất lượng giọng nói."

    synthesis_input = texttospeech.SynthesisInput(text=test_text)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Test Standard voice ($4/million)
    standard_voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN", name="vi-VN-Standard-A"
    )
    standard_response = client.synthesize_speech(
        input=synthesis_input, voice=standard_voice, audio_config=audio_config
    )
    with open("/tmp/test_standard_quality.mp3", "wb") as out:
        out.write(standard_response.audio_content)
    print("✅ Standard voice saved to: /tmp/test_standard_quality.mp3")

    # Test WaveNet voice ($16/million)
    wavenet_voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN", name="vi-VN-Wavenet-A"
    )
    wavenet_response = client.synthesize_speech(
        input=synthesis_input, voice=wavenet_voice, audio_config=audio_config
    )
    with open("/tmp/test_wavenet_quality.mp3", "wb") as out:
        out.write(wavenet_response.audio_content)
    print("✅ WaveNet voice saved to: /tmp/test_wavenet_quality.mp3")

    print("\n🎧 Listen to both files and compare quality vs cost:")
    print("   Standard: $4/million chars")
    print("   WaveNet:  $16/million chars")


if __name__ == "__main__":
    # Check credentials
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("❌ Error: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        exit(1)

    print("🚀 Testing Google Cloud TTS with Mixed English-Vietnamese\n")

    # Run all tests
    list_available_vietnamese_voices()

    print("\n" + "=" * 60)
    print("Running synthesis tests...")
    print("=" * 60 + "\n")

    test_auto_detection()
    test_ssml_explicit_tags()
    test_realistic_scenario()
    compare_standard_vs_wavenet()

    print("\n✨ All tests complete!")
    print("\n💡 Recommendations:")
    print("   1. Start with Standard voices ($4/million) for testing")
    print("   2. Use auto-detection for simple mixed text")
    print("   3. Use SSML <lang> tags for precise control")
    print("   4. Upgrade to WaveNet ($16/million) if quality feedback requires it")
    print("   5. Still 73% cheaper than OpenAI TTS ($15/million)!")
