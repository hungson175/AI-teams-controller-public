"""
OpenAI Realtime API WebSocket Client.

Provides a clean async interface for speech-to-speech communication
with the OpenAI Realtime API.
"""

import asyncio
import json
import os
from typing import Callable, Optional, Any
from dataclasses import dataclass, field

import websockets
from websockets.asyncio.client import ClientConnection

from audio_utils import audio_to_base64, base64_to_audio, SAMPLE_RATE


@dataclass
class SessionConfig:
    """Configuration for the Realtime API session."""
    model: str = "gpt-4o-realtime-preview"
    voice: str = "alloy"  # Options: alloy, echo, shimmer, cedar, marin
    instructions: str = "You are a helpful assistant. Be concise in your responses."
    input_audio_format: str = "pcm16"
    output_audio_format: str = "pcm16"
    turn_detection: Optional[dict] = None  # None = server VAD, or custom config
    tools: list = field(default_factory=list)

    def __post_init__(self):
        if self.turn_detection is None:
            # Default server-side VAD (Voice Activity Detection)
            self.turn_detection = {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500,
            }


class RealtimeClient:
    """
    Async client for OpenAI Realtime API.

    Usage:
        async with RealtimeClient(api_key) as client:
            await client.send_audio(audio_data)
            async for event in client.events():
                handle_event(event)
    """

    WEBSOCKET_URL = "wss://api.openai.com/v1/realtime"

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[SessionConfig] = None,
        on_audio: Optional[Callable[[bytes], None]] = None,
        on_transcript: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[dict], None]] = None,
        on_interrupt: Optional[Callable[[], None]] = None,
    ):
        """
        Initialize the Realtime client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            config: Session configuration
            on_audio: Callback for received audio chunks
            on_transcript: Callback for transcription text
            on_error: Callback for error events
            on_interrupt: Callback when user interrupts (speech detected during response)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not provided")

        self.config = config or SessionConfig()
        self.on_audio = on_audio
        self.on_transcript = on_transcript
        self.on_error = on_error
        self.on_interrupt = on_interrupt

        self._ws: Optional[ClientConnection] = None
        self._connected = False
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._is_responding = False  # Track if AI is currently responding

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        """Establish WebSocket connection to the Realtime API."""
        url = f"{self.WEBSOCKET_URL}?model={self.config.model}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1",
        }

        self._ws = await websockets.connect(url, additional_headers=headers)
        self._connected = True

        # Configure the session
        await self._configure_session()

        # Start listening for events
        asyncio.create_task(self._listen())

    async def _configure_session(self) -> None:
        """Send session configuration to the API."""
        session_update = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "voice": self.config.voice,
                "instructions": self.config.instructions,
                "input_audio_format": self.config.input_audio_format,
                "output_audio_format": self.config.output_audio_format,
                "turn_detection": self.config.turn_detection,
                "tools": self.config.tools,
            },
        }
        await self._send(session_update)

    async def _send(self, event: dict) -> None:
        """Send an event to the API."""
        if self._ws:
            await self._ws.send(json.dumps(event))

    async def _listen(self) -> None:
        """Listen for events from the API."""
        try:
            async for message in self._ws:
                event = json.loads(message)
                await self._handle_event(event)
        except websockets.exceptions.ConnectionClosed:
            self._connected = False

    async def _handle_event(self, event: dict) -> None:
        """Process incoming events and route to callbacks."""
        event_type = event.get("type", "")

        # Queue all events for async iteration
        await self._event_queue.put(event)

        # Track response state for interruption detection
        if event_type == "response.created":
            self._is_responding = True
        elif event_type in ("response.done", "response.cancelled"):
            self._is_responding = False

        # Handle interruption: user started speaking while AI is responding
        if event_type == "input_audio_buffer.speech_started":
            if self._is_responding:
                # User interrupted! Cancel the response
                await self.cancel_response()
                if self.on_interrupt:
                    self.on_interrupt()

        # Handle specific event types
        elif event_type == "response.audio.delta":
            if self.on_audio and "delta" in event:
                audio_data = base64_to_audio(event["delta"])
                self.on_audio(audio_data)

        elif event_type == "response.audio_transcript.delta":
            if self.on_transcript and "delta" in event:
                self.on_transcript(event["delta"])

        elif event_type == "conversation.item.input_audio_transcription.completed":
            if self.on_transcript and "transcript" in event:
                self.on_transcript(f"[You]: {event['transcript']}")

        elif event_type == "error":
            if self.on_error:
                self.on_error(event.get("error", {}))
            else:
                print(f"Error: {event.get('error', {})}")

    async def events(self):
        """Async generator for all events."""
        while self._connected:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=0.1)
                yield event
            except asyncio.TimeoutError:
                continue

    async def send_audio(self, audio_pcm16) -> None:
        """
        Send audio to the API.

        Args:
            audio_pcm16: NumPy array of int16 PCM audio samples (24kHz mono)
        """
        if not self._connected:
            raise RuntimeError("Not connected to Realtime API")

        audio_base64 = audio_to_base64(audio_pcm16)
        await self._send({
            "type": "input_audio_buffer.append",
            "audio": audio_base64,
        })

    async def commit_audio(self) -> None:
        """Commit the audio buffer and trigger a response."""
        await self._send({"type": "input_audio_buffer.commit"})
        await self._send({"type": "response.create"})

    async def send_text(self, text: str) -> None:
        """
        Send a text message to the API.

        Args:
            text: Text message to send
        """
        await self._send({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": text}],
            },
        })
        await self._send({"type": "response.create"})

    async def cancel_response(self) -> None:
        """Cancel the current response (for interruption handling)."""
        await self._send({"type": "response.cancel"})

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self._ws:
            await self._ws.close()
            self._connected = False

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
