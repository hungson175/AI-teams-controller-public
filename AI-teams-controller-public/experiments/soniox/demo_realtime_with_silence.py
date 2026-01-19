"""
Soniox Demo: Real-time Transcription with Silence Detection

This demo mimics the AI Controller voice command flow:
1. Start recording from microphone
2. Stream to Soniox for real-time transcription
3. Detect silence (5 seconds) to auto-finalize
4. Print final command

This is the pattern needed for voice commands.

Usage:
    export SONIOX_API_KEY=your_api_key
    python demo_realtime_with_silence.py
"""

import os
import sys
import json
import asyncio
import time
import struct
from queue import Queue

try:
    import pyaudio
except ImportError:
    print("Error: pyaudio not installed")
    print("Install with: pip install pyaudio")
    sys.exit(1)

import websockets
from dotenv import load_dotenv

load_dotenv()

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16

# Silence detection
SILENCE_THRESHOLD_DB = -40  # dB threshold for silence
SILENCE_DURATION_SEC = 5.0  # Seconds of silence to trigger finalization

# Soniox WebSocket endpoint
SONIOX_WS_URL = "wss://stt-rt.soniox.com/transcribe-websocket"


def calculate_rms_db(audio_data: bytes) -> float:
    """Calculate RMS volume in dB from raw PCM audio."""
    samples = struct.unpack(f"<{len(audio_data)//2}h", audio_data)
    if len(samples) == 0:
        return -100

    rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
    if rms == 0:
        return -100

    # Convert to dB (reference: 32768 for 16-bit audio)
    db = 20 * (rms / 32768.0 + 1e-10).__log10__() if rms > 0 else -100
    return db


def calculate_rms_db(audio_data: bytes) -> float:
    """Calculate RMS volume in dB from raw PCM audio."""
    import math
    samples = struct.unpack(f"<{len(audio_data)//2}h", audio_data)
    if len(samples) == 0:
        return -100

    rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
    if rms == 0:
        return -100

    # Convert to dB (reference: 32768 for 16-bit audio)
    db = 20 * math.log10(rms / 32768.0 + 1e-10)
    return db


class VoiceCommandTranscriber:
    """Voice command transcription with silence detection."""

    def __init__(self, api_key: str, model: str = "stt-rt-preview"):
        self.api_key = api_key
        self.model = model
        self.audio_queue: Queue = Queue()
        self.is_running = False
        self.current_transcript = ""
        self.last_speech_time = time.time()
        self.has_speech = False

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback with silence detection."""
        if self.is_running:
            self.audio_queue.put(in_data)

            # Check if audio contains speech
            db = calculate_rms_db(in_data)
            # Debug: print dB level periodically
            if not hasattr(self, '_db_counter'):
                self._db_counter = 0
            self._db_counter += 1
            if self._db_counter % 50 == 0:  # Every ~3 seconds
                print(f"\n[DEBUG] Audio level: {db:.1f} dB (threshold: {SILENCE_THRESHOLD_DB} dB)")

            if db > SILENCE_THRESHOLD_DB:
                self.last_speech_time = time.time()
                self.has_speech = True

        return (None, pyaudio.paContinue)

    async def _send_audio(self, websocket):
        """Send audio chunks to WebSocket."""
        while self.is_running:
            try:
                audio_data = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.audio_queue.get(timeout=0.1)
                )
                await websocket.send(audio_data)
            except Exception:
                pass

    async def _receive_results(self, websocket):
        """Receive transcription results."""
        msg_count = 0
        async for message in websocket:
            data = json.loads(message)
            msg_count += 1

            # Debug: show raw message every few messages
            if msg_count <= 3 or msg_count % 20 == 0:
                print(f"\n[DEBUG] Msg #{msg_count}: {json.dumps(data)[:200]}")

            # Check for error
            if "error_message" in data and data["error_message"]:
                print(f"\nError: {data['error_message']}")
                self.is_running = False
                break

            # Process tokens (Soniox response format)
            if "tokens" in data:
                for token in data["tokens"]:
                    text = token.get("text", "")
                    is_final = token.get("is_final", False)
                    if is_final and text:
                        self.current_transcript += text
                        print(text, end="", flush=True)
                        self.last_speech_time = time.time()
                        self.has_speech = True

    async def _check_silence(self):
        """Check for silence timeout."""
        while self.is_running:
            await asyncio.sleep(0.5)

            if self.has_speech:
                silence_duration = time.time() - self.last_speech_time
                remaining = SILENCE_DURATION_SEC - silence_duration

                if remaining <= 0:
                    print(f"\n\n[Silence detected - finalizing command]")
                    self.is_running = False
                    break
                elif remaining <= 3:
                    # Show countdown
                    print(f"\r[Auto-send in {remaining:.1f}s]", end="", flush=True)

    async def record_command(self) -> str:
        """Record a single voice command with silence auto-finalization."""
        print("Connecting to Soniox...")

        url = SONIOX_WS_URL

        p = pyaudio.PyAudio()

        try:
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                stream_callback=self._audio_callback,
            )

            async with websockets.connect(url) as websocket:
                # Send start request as JSON text message first
                start_request = {
                    "api_key": self.api_key,
                    "model": self.model,
                    "sample_rate": SAMPLE_RATE,
                    "num_channels": CHANNELS,
                    "audio_format": "pcm_s16le",
                }
                await websocket.send(json.dumps(start_request))
                print("Ready! Speak your command...")
                print(f"(Will auto-send after {SILENCE_DURATION_SEC}s of silence)")
                print("-" * 50)

                self.is_running = True
                self.current_transcript = ""
                self.has_speech = False
                self.last_speech_time = time.time()

                stream.start_stream()

                # Run all tasks
                send_task = asyncio.create_task(self._send_audio(websocket))
                receive_task = asyncio.create_task(self._receive_results(websocket))
                silence_task = asyncio.create_task(self._check_silence())

                # Wait for silence detection to trigger stop
                await silence_task

                # Send empty frame to gracefully close the stream
                try:
                    await websocket.send("")
                    # Wait briefly for final response
                    await asyncio.sleep(0.5)
                except Exception:
                    pass

                # Cancel remaining tasks
                send_task.cancel()
                receive_task.cancel()

        except KeyboardInterrupt:
            print("\n\nCancelled by user")

        finally:
            self.is_running = False
            stream.stop_stream()
            stream.close()
            p.terminate()

        return self.current_transcript.strip()


async def main():
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        print("Error: SONIOX_API_KEY environment variable not set")
        sys.exit(1)

    model = sys.argv[1] if len(sys.argv) > 1 else "stt-rt-preview"

    # Check for hands-free mode
    hands_free = "--loop" in sys.argv or "-l" in sys.argv

    print(f"Soniox Voice Command Demo (Model: {model})")
    if hands_free:
        print("Mode: HANDS-FREE (continuous listening)")
    print("=" * 50)

    transcriber = VoiceCommandTranscriber(api_key, model)
    command_count = 0

    try:
        while True:
            command = await transcriber.record_command()
            command_count += 1

            print("\n" + "=" * 50)
            print(f"COMMAND #{command_count}:")
            print(command)
            print("=" * 50)

            # In real usage, this would be sent to the LLM for correction
            # and then to the tmux pane
            if command.strip():
                print("\n[Would send to LLM for correction, then to tmux pane]")
            else:
                print("\n[Empty command, skipping]")

            if not hands_free:
                break

            print("\n" + "~" * 50)
            print("Listening for next command... (Ctrl+C to stop)")
            print("~" * 50 + "\n")
            await asyncio.sleep(1)  # Brief pause between commands

    except KeyboardInterrupt:
        print(f"\n\nStopped. Total commands captured: {command_count}")


if __name__ == "__main__":
    asyncio.run(main())
