#!/usr/bin/env python3
"""
Speech-to-Speech Demo with Function Calling (Tools).

This demo shows how to use OpenAI Realtime API with function calling,
which is essential for the AI Teams Controller use case.

The AI can:
- Send commands to team roles (simulated)
- Get status of team roles (simulated)
- Execute various tools via voice commands

Usage:
    python demo_with_tools.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

from realtime_client import RealtimeClient, SessionConfig
from audio_handler import AudioHandler

# Load environment variables
load_dotenv()


# =============================================================================
# Simulated Team Management Functions
# =============================================================================

# Simulated team state
TEAM_STATE = {
    "pm": {
        "name": "Project Manager",
        "status": "Working on sprint planning",
        "last_update": "2 minutes ago",
    },
    "developer": {
        "name": "Developer",
        "status": "Implementing authentication module",
        "last_update": "5 minutes ago",
    },
    "code_reviewer": {
        "name": "Code Reviewer",
        "status": "Reviewing PR #42 - API refactoring",
        "last_update": "1 minute ago",
    },
}


def send_to_role(role: str, message: str) -> dict:
    """
    Simulate sending a command to a team role.

    In the real implementation, this would send to tmux pane.
    """
    if role not in TEAM_STATE:
        return {"success": False, "error": f"Unknown role: {role}"}

    # Simulate sending command
    print(f"\n[TOOL] Sending to {TEAM_STATE[role]['name']}: {message}")

    return {
        "success": True,
        "message": f"Command sent to {TEAM_STATE[role]['name']}",
        "role": role,
    }


def get_role_status(role: str) -> dict:
    """
    Get the current status of a team role.

    In the real implementation, this would read from tmux pane.
    """
    if role not in TEAM_STATE:
        return {"success": False, "error": f"Unknown role: {role}"}

    state = TEAM_STATE[role]
    return {
        "success": True,
        "role": role,
        "name": state["name"],
        "status": state["status"],
        "last_update": state["last_update"],
    }


def get_team_overview() -> dict:
    """Get an overview of all team members."""
    overview = []
    for role, state in TEAM_STATE.items():
        overview.append({
            "role": role,
            "name": state["name"],
            "status": state["status"],
            "last_update": state["last_update"],
        })
    return {"success": True, "team": overview}


def get_current_time() -> dict:
    """Get the current time."""
    now = datetime.now()
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "day": now.strftime("%A"),
    }


# =============================================================================
# Tool Definitions for OpenAI Realtime API
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "name": "send_to_role",
        "description": "Send a command or message to a specific team role (PM, Developer, or Code Reviewer). Use this when the user wants to instruct a team member.",
        "parameters": {
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "enum": ["pm", "developer", "code_reviewer"],
                    "description": "The team role to send the message to",
                },
                "message": {
                    "type": "string",
                    "description": "The command or message to send to the role",
                },
            },
            "required": ["role", "message"],
        },
    },
    {
        "type": "function",
        "name": "get_role_status",
        "description": "Get the current status and activity of a specific team role",
        "parameters": {
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "enum": ["pm", "developer", "code_reviewer"],
                    "description": "The team role to check status for",
                },
            },
            "required": ["role"],
        },
    },
    {
        "type": "function",
        "name": "get_team_overview",
        "description": "Get an overview of all team members and their current activities",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "type": "function",
        "name": "get_current_time",
        "description": "Get the current time and date",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]


# Map function names to implementations
FUNCTION_MAP = {
    "send_to_role": send_to_role,
    "get_role_status": get_role_status,
    "get_team_overview": get_team_overview,
    "get_current_time": get_current_time,
}


# =============================================================================
# Main Demo
# =============================================================================

class ToolsDemo:
    """Demo showing speech-to-speech with function calling."""

    def __init__(self):
        self.audio_handler = AudioHandler()
        self.client: RealtimeClient = None
        self.running = True

    def on_audio(self, audio_data):
        """Handle incoming audio."""
        self.audio_handler.play_audio(audio_data)

    def on_transcript(self, text):
        """Handle transcript updates."""
        print(text, end="", flush=True)

    def on_error(self, error):
        """Handle errors."""
        print(f"\n[Error] {error.get('message', error)}")

    async def handle_function_call(self, event: dict) -> None:
        """
        Handle function call requests from the API.

        When the API wants to call a function, it sends a
        'response.function_call_arguments.done' event with the function
        name and arguments.
        """
        function_name = event.get("name")
        call_id = event.get("call_id")

        # Parse arguments
        try:
            arguments = json.loads(event.get("arguments", "{}"))
        except json.JSONDecodeError:
            arguments = {}

        print(f"\n[TOOL CALL] {function_name}({arguments})")

        # Execute the function
        if function_name in FUNCTION_MAP:
            result = FUNCTION_MAP[function_name](**arguments)
        else:
            result = {"error": f"Unknown function: {function_name}"}

        print(f"[TOOL RESULT] {result}")

        # Send result back to the API
        await self.client._send({
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result),
            },
        })

        # Trigger response generation
        await self.client._send({"type": "response.create"})

    async def event_loop(self):
        """Process events from the API."""
        async for event in self.client.events():
            if not self.running:
                break

            event_type = event.get("type", "")

            # Handle function calls
            if event_type == "response.function_call_arguments.done":
                await self.handle_function_call(event)

    async def audio_loop(self):
        """Capture and send audio."""
        while self.running:
            audio_chunk = await self.audio_handler.get_audio_chunk_async(timeout=0.05)
            if audio_chunk is not None and len(audio_chunk) > 0:
                await self.client.send_audio(audio_chunk)
            await asyncio.sleep(0.01)

    async def run(self):
        """Main entry point."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not set!")
            return

        config = SessionConfig(
            voice="alloy",
            instructions="""You are the Coordinator for an AI development team.

Your team has three members:
1. PM (Project Manager) - handles planning and coordination
2. Developer - implements features and fixes bugs
3. Code Reviewer - reviews pull requests and ensures code quality

When the user asks to:
- Send instructions to a team member: use send_to_role
- Check on a team member: use get_role_status
- Get team overview: use get_team_overview
- Ask about time: use get_current_time

Be helpful and conversational. After executing tools, summarize what you did.""",
            tools=TOOLS,
        )

        print("=" * 60)
        print("OpenAI Realtime API - Speech-to-Speech with Tools Demo")
        print("=" * 60)
        print("\nThis demo simulates the AI Teams Controller voice interface.")
        print("You can ask the AI to:")
        print("  - 'Tell the developer to start working on the login feature'")
        print("  - 'What is the PM working on?'")
        print("  - 'Give me a team status update'")
        print("  - 'What time is it?'")
        print("\nPress Ctrl+C to exit.")
        print("=" * 60 + "\n")

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
                print("Connected! Start speaking...\n")

                # Start audio
                self.audio_handler.start()

                # Run event and audio loops
                try:
                    await asyncio.gather(
                        self.event_loop(),
                        self.audio_loop(),
                    )
                except asyncio.CancelledError:
                    pass

        except Exception as e:
            print(f"\nError: {e}")
            raise
        finally:
            self.audio_handler.stop()
            print("\nGoodbye!")


async def main():
    demo = ToolsDemo()
    try:
        await demo.run()
    except KeyboardInterrupt:
        demo.running = False


if __name__ == "__main__":
    asyncio.run(main())
