#!/usr/bin/env python3
"""
Voice Demo: Full Pipeline (S2T -> T2T -> T2S)

Complete voice command flow:
1. Record voice from microphone
2. Transcribe with Whisper (S2T)
3. Detect stop word "SEND PLS"
4. Rewrite command with GPT (T2T)
5. Simulate sending to agent
6. Generate voice response (T2S)

Requirements:
    uv sync

Usage:
    uv run python voice_demo_full.py
"""

import os
import subprocess
import sys
import tempfile
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
SAMPLE_RATE = 16000
CHANNELS = 1
MAX_DURATION = 30


def record_audio(duration: int = MAX_DURATION) -> np.ndarray:
    """Record audio from microphone."""
    print(f"\n🎤 Recording... (max {duration}s, press Ctrl+C to stop)")
    print(f"   Say 'send please' or 'send pls' at the end to send command\n")

    recording = []

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
        print("\n⏹️  Recording stopped")

    if not recording:
        return np.array([])

    return np.concatenate(recording, axis=0)


def save_audio(audio: np.ndarray, filepath: str) -> None:
    """Save audio to WAV file."""
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(filepath, SAMPLE_RATE, audio_int16)


def transcribe_audio(filepath: str, client: OpenAI) -> str:
    """Transcribe audio with Whisper."""
    print("🔄 Step 1: Transcribing with Whisper (S2T)...")

    with open(filepath, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en",
        )

    return transcription.text


def detect_stop_word(text: str) -> tuple[bool, str, str]:
    """Check for stop word and extract command.

    Returns:
        (triggered, command, matched_word) - triggered is True if stop word found
    """
    text_lower = text.lower()

    for stop_word in STOP_WORDS:
        if stop_word in text_lower:
            idx = text_lower.find(stop_word)
            command = text[:idx].strip()

            for filler in [",", ".", "and", "so", "then"]:
                if command.lower().endswith(filler):
                    command = command[: -len(filler)].strip()

            return True, command, stop_word

    return False, text, ""


def rewrite_command(command: str, pane_context: str, client: OpenAI) -> str:
    """Rewrite spoken command into agent instruction (T2T)."""
    print("🔄 Step 2: Rewriting command with GPT (T2T)...")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a command translator for an AI agent team. "
                    "Rewrite the user's spoken command into a clear, actionable instruction. "
                    "Keep it concise and professional. Output only the command, nothing else."
                ),
            },
            {
                "role": "user",
                "content": f"Current pane context:\n{pane_context}\n\nUser said: \"{command}\"\n\nRewrite as agent command:",
            },
        ],
        max_tokens=200,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def simulate_agent_response() -> str:
    """Simulate agent task completion."""
    return """
Task completed successfully.

Changes made:
- Updated the API documentation with new endpoints
- Added example request/response for each endpoint
- Fixed typos in the README

All changes committed to feature branch.
"""


def generate_summary(agent_output: str, original_command: str, client: OpenAI) -> str:
    """Generate spoken summary of agent output."""
    print("🔄 Step 3: Generating summary...")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Create a brief, spoken-friendly summary (1-2 sentences) of the task completion. "
                    "Use natural language suitable for text-to-speech. "
                    "Start with 'Done.' or 'Task complete.' and mention key outcomes."
                ),
            },
            {
                "role": "user",
                "content": f"Original command: {original_command}\n\nAgent output:\n{agent_output}\n\nCreate voice summary:",
            },
        ],
        max_tokens=100,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


def text_to_speech(text: str, output_path: str, client: OpenAI) -> None:
    """Convert text to speech (T2S)."""
    print("🔄 Step 4: Generating speech (T2S)...")

    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )

    response.stream_to_file(output_path)


def play_audio(filepath: str) -> None:
    """Play audio file."""
    system = sys.platform

    try:
        if system == "darwin":
            subprocess.run(["afplay", filepath], check=True)
        elif system == "linux":
            for player in ["aplay", "paplay", "mpv", "ffplay"]:
                try:
                    subprocess.run([player, filepath], check=True)
                    return
                except FileNotFoundError:
                    continue
        elif system == "win32":
            os.startfile(filepath)
    except Exception as e:
        print(f"⚠️  Could not play audio: {e}")


def main():
    """Main demo function."""
    print("=" * 60)
    print("🎙️  Voice Demo: Full Pipeline (S2T -> T2T -> T2S)")
    print("=" * 60)

    # Check API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    client = OpenAI()

    print(f"\nStop words: {STOP_WORDS}")
    print("Example: 'Update the API documentation, SEND PLS'")

    # Simulated pane context
    pane_context = """
Current session: AI-controller-app-PM
Role: PM
Last activity: Waiting for instructions
"""

    # Record audio
    audio = record_audio(duration=15)

    if len(audio) == 0:
        print("❌ No audio recorded")
        return

    print(f"✅ Recorded {len(audio) / SAMPLE_RATE:.1f}s of audio")

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_audio = f.name
        save_audio(audio, temp_audio)

    try:
        # Step 1: Transcribe (S2T)
        text = transcribe_audio(temp_audio, client)
        print(f"   📝 Transcription: '{text}'")

        # Detect stop word
        triggered, raw_command, matched = detect_stop_word(text)

        if not triggered:
            print(f"\n⚠️  No stop word detected")
            print(f"   Expected one of: {STOP_WORDS}")
            print(f"   Full text: '{text}'")
            print("   (In production, would continue listening)")
            return

        print(f"   ✅ Stop word detected: '{matched}'")
        print(f"   📤 Raw command: '{raw_command}'")

        # Step 2: Rewrite command (T2T)
        rewritten = rewrite_command(raw_command, pane_context, client)
        print(f"   📝 Rewritten: '{rewritten}'")

        # Simulate sending and getting response
        print("\n⏳ Simulating agent execution...")
        agent_output = simulate_agent_response()
        print(f"   Agent output:{agent_output}")

        # Step 3: Generate summary
        summary = generate_summary(agent_output, rewritten, client)
        print(f"   📝 Summary: '{summary}'")

        # Step 4: Text to Speech (T2S)
        output_path = "voice_response.mp3"
        text_to_speech(summary, output_path, client)
        print(f"   💾 Saved: {output_path}")

        # Play response
        print("\n▶️  Playing voice response...")
        play_audio(output_path)

        print("\n" + "=" * 60)
        print("✅ Full pipeline complete!")
        print("=" * 60)

    finally:
        Path(temp_audio).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
