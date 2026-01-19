#!/usr/bin/env python3
"""
Full Voice-to-Command Pipeline Experiment.

This experiment demonstrates the complete flow:
1. Voice input → GPT Realtime API (S2T with stop word detection)
2. Voice transcript + tmux context → grok-4-fast-non-reasoning (T2T pronunciation correction)
3. Corrected command ready to send to tmux pane

Requirements:
    uv add langchain-xai
    # or use init_chat_model with XAI_API_KEY

Usage:
    uv run python exp_full_voice_2_command.py

    # Test T2T only (no voice):
    uv run python exp_full_voice_2_command.py --test-t2t

Press Ctrl+C to stop.
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Configuration
STOP_WORDS = [
    "go go go",
    "go go",
]
SAMPLE_RATE = 24000
CHANNELS = 1

# Import system prompt from backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from app.services.prompts import VOICE_2_COMMAND_SYSTEM_PROMPT


def get_tmux_pane_content(session: str, pane_index: int = 0, lines: int = 50) -> str:
    """Get content from a tmux pane.

    Args:
        session: tmux session name
        pane_index: pane index (default 0)
        lines: number of lines to capture

    Returns:
        Pane content as string
    """
    target = f"{session}:0.{pane_index}"
    try:
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", target, "-p", "-S", f"-{lines}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return f"[Error capturing pane: {result.stderr}]"
    except FileNotFoundError:
        return "[tmux not found]"
    except subprocess.TimeoutExpired:
        return "[tmux command timed out]"
    except Exception as e:
        return f"[Error: {e}]"


def list_tmux_sessions() -> list[str]:
    """List all tmux sessions."""
    try:
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return [s for s in result.stdout.strip().split("\n") if s]
        return []
    except Exception:
        return []


class CorrectedCommand(BaseModel):
    """Structured output for voice command correction."""
    command: str = Field(description="The corrected command in English only")


def correct_voice_command(voice_transcript: str, tmux_context: str) -> str:
    """Use LLM to correct pronunciation errors in voice transcript.

    Args:
        voice_transcript: Raw transcript from voice input (may have errors)
        tmux_context: Current tmux pane content for context

    Returns:
        Corrected command string
    """
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import SystemMessage, HumanMessage

    # Use grok-4-fast-non-reasoning for speed
    # Requires XAI_API_KEY environment variable
    llm = init_chat_model("grok-4-fast-non-reasoning", model_provider="xai", temperature=0.1)
    structured_llm = llm.with_structured_output(CorrectedCommand)

    # Build user message with context
    user_content = f"""## Tmux Pane Context (last 50 lines):
```
{tmux_context[-2000:] if len(tmux_context) > 2000 else tmux_context}
```

## Voice Transcript (may have pronunciation errors):
"{voice_transcript}"
"""

    messages = [
        SystemMessage(content=VOICE_2_COMMAND_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = structured_llm.invoke(messages)
    return response.command


def detect_stop_word(text: str) -> tuple[bool, str, str]:
    """Check for stop word and extract command."""
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


async def voice_to_text_realtime(duration: int = 30) -> tuple[str, bool]:
    """Capture voice and transcribe using GPT Realtime API.

    Returns:
        (transcript, stop_word_detected)
    """
    import base64
    import queue
    import numpy as np
    import sounddevice as sd
    import websockets

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    full_transcript = ""
    stop_word_detected = False
    detected_command = ""

    # Connect to Realtime API
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1",
    }

    print(f"\n🎤 Recording... (max {duration}s)")
    print(f"   Say 'go go' to trigger command send")
    print("   Press Ctrl+C to stop early\n")

    async with websockets.connect(url, additional_headers=headers) as ws:
        # Configure session
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text"],
                "instructions": "Transcribe exactly what the user says.",
                "input_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 800,
                },
            },
        }))

        # Audio capture setup
        audio_queue = queue.Queue()

        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
            audio_queue.put(audio_int16.tobytes())

        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='float32',
            blocksize=int(SAMPLE_RATE * 0.05),
            callback=audio_callback,
        )

        async def send_audio():
            """Send audio chunks to API."""
            while True:
                try:
                    audio_data = audio_queue.get_nowait()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    await ws.send(json.dumps({
                        "type": "input_audio_buffer.append",
                        "audio": audio_base64,
                    }))
                except queue.Empty:
                    pass
                await asyncio.sleep(0.01)

        async def receive_events():
            """Receive and process events."""
            nonlocal full_transcript, stop_word_detected, detected_command

            async for message in ws:
                event = json.loads(message)
                event_type = event.get("type", "")

                if event_type == "conversation.item.input_audio_transcription.completed":
                    transcript = event.get("transcript", "")
                    if transcript:
                        full_transcript += " " + transcript
                        full_transcript = full_transcript.strip()
                        print(f"   📝 {transcript}")

                        # Check for stop word
                        triggered, command, matched = detect_stop_word(full_transcript)
                        if triggered:
                            stop_word_detected = True
                            detected_command = command
                            return

                elif event_type == "error":
                    error = event.get("error", {})
                    print(f"   ❌ Error: {error.get('message', error)}")

        # Start recording
        stream.start()
        send_task = asyncio.create_task(send_audio())
        receive_task = asyncio.create_task(receive_events())

        try:
            # Wait for stop word or timeout
            await asyncio.wait_for(receive_task, timeout=duration)
        except asyncio.TimeoutError:
            print("\n⏱️  Max duration reached")
        except KeyboardInterrupt:
            print("\n⏹️  Recording stopped")
        finally:
            send_task.cancel()
            stream.stop()
            stream.close()

    return (detected_command if stop_word_detected else full_transcript, stop_word_detected)


def test_t2t_correction():
    """Test T2T correction with sample data."""
    print("=" * 60)
    print("🧪 Testing T2T Voice Correction")
    print("=" * 60)

    # Check API key
    if not os.environ.get("XAI_API_KEY"):
        print("\n❌ Error: XAI_API_KEY not set")
        print("   Export your key: export XAI_API_KEY=xai-...")
        sys.exit(1)

    # Sample test cases
    test_cases = [
        {
            "voice": "run cross code to fix the bug",
            "context": "Session: AI-teams-PM\nRunning claude-code CLI\n> Waiting for input...",
        },
        {
            "voice": "tell the PM to update the A.P.I documentation",
            "context": "Roles: PM, Developer, CR\nPM is working on API docs",
        },
        {
            "voice": "use tea mux to switch to the back end pane",
            "context": "tmux session: backend-team\nPanes: frontend, backend, database",
        },
        {
            "voice": "chay cross code de sua cai loi nay di",
            "context": "Session: AI-teams-PM\nRunning claude-code CLI\n> Error in main.py",
        },
        {
            "voice": "cap nhat file readme roi gui cho PM nhe",
            "context": "Roles: PM, Developer\nWorking on README.md",
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Test {i} ---")
        print(f"Voice: '{case['voice']}'")
        print(f"Context: {case['context'][:50]}...")

        corrected = correct_voice_command(case["voice"], case["context"])
        print(f"✅ Corrected: '{corrected}'")


async def main():
    parser = argparse.ArgumentParser(description="Voice-to-Command Pipeline")
    parser.add_argument("--test-t2t", action="store_true", help="Test T2T correction only")
    parser.add_argument("--session", type=str, help="Tmux session name for context")
    parser.add_argument("--pane", type=int, default=0, help="Tmux pane index (default: 0)")
    args = parser.parse_args()

    if args.test_t2t:
        test_t2t_correction()
        return

    print("=" * 60)
    print("🎙️  Full Voice-to-Command Pipeline")
    print("=" * 60)

    # Check API keys
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY not set")
        sys.exit(1)

    if not os.environ.get("XAI_API_KEY"):
        print("\n❌ Error: XAI_API_KEY not set")
        print("   Export your key: export XAI_API_KEY=xai-...")
        sys.exit(1)

    # Get tmux session
    session = args.session
    if not session:
        sessions = list_tmux_sessions()
        if sessions:
            print(f"\nAvailable tmux sessions: {sessions}")
            session = sessions[0]
            print(f"Using first session: {session}")
        else:
            print("\n⚠️  No tmux sessions found. Using mock context.")
            session = None

    # Get tmux context
    if session:
        tmux_context = get_tmux_pane_content(session, args.pane)
        print(f"\n📋 Tmux context from {session}:0.{args.pane}")
        print("-" * 40)
        print(tmux_context[-500:] if len(tmux_context) > 500 else tmux_context)
        print("-" * 40)
    else:
        tmux_context = "[No tmux context available]"

    print(f"\nStop words: {STOP_WORDS}")
    print("Example: 'Run cross code to fix the bug, send please'")

    # Step 1: Voice to Text (S2T)
    print("\n" + "=" * 40)
    print("📢 STEP 1: Voice to Text (GPT Realtime API)")
    print("=" * 40)

    try:
        voice_transcript, stop_detected = await voice_to_text_realtime()
    except Exception as e:
        print(f"\n❌ S2T Error: {e}")
        return

    print(f"\n📝 Voice Transcript: '{voice_transcript}'")
    print(f"   Stop word detected: {stop_detected}")

    if not voice_transcript:
        print("\n❌ No voice input captured")
        return

    # Step 2: Text to Text (T2T) - Pronunciation Correction
    print("\n" + "=" * 40)
    print("🔄 STEP 2: Pronunciation Correction (grok-4-fast-non-reasoning)")
    print("=" * 40)

    corrected_command = correct_voice_command(voice_transcript, tmux_context)

    print(f"\n✅ Corrected Command: '{corrected_command}'")

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"   Voice Input: '{voice_transcript}'")
    print(f"   Corrected:   '{corrected_command}'")
    print(f"   Stop Word:   {stop_detected}")
    if session:
        print(f"   Target:      {session}:0.{args.pane}")
    print("=" * 60)

    if stop_detected:
        print("\n🚀 Command ready to send to tmux pane!")
        print(f"   tmux send-keys -t {session}:0.{args.pane} '{corrected_command}' Enter")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
