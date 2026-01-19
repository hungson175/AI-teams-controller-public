#!/usr/bin/env python3
"""
Google Cloud Text-to-Speech Demo
Cost: $4/million chars (73% cheaper than OpenAI)
Free tier: 4M chars/month for Standard voices
"""

import os
from google.cloud import texttospeech


def test_google_tts(text: str, output_file: str = "output_google.mp3"):
    """
    Test Google Cloud TTS with Standard and Neural2 voices.

    Args:
        text: Text to convert to speech
        output_file: Output audio file path
    """
    # Initialize client
    client = texttospeech.TextToSpeechClient()

    # Set the text input
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Test 1: Standard voice (cheapest - $4/million)
    print("\n=== Testing Google Standard Voice ($4/million) ===")
    voice_standard = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Standard-C",  # Female voice
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,  # Normal speed
        pitch=0.0,  # Normal pitch
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice_standard,
        audio_config=audio_config
    )

    standard_file = output_file.replace(".mp3", "_standard.mp3")
    with open(standard_file, "wb") as out:
        out.write(response.audio_content)
    print(f"✓ Standard voice audio saved to: {standard_file}")
    print(f"  Cost estimate: ~${len(text) * 0.000004:.6f}")

    # Test 2: Neural2 voice (premium - $16/million)
    print("\n=== Testing Google Neural2 Voice ($16/million) ===")
    voice_neural = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-C",  # Female voice
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice_neural,
        audio_config=audio_config
    )

    neural_file = output_file.replace(".mp3", "_neural2.mp3")
    with open(neural_file, "wb") as out:
        out.write(response.audio_content)
    print(f"✓ Neural2 voice audio saved to: {neural_file}")
    print(f"  Cost estimate: ~${len(text) * 0.000016:.6f}")

    # Test 3: Vietnamese voice (if you need it)
    print("\n=== Testing Vietnamese Voice ===")
    synthesis_input_vi = texttospeech.SynthesisInput(
        text="Xin chào, đây là bài kiểm tra giọng nói tiếng Việt."
    )
    voice_vi = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",
        name="vi-VN-Standard-A",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    response = client.synthesize_speech(
        input=synthesis_input_vi,
        voice=voice_vi,
        audio_config=audio_config
    )

    vi_file = output_file.replace(".mp3", "_vietnamese.mp3")
    with open(vi_file, "wb") as out:
        out.write(response.audio_content)
    print(f"✓ Vietnamese voice audio saved to: {vi_file}")

    print("\n=== Summary ===")
    print(f"Standard voice: 73% cheaper than OpenAI")
    print(f"Neural2 voice: Same quality as OpenAI, 7% more expensive")
    print(f"Free tier: 4M chars/month (Standard), 1M chars/month (Neural2)")


def list_available_voices():
    """List all available Google Cloud TTS voices."""
    client = texttospeech.TextToSpeechClient()
    voices = client.list_voices()

    print("\n=== Available English Voices ===")
    for voice in voices.voices:
        if voice.language_codes[0].startswith("en-"):
            name = voice.name
            gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
            print(f"{name} ({gender}) - {', '.join(voice.language_codes)}")


if __name__ == "__main__":
    # Check for credentials
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        print("ERROR: GOOGLE_APPLICATION_CREDENTIALS environment variable not set!")
        print("\nSetup instructions:")
        print("1. Create a Google Cloud project: https://console.cloud.google.com")
        print("2. Enable Text-to-Speech API")
        print("3. Create service account and download JSON key")
        print("4. Set environment variable:")
        print('   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"')
        exit(1)

    # Test text
    test_text = """
    This is a test of Google Cloud Text-to-Speech API.
    It's significantly cheaper than OpenAI TTS,
    with standard voices costing only four dollars per million characters,
    compared to fifteen dollars for OpenAI.
    """

    try:
        test_google_tts(test_text.strip())
        # Uncomment to see all available voices
        # list_available_voices()
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nMake sure you have:")
        print("1. Installed google-cloud-texttospeech: pip install google-cloud-texttospeech")
        print("2. Set up authentication (see instructions above)")
