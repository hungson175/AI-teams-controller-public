#!/usr/bin/env python3
"""
Push-to-Talk Speech-to-Speech Demo using OpenAI Realtime API.

This demo provides more control:
- Press SPACE to start/stop recording
- Press 'q' to quit
- Press 'm' to mute/unmute
- Press 'c' to cancel current response

Usage:
    python demo_push_to_talk.py
"""

import asyncio
import os
import sys
import threading
from typing import Optional

from dotenv import load_dotenv

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Note: Install 'rich' for better UI: pip install rich")

from realtime_client import RealtimeClient, SessionConfig
from audio_handler import AudioHandler

# Load environment variables
load_dotenv()


class PushToTalkDemo:
    """Interactive push-to-talk demo with rich UI."""

    def __init__(self):
        self.audio_handler = AudioHandler()
        self.client: Optional[RealtimeClient] = None
        self.recording = False
        self.muted = False
        self.running = True
        self.transcript_buffer = []
        self.status = "Idle"

        if RICH_AVAILABLE:
            self.console = Console()

    def on_audio(self, audio_data):
        """Handle incoming audio from the API."""
        self.audio_handler.play_audio(audio_data)

    def on_transcript(self, text):
        """Handle incoming transcript."""
        self.transcript_buffer.append(text)
        # Keep only last 20 lines
        if len(self.transcript_buffer) > 20:
            self.transcript_buffer = self.transcript_buffer[-20:]
        self._update_display()

    def on_error(self, error):
        """Handle errors."""
        msg = f"[Error] {error.get('message', error)}"
        self.transcript_buffer.append(msg)
        self._update_display()

    def _update_display(self):
        """Update the terminal display."""
        if RICH_AVAILABLE:
            # Will be handled by Live context
            pass
        else:
            # Simple print for non-rich mode
            if self.transcript_buffer:
                print(self.transcript_buffer[-1], end="", flush=True)

    def _render_ui(self):
        """Render the UI panel."""
        if not RICH_AVAILABLE:
            return ""

        # Status line
        status_color = "green" if self.recording else "yellow" if self.status == "Processing..." else "white"
        status_text = Text()
        status_text.append(f"Status: ", style="bold")
        status_text.append(self.status, style=status_color)

        if self.muted:
            status_text.append(" [MUTED]", style="red")

        # Transcript
        transcript_text = "\n".join(self.transcript_buffer[-15:]) if self.transcript_buffer else "(No conversation yet)"

        # Controls
        controls = """
[SPACE] Start/Stop Recording  [M] Mute/Unmute  [C] Cancel Response  [Q] Quit
        """

        content = f"""
{status_text}

{"-" * 50}
{transcript_text}
{"-" * 50}
{controls}
"""
        return Panel(content, title="OpenAI Realtime API - Push-to-Talk Demo", border_style="blue")

    async def handle_keyboard(self):
        """Handle keyboard input in a separate thread."""
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            while self.running:
                # Non-blocking check for input
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)

                    if key == ' ':  # Space - toggle recording
                        await self.toggle_recording()
                    elif key.lower() == 'q':  # Quit
                        self.running = False
                        break
                    elif key.lower() == 'm':  # Mute
                        self.toggle_mute()
                    elif key.lower() == 'c':  # Cancel
                        await self.cancel_response()

                await asyncio.sleep(0.05)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    async def toggle_recording(self):
        """Toggle recording state."""
        if self.recording:
            # Stop recording and send audio
            self.recording = False
            self.status = "Processing..."
            self._update_display()

            # Commit audio buffer to trigger response
            if self.client:
                await self.client.commit_audio()
        else:
            # Start recording
            self.recording = True
            self.status = "Recording..."
            self.audio_handler.unmute()
            self._update_display()

    def toggle_mute(self):
        """Toggle mute state."""
        self.muted = not self.muted
        if self.muted:
            self.audio_handler.mute()
        else:
            self.audio_handler.unmute()
        self._update_display()

    async def cancel_response(self):
        """Cancel current AI response."""
        if self.client:
            await self.client.cancel_response()
            self.audio_handler.clear_playback_queue()
            self.status = "Response cancelled"
            self._update_display()

    async def audio_capture_loop(self):
        """Continuously capture and send audio when recording."""
        while self.running:
            if self.recording and not self.muted:
                audio_chunk = await self.audio_handler.get_audio_chunk_async(timeout=0.05)
                if audio_chunk is not None and len(audio_chunk) > 0 and self.client:
                    await self.client.send_audio(audio_chunk)
            else:
                # Still drain the queue to prevent buildup
                _ = self.audio_handler.get_audio_chunk()
                await asyncio.sleep(0.05)

    async def event_handler_loop(self):
        """Handle events from the API."""
        if not self.client:
            return

        async for event in self.client.events():
            if not self.running:
                break

            event_type = event.get("type", "")

            # Update status based on events
            if event_type == "response.audio.done":
                self.status = "Idle"
                self._update_display()
            elif event_type == "response.created":
                self.status = "AI Speaking..."
                self._update_display()

    async def run(self):
        """Main entry point."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not set!")
            print("Please copy .env.example to .env and add your API key.")
            return

        config = SessionConfig(
            voice="alloy",
            instructions="""You are a helpful voice assistant.
Keep your responses brief and conversational.
Speak naturally as if having a casual conversation.""",
            turn_detection=None,  # We're using push-to-talk, not VAD
        )

        # Disable server-side turn detection for push-to-talk
        config.turn_detection = {"type": "none"}

        print("Connecting to OpenAI Realtime API...")

        try:
            async with RealtimeClient(
                api_key=api_key,
                config=config,
                on_audio=self.on_audio,
                on_transcript=self.on_transcript,
                on_error=self.on_error,
            ) as client:
                self.client = client
                print("Connected!")

                # Start audio
                self.audio_handler.start()
                self.audio_handler.mute()  # Start muted (push-to-talk)

                self.status = "Ready - Press SPACE to talk"

                if RICH_AVAILABLE:
                    with Live(self._render_ui(), refresh_per_second=10, console=self.console) as live:
                        # Start background tasks
                        tasks = [
                            asyncio.create_task(self.handle_keyboard()),
                            asyncio.create_task(self.audio_capture_loop()),
                            asyncio.create_task(self.event_handler_loop()),
                        ]

                        # Update display in loop
                        while self.running:
                            live.update(self._render_ui())
                            await asyncio.sleep(0.1)

                        # Cancel tasks
                        for task in tasks:
                            task.cancel()
                else:
                    # Simple mode without rich
                    print("\nControls: SPACE=record, Q=quit, M=mute, C=cancel")
                    print("-" * 50)

                    tasks = [
                        asyncio.create_task(self.handle_keyboard()),
                        asyncio.create_task(self.audio_capture_loop()),
                        asyncio.create_task(self.event_handler_loop()),
                    ]

                    try:
                        await asyncio.gather(*tasks)
                    except asyncio.CancelledError:
                        pass

        finally:
            self.audio_handler.stop()
            print("\nGoodbye!")


async def main():
    demo = PushToTalkDemo()
    try:
        await demo.run()
    except KeyboardInterrupt:
        demo.running = False


if __name__ == "__main__":
    asyncio.run(main())
