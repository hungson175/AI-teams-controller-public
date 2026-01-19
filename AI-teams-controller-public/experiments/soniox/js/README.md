# Soniox JavaScript Demo

Browser-based demo for testing Soniox real-time transcription.

## Usage

1. Open `index.html` in your browser (Chrome recommended)
2. Enter your Soniox API key
3. Select detection mode:
   - **5s Silence**: Command finalized after 5 seconds of silence
   - **Stop Word**: Command finalized when you say "go go go"
4. Click "Start Recording" and speak

## Features

- Real-time transcription display (final + interim)
- Audio level meter
- Configurable silence duration
- Configurable stop word
- Debug log for troubleshooting

## Requirements

- Modern browser with WebSocket and getUserMedia support
- Soniox API key (get one at https://console.soniox.com)
- HTTPS or localhost (required for microphone access)

## Running Locally

Simply open `index.html` in your browser. No server required.

For testing on other devices, you can use a simple HTTP server:

```bash
# Python 3
python -m http.server 8000

# Then open: http://localhost:8000/index.html
```

## Notes

- Audio is captured at 16kHz mono (Soniox requirement)
- Stop word detection is case-insensitive and ignores punctuation
- API key is saved to localStorage for convenience
