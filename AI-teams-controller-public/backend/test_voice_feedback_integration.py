"""Test full voice feedback integration with Google Cloud TTS"""
import requests
import os
import time
import json

# Backend URL
BACKEND_URL = "http://localhost:17061"
API_TOKEN = os.environ.get("API_TOKEN", "zIpz2QeOvTOEsfxzETN7sTEgQfw7uwuIpgxza_fNVcA")

headers = {"Authorization": f"Bearer {API_TOKEN}"}

print("🧪 Testing Voice Feedback Integration with Google Cloud TTS\n")

# Step 1: Test task-done endpoint (triggers Celery task)
print("1. Triggering voice feedback task...")
payload = {
    "pane_output": "Done. Successfully completed the test task. All systems working.",
    "original_command": "test google cloud tts integration"
}

try:
    response = requests.post(
        f"{BACKEND_URL}/api/voice/task-done/test_team/0",
        json=payload,
        headers=headers,
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code == 202:
        print("   ✓ Task queued successfully")
    else:
        print(f"   ✗ Unexpected status code: {response.status_code}")
        exit(1)
        
except Exception as e:
    print(f"   ✗ Request failed: {e}")
    exit(1)

# Step 2: Wait for Celery to process
print("\n2. Waiting for Celery to process (5 seconds)...")
time.sleep(5)

# Step 3: Check Celery logs for Google Cloud TTS usage
print("\n3. Checking Celery logs for TTS provider...")
import subprocess
result = subprocess.run(
    ["tail", "-50", "/tmp/ai-teams-celery.err"],
    capture_output=True,
    text=True
)

logs = result.stdout
if "Google Cloud generating speech" in logs or "Google provider" in logs:
    print("   ✓ Google Cloud TTS is being used!")
elif "OpenAI" in logs:
    print("   ✗ OpenAI TTS is being used instead of Google Cloud")
    print("   Check TTS_PROVIDER env var in .env")
    exit(1)
else:
    print("   ⚠ Could not confirm TTS provider from logs")
    print("   Recent logs:")
    print("   " + "\n   ".join(logs.split("\n")[-10:]))

print("\n✅ Integration test completed!")
print("\nTo verify audio playback:")
print("1. Open https://voice-ui.hungson175.com")
print("2. Trigger a voice command")
print("3. Check notification panel for voice feedback")
print("4. Listen to audio - should be Google Cloud TTS voice")

