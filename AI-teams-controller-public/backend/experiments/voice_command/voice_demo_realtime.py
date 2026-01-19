#!/usr/bin/env python3
"""
Voice Demo: Speech-to-Text using GPT Realtime API with Stop Word Detection.

This demo uses OpenAI GPT Realtime API for transcription (S2T) instead of Whisper.
When the stop word "send please" is detected, it extracts the command.

Requirements:
    uv sync

Usage:
    uv run python voice_demo_realtime.py

Press Ctrl+C to stop.
"""

import asyncio
import json
import os
import sys
from typing import Optional

from dotenv import load_dotenv
import websockets

# Load environment variables
load_dotenv()

# Configuration
STOP_WORDS = [
    "send please",
    "send pls",
    "send, please",
    "send it please",
    "sent please",
    "send please.",
    "send pls.",
]
SAMPLE_RATE = 24000  # 24kHz for Realtime API
CHANNELS = 1


def detect_stop_word(text: str) -> tuple[bool, str, str]:
    """
    Check for stop word and extract command.

    Returns:
        (triggered, command, matched_word) - triggered is True if stop word found
    """
    text_lower = text.lower()

    for stop_word in STOP_WORDS:
        if stop_word in text_lower:
            idx = text_lower.find(stop_word)
            command = text[:idx].strip()

            # Clean up common filler words at the end
            for filler in [",", ".", "and", "so", "then"]:
                if command.lower().endswith(filler):
                    command = command[: -len(filler)].strip()

            return True, command, stop_word

    return False, text, ""


class RealtimeTranscriber:
    """Uses GPT Realtime API for speech-to-text transcription."""

    WEBSOCKET_URL = "wss://api.openai.com/v1/realtime"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._ws = None
        self._connected = False
        self._full_transcript = ""
        self._command_detected = False
        self._detected_command = ""
        self._matched_word = ""

    async def connect(self):
        """Connect to Realtime API."""
        url = f"{self.WEBSOCKET_URL}?model=gpt-4o-realtime-preview"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1",
        }

        self._ws = await websockets.connect(url, additional_headers=headers)
        self._connected = True

        # Configure session for transcription only (no response)
        await self._configure_session()
        print("Connected to GPT Realtime API")

    async def _configure_session(self):
        """Configure session for transcription."""
        session_update = {
            "type": "session.update",
            "session": {
                "modalities": ["text"],  # Text only - we just want transcription
                "instructions": "Transcribe exactly what the user says. Do not respond.",
                "input_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1",  # Use Whisper for transcription
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 800,  # Longer silence to detect end of speech
                },
            },
        }
        await self._ws.send(json.dumps(session_update))

    async def send_audio(self, audio_data: bytes):
        """Send audio chunk to API."""
        if not self._connected:
            return

        import base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        await self._ws.send(json.dumps({
            "type": "input_audio_buffer.append",
            "audio": audio_base64,
        }))

    async def listen_for_events(self):
        """Listen for transcription events."""
        try:
            async for message in self._ws:
                event = json.loads(message)
                event_type = event.get("type", "")

                # Handle transcription completed
                if event_type == "conversation.item.input_audio_transcription.completed":
                    transcript = event.get("transcript", "")
                    if transcript:
                        self._full_transcript += " " + transcript
                        self._full_transcript = self._full_transcript.strip()
                        print(f"Transcript: {transcript}")

                        # Check for stop word
                        triggered, command, matched = detect_stop_word(self._full_transcript)
                        if triggered:
                            self._command_detected = True
                            self._detected_command = command
                            self._matched_word = matched
                            return  # Exit loop when stop word detected

                elif event_type == "error":
                    error = event.get("error", {})
                    print(f"Error: {error.get('message', error)}")

                elif event_type == "input_audio_buffer.speech_stopped":
                    print("[Speech ended, processing...]")

        except websockets.exceptions.ConnectionClosed:
            self._connected = False

    async def close(self):
        """Close connection."""
        if self._ws:
            await self._ws.close()
            self._connected = False

    @property
    def command_detected(self) -> bool:
        return self._command_detected

    @property
    def detected_command(self) -> str:
        return self._detected_command

    @property
    def matched_word(self) -> str:
        return self._matched_word

    @property
    def full_transcript(self) -> str:
        return self._full_transcript


async def record_and_transcribe(transcriber: RealtimeTranscriber, duration: int = 30):
    """Record audio and send to Realtime API for transcription."""
    import numpy as np
    import sounddevice as sd
    import queue

    print(f"\n🎤 Recording... (max {duration}s)")
    print(f"   Say 'send please' to trigger command send")
    print("   Press Ctrl+C to stop early\n")

    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time, status):
        if status:
            print(f"Audio status: {status}")
        # Convert float32 to int16 PCM
        audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
        audio_queue.put(audio_int16.tobytes())

    # Start recording
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='float32',
        blocksize=int(SAMPLE_RATE * 0.05),  # 50ms chunks
        callback=audio_callback,
    )

    # Start listening task
    listen_task = asyncio.create_task(transcriber.listen_for_events())

    try:
        stream.start()
        start_time = asyncio.get_event_loop().time()

        while True:
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= duration:
                print("\n⏱️  Max duration reached")
                break

            # Check if command detected
            if transcriber.command_detected:
                break

            # Send audio chunks
            try:
                audio_data = audio_queue.get_nowait()
                await transcriber.send_audio(audio_data)
            except queue.Empty:
                pass

            await asyncio.sleep(0.01)

    except KeyboardInterrupt:
        print("\n⏹️  Recording stopped by user")
    finally:
        stream.stop()
        stream.close()
        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            pass


async def main():
    print("=" * 60)
    print("🎙️  Voice Demo: GPT Realtime API Speech-to-Text")
    print("=" * 60)

    # Check API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    print(f"\nStop words: {STOP_WORDS}")
    print("Example: 'Update the documentation for the API, send please'")

    transcriber = RealtimeTranscriber(api_key)

    try:
        await transcriber.connect()
        await record_and_transcribe(transcriber)

        print("\n" + "-" * 40)
        print(f"📝 Full Transcript: '{transcriber.full_transcript}'")

        if transcriber.command_detected:
            print(f"✅ Stop word detected: '{transcriber.matched_word}'")
            print(f"📤 Command to send:\n   '{transcriber.detected_command}'")
        else:
            print(f"⏳ No stop word detected")
            print(f"   Expected one of: {STOP_WORDS}")
        print("-" * 40)

    finally:
        await transcriber.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
