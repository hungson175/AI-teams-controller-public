#!/usr/bin/env python3
"""
Demo: Google Cloud TTS with Mixed English-Vietnamese Sentences
For Boss to manually test voice quality on realistic bilingual content.

Run:
    cd backend
    uv run python experiments/test_google_mixed_language.py

Output:
    /tmp/mixed_lang_1.mp3 - Technical discussion sentence
    /tmp/mixed_lang_2.mp3 - Task completion sentence
    /tmp/mixed_lang_3.mp3 - Code review sentence

Requirements:
    - Google Cloud credentials: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
    - google-cloud-texttospeech package (already in project)
"""

import os
import sys

def main():
    # Check credentials first
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("❌ Error: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json")
        sys.exit(1)

    # Import after credential check
    from google.cloud import texttospeech

    # Initialize client
    client = texttospeech.TextToSpeechClient()

    # Three realistic mixed EN/VI sentences (like actual dev conversations)
    test_sentences = [
        {
            "id": 1,
            "text": "Không biết component này có work on front-end và back-end cùng một lúc không nhỉ?",
            "description": "Technical discussion about component behavior"
        },
        {
            "id": 2,
            "text": "Task completed successfully. Đã fix xong bug trong API endpoint. All tests passed.",
            "description": "Task completion feedback (typical voice feedback)"
        },
        {
            "id": 3,
            "text": "Code review xong rồi. Cần refactor lại function handleSubmit vì có memory leak issue.",
            "description": "Code review comment"
        },
    ]

    # Audio config
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
    )

    # Use Vietnamese Standard voice (cost: $4/million chars)
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",
        name="vi-VN-Standard-A",
    )

    print("🚀 Google Cloud TTS - Mixed English/Vietnamese Demo")
    print("=" * 60)
    print()

    output_files = []

    for sentence in test_sentences:
        print(f"📝 Sentence {sentence['id']}: {sentence['description']}")
        print(f"   Text: \"{sentence['text']}\"")

        # Generate speech
        synthesis_input = texttospeech.SynthesisInput(text=sentence["text"])
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # Save to file
        output_path = f"/tmp/mixed_lang_{sentence['id']}.mp3"
        with open(output_path, "wb") as f:
            f.write(response.audio_content)

        output_files.append(output_path)
        print(f"   ✅ Saved: {output_path}")
        print()

    print("=" * 60)
    print("✨ Demo complete! Output files:")
    print()
    for f in output_files:
        print(f"   🎧 {f}")
    print()
    print("💡 To play on Linux:")
    print("   mpv /tmp/mixed_lang_1.mp3")
    print("   mpv /tmp/mixed_lang_2.mp3")
    print("   mpv /tmp/mixed_lang_3.mp3")
    print()
    print("💡 Or play all:")
    print("   for f in /tmp/mixed_lang_*.mp3; do mpv \"$f\"; done")


if __name__ == "__main__":
    main()
