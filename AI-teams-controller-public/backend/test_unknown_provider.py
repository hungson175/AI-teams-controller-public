#!/usr/bin/env python3
"""Manual test for AC5: Unknown TTS provider error handling."""

import os
import sys

# Set unknown provider
os.environ["TTS_PROVIDER"] = "unknown"

try:
    from app.services.voice_feedback.audio import generate_tts
    
    print("[TEST] Calling generate_tts with TTS_PROVIDER=unknown")
    result = generate_tts("Test message")
    
    print(f"[ERROR] Should have raised ValueError but got result: '{result}'")
    sys.exit(1)
    
except ValueError as e:
    print(f"[SUCCESS] ValueError raised as expected: {e}")
    sys.exit(0)
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    sys.exit(1)
