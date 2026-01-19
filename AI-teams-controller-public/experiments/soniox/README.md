# Soniox Speech-to-Text Experiments

This directory contains demo code for evaluating Soniox as an alternative to GPT Realtime API for voice commands.

## Setup

1. Get your API key from https://console.soniox.com (free tier available)

2. Set environment variable:
   ```bash
   export SONIOX_API_KEY=your_api_key
   ```

3. Install dependencies:
   ```bash
   cd experiments/soniox
   pip install -r requirements.txt

   # For microphone demos on Mac:
   brew install portaudio
   pip install pyaudio
   ```

## Demo Scripts

### 1. File Transcription (demo_file_transcription.py)
Transcribe a short audio file (< 60 seconds).

```bash
python demo_file_transcription.py path/to/audio.mp3

# With specific model
python demo_file_transcription.py audio.mp3 vi  # Vietnamese model
```

### 2. Real-time Microphone (demo_realtime_microphone.py)
Continuous real-time transcription from microphone.

```bash
python demo_realtime_microphone.py

# With specific model
python demo_realtime_microphone.py soniox_enhanced
```

Press Ctrl+C to stop.

### 3. Voice Command with Silence Detection (demo_realtime_with_silence.py)
Mimics the AI Controller voice command flow with 5-second silence auto-send.

```bash
python demo_realtime_with_silence.py
```

This demo:
- Starts recording from microphone
- Streams to Soniox for real-time transcription
- Detects 5 seconds of silence to auto-finalize
- Shows countdown before auto-send

## Available Models

| Model | Description |
|-------|-------------|
| `soniox_enhanced` | Best accuracy, 60+ languages (default) |
| `en_v2` | English optimized |
| `vi` | Vietnamese |

## Research Document

See `SONIOX_RESEARCH.md` for detailed comparison with GPT Realtime API including:
- Accuracy benchmarks (Vietnamese: 5.4% WER)
- Cost comparison ($0.12/hr vs $0.38/hr)
- Feature comparison
- Migration considerations

## Cost Comparison

| Provider | Cost/Hour |
|----------|-----------|
| Soniox | $0.10-0.12 |
| OpenAI Realtime | ~$0.38 |

Potential savings: ~70%
