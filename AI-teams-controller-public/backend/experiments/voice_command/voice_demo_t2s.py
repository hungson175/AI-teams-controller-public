#!/usr/bin/env python3
"""
Voice Demo: Text-to-Speech for Summaries

This demo takes text (like agent output), optionally summarizes it with GPT,
and converts it to speech using OpenAI TTS API.

Requirements:
    uv sync

Usage:
    uv run python voice_demo_t2s.py

Options:
    --text "Your text here"     Text to speak
    --summarize                 Summarize the text first with GPT
    --voice alloy               Voice: alloy, echo, fable, onyx, nova, shimmer
    --output speech.mp3         Output file path
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()


# Available voices
VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# Sample agent output for demo
SAMPLE_OUTPUT = """
PM [20:45]: WHITEBOARD updated with WebSocket streaming implementation.

Changes completed:
1. Added WebSocket endpoint to FastAPI backend (routes.py)
2. Created polling interval UI setting (0.5s, 1s, 2s)
3. Frontend now uses WebSocket for real-time updates
4. Connection indicator shows live status

All tests passing. Documentation in docs/voice_command_v1.md.
Ready for production deployment.
"""


def summarize_text(text: str) -> str:
    """Summarize text using grok-4-fast-non-reasoning."""
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import SystemMessage, HumanMessage

    print("🔄 Summarizing with Grok...")

    llm = init_chat_model("grok-4-fast-non-reasoning", model_provider="xai", temperature=0.3)

    messages = [
        SystemMessage(content=(
            "Summarize agent task outputs in 1-2 sentences. "
            "Use natural spoken language suitable for text-to-speech."
        )),
        HumanMessage(content=f"Summarize:\n\n{text}"),
    ]

    response = llm.invoke(messages)
    return response.content


def text_to_speech(text: str, voice: str, output_path: str, client: OpenAI) -> None:
    """Convert text to speech using OpenAI TTS API."""
    print(f"🔊 Generating speech with voice '{voice}'...")

    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )

    response.stream_to_file(output_path)
    print(f"💾 Saved to: {output_path}")


def play_audio(filepath: str) -> None:
    """Play audio file using system command."""
    system = sys.platform

    try:
        if system == "darwin":  # macOS
            subprocess.run(["afplay", filepath], check=True)
        elif system == "linux":
            # Try various players
            for player in ["aplay", "paplay", "mpv", "ffplay"]:
                try:
                    subprocess.run([player, filepath], check=True)
                    return
                except FileNotFoundError:
                    continue
            print("⚠️  No audio player found. Install mpv or ffmpeg.")
        elif system == "win32":
            os.startfile(filepath)
        else:
            print(f"⚠️  Unknown platform: {system}. Cannot auto-play.")
    except Exception as e:
        print(f"⚠️  Could not play audio: {e}")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(
        description="Text-to-Speech demo with optional summarization"
    )
    parser.add_argument(
        "--text",
        type=str,
        default=SAMPLE_OUTPUT,
        help="Text to convert to speech",
    )
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Summarize text with GPT before TTS",
    )
    parser.add_argument(
        "--voice",
        type=str,
        default="alloy",
        choices=VOICES,
        help="TTS voice to use",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="speech_output.mp3",
        help="Output file path",
    )
    parser.add_argument(
        "--no-play",
        action="store_true",
        help="Don't auto-play the generated audio",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🔊 Voice Demo: Text-to-Speech for Summaries")
    print("=" * 60)

    # Check API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Export your key: export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    client = OpenAI()

    # Get text to speak
    text = args.text
    print(f"\n📄 Input text ({len(text)} chars):")
    print("-" * 40)
    print(text[:500] + ("..." if len(text) > 500 else ""))
    print("-" * 40)

    # Optionally summarize
    if args.summarize:
        text = summarize_text(text)
        print(f"\n📝 Summary:\n   '{text}'")

    # Generate speech
    print()
    text_to_speech(text, args.voice, args.output, client)

    # Play audio
    if not args.no_play:
        print("\n▶️  Playing audio...")
        play_audio(args.output)

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
