#!/usr/bin/env python3
"""
Simple Speech-to-Speech Demo using OpenAI Realtime API.

This demo supports INTERRUPTION:
- When the AI is speaking, you can interrupt by speaking
- The AI will stop and listen to you

Features:
1. Captures audio from your microphone
2. Sends it to OpenAI Realtime API
3. Plays back the AI's voice response
4. Supports natural interruption (speak to interrupt the AI)

Usage:
    python demo_simple.py

Press Ctrl+C to exit.
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

from realtime_client import RealtimeClient, SessionConfig
from audio_handler import AudioHandler

# Load environment variables
load_dotenv()


async def main():
    print("=" * 60)
    print("OpenAI Realtime API - Speech-to-Speech Demo")
    print("=" * 60)

    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\nError: OPENAI_API_KEY not set!")
        print("Please copy .env.example to .env and add your API key.")
        sys.exit(1)

    # Initialize audio handler
    audio_handler = AudioHandler()

    # Configure the session with VAD for interruption support
    config = SessionConfig(
        voice="alloy",  # Options: alloy, echo, shimmer, cedar, marin
        instructions="""You are a helpful voice assistant.
Keep your responses brief and conversational.
Speak naturally as if having a casual conversation.
If the user interrupts you, stop speaking and listen to them.""",
    )

    # Callbacks for handling responses
    def on_audio(audio_data):
        """Called when audio chunk is received from the API."""
        audio_handler.play_audio(audio_data)

    def on_transcript(text):
        """Called when transcript is received."""
        print(f"{text}", end="", flush=True)

    def on_error(error):
        """Called when an error occurs."""
        print(f"\n[Error] {error.get('message', error)}")

    def on_interrupt():
        """Called when user interrupts the AI."""
        # Clear any pending audio in the playback queue
        audio_handler.clear_playback_queue()
        print("\n[Interrupted - listening...]", flush=True)

    print("\nConnecting to OpenAI Realtime API...")

    try:
        async with RealtimeClient(
            api_key=api_key,
            config=config,
            on_audio=on_audio,
            on_transcript=on_transcript,
            on_error=on_error,
            on_interrupt=on_interrupt,
        ) as client:
            print("Connected!")
            print("\n" + "-" * 60)
            print("Speak into your microphone. The AI will respond.")
            print("You can INTERRUPT the AI by speaking while it talks!")
            print("Press Ctrl+C to exit.")
            print("-" * 60 + "\n")

            # Start audio I/O
            audio_handler.start()

            # Main loop: capture and send audio
            try:
                while True:
                    # Get audio from microphone
                    audio_chunk = await audio_handler.get_audio_chunk_async(timeout=0.05)

                    if audio_chunk is not None and len(audio_chunk) > 0:
                        # Send to API
                        await client.send_audio(audio_chunk)

                    # Small delay to prevent CPU spinning
                    await asyncio.sleep(0.01)

            except KeyboardInterrupt:
                print("\n\nShutting down...")

            finally:
                audio_handler.stop()

    except Exception as e:
        print(f"\nConnection error: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
