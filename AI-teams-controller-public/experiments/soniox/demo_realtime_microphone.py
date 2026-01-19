"""
Soniox Demo: Real-time Microphone Transcription

This demo captures audio from your microphone and streams it to Soniox
for real-time transcription.

Usage:
    export SONIOX_API_KEY=your_api_key
    python demo_realtime_microphone.py

Press Ctrl+C to stop recording.
"""

import os
import sys
import json
import asyncio
import threading
from queue import Queue

try:
    import pyaudio
except ImportError:
    print("Error: pyaudio not installed")
    print("Install with: pip install pyaudio")
    print("On Mac: brew install portaudio && pip install pyaudio")
    sys.exit(1)

import websockets
from dotenv import load_dotenv

load_dotenv()

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024  # ~64ms at 16kHz
FORMAT = pyaudio.paInt16

# Soniox WebSocket endpoint
SONIOX_WS_URL = "wss://stt-rt.soniox.com/transcribe-websocket"


class SonioxRealtimeTranscriber:
    """Real-time transcription using Soniox WebSocket API."""

    def __init__(self, api_key: str, model: str = "soniox_enhanced"):
        self.api_key = api_key
        self.model = model
        self.audio_queue: Queue = Queue()
        self.is_running = False
        self.current_transcript = ""

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback - runs in separate thread."""
        if self.is_running:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    async def _send_audio(self, websocket):
        """Send audio chunks to WebSocket."""
        while self.is_running:
            try:
                # Get audio with timeout to allow checking is_running
                audio_data = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.audio_queue.get(timeout=0.1)
                )
                await websocket.send(audio_data)
            except Exception:
                # Queue timeout or other error, continue
                pass

    async def _receive_results(self, websocket):
        """Receive transcription results from WebSocket."""
        async for message in websocket:
            data = json.loads(message)

            if "fw" in data:
                # Final words
                for word in data["fw"]:
                    text = word.get("t", "")
                    self.current_transcript += text
                    print(text, end="", flush=True)

            elif "nfw" in data:
                # Non-final (interim) words - optional display
                interim = "".join(w.get("t", "") for w in data["nfw"])
                # Print interim results in gray (optional)
                # print(f"\033[90m{interim}\033[0m", end="\r", flush=True)

            elif "error" in data:
                print(f"\nError: {data['error']}")
                break

    async def start(self):
        """Start real-time transcription."""
        print("Connecting to Soniox...")

        # Build WebSocket URL with params
        params = {
            "api_key": self.api_key,
            "model": self.model,
            "sample_rate_hertz": SAMPLE_RATE,
            "num_audio_channels": CHANNELS,
            "encoding": "pcm_s16le",
            "enable_endpoint_detection": "true",
            "enable_streaming_speaker_diarization": "false",
        }

        url = SONIOX_WS_URL + "?" + "&".join(f"{k}={v}" for k, v in params.items())

        # Initialize PyAudio
        p = pyaudio.PyAudio()

        try:
            # Open microphone stream
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                stream_callback=self._audio_callback,
            )

            async with websockets.connect(url) as websocket:
                print("Connected! Speak now... (Ctrl+C to stop)")
                print("-" * 50)

                self.is_running = True
                stream.start_stream()

                # Run send and receive concurrently
                send_task = asyncio.create_task(self._send_audio(websocket))
                receive_task = asyncio.create_task(self._receive_results(websocket))

                try:
                    await asyncio.gather(send_task, receive_task)
                except asyncio.CancelledError:
                    pass

        except KeyboardInterrupt:
            print("\n\nStopping...")

        finally:
            self.is_running = False
            stream.stop_stream()
            stream.close()
            p.terminate()

            print("\n" + "-" * 50)
            print("Final transcript:")
            print(self.current_transcript)


async def main():
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        print("Error: SONIOX_API_KEY environment variable not set")
        print("Get your API key from: https://console.soniox.com")
        sys.exit(1)

    # Model options:
    # - "soniox_enhanced" - best accuracy, supports 60+ languages
    # - "en_v2" - English optimized
    # - "vi" - Vietnamese
    model = sys.argv[1] if len(sys.argv) > 1 else "soniox_enhanced"

    print(f"Model: {model}")
    print("=" * 50)

    transcriber = SonioxRealtimeTranscriber(api_key, model)

    try:
        await transcriber.start()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())
