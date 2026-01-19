"""
Audio capture and playback handler using sounddevice.

Provides async-compatible audio I/O for real-time voice applications.
"""

import asyncio
import queue
import threading
from typing import Optional, Callable

import numpy as np
import sounddevice as sd

from audio_utils import (
    SAMPLE_RATE,
    CHANNELS,
    DTYPE,
    float32_to_pcm16,
    ensure_mono,
)


class AudioHandler:
    """
    Handles microphone capture and speaker playback for real-time audio.

    Uses sounddevice with callbacks for low-latency audio I/O.
    Thread-safe queues enable async integration.
    """

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
        chunk_ms: int = 50,  # Audio chunk size in milliseconds
    ):
        """
        Initialize audio handler.

        Args:
            sample_rate: Audio sample rate (default: 24000 Hz)
            channels: Number of audio channels (default: 1 = mono)
            chunk_ms: Size of audio chunks in milliseconds
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = int(sample_rate * chunk_ms / 1000)

        # Thread-safe queues for async integration
        self._input_queue: queue.Queue = queue.Queue()
        self._output_queue: queue.Queue = queue.Queue()

        # Audio streams
        self._input_stream: Optional[sd.InputStream] = None
        self._output_stream: Optional[sd.OutputStream] = None

        # Control flags
        self._recording = False
        self._playing = False
        self._muted = False

        # Event loop reference for async callbacks
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _input_callback(self, indata, frames, time, status):
        """Callback for microphone input."""
        if status:
            print(f"Input status: {status}")
        if self._recording and not self._muted:
            # Convert to mono if needed and ensure PCM16
            audio = ensure_mono(indata.copy())
            if audio.dtype == np.float32:
                audio = float32_to_pcm16(audio)
            self._input_queue.put(audio)

    def _output_callback(self, outdata, frames, time, status):
        """Callback for speaker output."""
        if status:
            print(f"Output status: {status}")

        try:
            # Get audio from queue with timeout
            audio = self._output_queue.get_nowait()

            # Ensure correct length
            if len(audio) < frames:
                # Pad with silence
                padded = np.zeros(frames, dtype=DTYPE)
                padded[:len(audio)] = audio
                audio = padded
            elif len(audio) > frames:
                # Truncate (shouldn't happen with proper chunk sizes)
                audio = audio[:frames]

            # Convert to float32 for sounddevice output
            outdata[:, 0] = audio.astype(np.float32) / 32768.0

        except queue.Empty:
            # Fill with silence if no audio available
            outdata.fill(0)

    def start_recording(self) -> None:
        """Start capturing audio from the microphone."""
        if self._recording:
            return

        self._input_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32',  # sounddevice default
            blocksize=self.chunk_size,
            callback=self._input_callback,
        )
        self._input_stream.start()
        self._recording = True
        print(f"Recording started ({self.sample_rate}Hz, {self.chunk_size} samples/chunk)")

    def stop_recording(self) -> None:
        """Stop capturing audio."""
        if self._input_stream:
            self._input_stream.stop()
            self._input_stream.close()
            self._input_stream = None
        self._recording = False
        print("Recording stopped")

    def start_playback(self) -> None:
        """Start audio playback to speakers."""
        if self._playing:
            return

        self._output_stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32',
            blocksize=self.chunk_size,
            callback=self._output_callback,
        )
        self._output_stream.start()
        self._playing = True
        print(f"Playback started ({self.sample_rate}Hz)")

    def stop_playback(self) -> None:
        """Stop audio playback."""
        if self._output_stream:
            self._output_stream.stop()
            self._output_stream.close()
            self._output_stream = None
        self._playing = False
        # Clear any remaining audio in queue
        while not self._output_queue.empty():
            try:
                self._output_queue.get_nowait()
            except queue.Empty:
                break
        print("Playback stopped")

    def mute(self) -> None:
        """Mute microphone input."""
        self._muted = True

    def unmute(self) -> None:
        """Unmute microphone input."""
        self._muted = False

    def is_muted(self) -> bool:
        """Check if microphone is muted."""
        return self._muted

    def get_audio_chunk(self) -> Optional[np.ndarray]:
        """
        Get the next audio chunk from the microphone (non-blocking).

        Returns:
            NumPy array of int16 PCM audio, or None if no audio available
        """
        try:
            return self._input_queue.get_nowait()
        except queue.Empty:
            return None

    async def get_audio_chunk_async(self, timeout: float = 0.1) -> Optional[np.ndarray]:
        """
        Get the next audio chunk asynchronously.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            NumPy array of int16 PCM audio, or None if timeout
        """
        loop = asyncio.get_event_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, self._input_queue.get),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return None

    def play_audio(self, audio_pcm16: np.ndarray) -> None:
        """
        Queue audio for playback.

        Args:
            audio_pcm16: NumPy array of int16 PCM audio samples
        """
        # Split into chunks matching output buffer size
        for i in range(0, len(audio_pcm16), self.chunk_size):
            chunk = audio_pcm16[i:i + self.chunk_size]
            self._output_queue.put(chunk)

    def clear_playback_queue(self) -> None:
        """Clear any pending audio in the playback queue."""
        while not self._output_queue.empty():
            try:
                self._output_queue.get_nowait()
            except queue.Empty:
                break

    def start(self) -> None:
        """Start both recording and playback."""
        self.start_recording()
        self.start_playback()

    def stop(self) -> None:
        """Stop both recording and playback."""
        self.stop_recording()
        self.stop_playback()

    @staticmethod
    def list_devices() -> None:
        """Print available audio devices."""
        print("Available audio devices:")
        print(sd.query_devices())

    @staticmethod
    def get_default_device_info() -> dict:
        """Get default input and output device info."""
        return {
            "input": sd.query_devices(kind='input'),
            "output": sd.query_devices(kind='output'),
        }
