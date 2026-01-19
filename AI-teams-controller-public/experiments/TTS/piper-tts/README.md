# Piper TTS Demo - Open-Source & Free

**Cost: $0 (completely free!)**

## Overview

Piper is a fast, local, open-source text-to-speech system that:
- Runs on **CPU-only** (no GPU required)
- Works **offline** (no internet needed)
- **100% free** (no API costs ever)
- **Privacy-friendly** (all processing is local)

Perfect for testing, low-volume apps, or privacy-sensitive use cases.

## Setup

### Option 1: Install via pip (Recommended)

```bash
pip install piper-tts
```

### Option 2: Docker

```bash
docker pull rhasspy/piper
```

### Option 3: Manual Build

```bash
git clone https://github.com/rhasspy/piper
cd piper
# Follow build instructions in README
```

## Quick Start

### Using pip

```bash
# Download voice model (one-time, ~20MB)
piper --model en_US-lessac-medium --download-dir ~/.local/share/piper/models

# Generate speech
echo "Hello, this is Piper TTS" | piper --model en_US-lessac-medium --output_file output.wav
```

### Using Docker

```bash
echo "Hello from Docker" | docker run -i rhasspy/piper \
  --model en_US-lessac-medium > output.wav
```

## Run Demo

```bash
python demo.py
```

This will:
1. Install Piper if needed
2. Download voice model (~20MB, one-time)
3. Generate `output_piper.wav`
4. Show cost comparison with commercial APIs

## Available Voice Models

### English (US)
- `en_US-lessac-medium` - Female, clear (recommended)
- `en_US-libritts-high` - Various speakers, high quality
- `en_US-ryan-high` - Male, expressive
- `en_US-amy-medium` - Female, neutral

### English (UK)
- `en_GB-alan-medium` - Male, British
- `en_GB-alba-medium` - Female, Scottish

### Other Languages
- German: `de_DE-thorsten-medium`
- Spanish: `es_ES-sharvard-medium`
- French: `fr_FR-upmc-medium`
- Vietnamese: Check [Piper models](https://github.com/rhasspy/piper/blob/master/VOICES.md)

Full list: [Piper Voice Models](https://github.com/rhasspy/piper/blob/master/VOICES.md)

## Cost Comparison (for 1M characters)

| Provider | Cost |
|----------|------|
| **Piper TTS** | **$0** |
| Google Standard | $4 |
| OpenAI | $15 |
| ElevenLabs | $165 |

## Pros & Cons

### ✅ Advantages
- **Free** - No API costs, ever
- **Fast** - Optimized for real-time synthesis
- **Offline** - Works without internet
- **Privacy** - All processing is local
- **Lightweight** - Runs on CPU (no GPU needed)
- **Open-source** - MIT license

### ⚠️ Trade-offs
- Lower quality than commercial APIs
- Fewer voice options (but growing)
- Manual setup required
- No cloud infrastructure benefits

## Use Cases

**Best for:**
- Testing and experimentation
- Low-volume applications
- Privacy-sensitive use cases
- Offline/edge deployment
- Budget-constrained projects
- Learning and prototyping

**Not ideal for:**
- High-quality commercial applications
- Large-scale production (consider Google Cloud at $4/million)
- When you need the absolute best voice quality

## Hardware Requirements

- **CPU**: Any modern CPU (no GPU required)
- **RAM**: 2-4GB
- **Storage**: ~50-100MB per voice model
- **Power**: <10W

Can run on:
- Raspberry Pi 4
- Low-end VPS
- Edge devices
- IoT devices

## Integration Example

```python
import subprocess

def generate_speech(text: str, output_file: str):
    """Generate speech using Piper."""
    process = subprocess.Popen(
        ["piper", "--model", "en_US-lessac-medium", "--output_file", output_file],
        stdin=subprocess.PIPE,
        text=True
    )
    process.communicate(input=text)
```

## Performance

- **Speed**: Real-time or faster (depends on CPU)
- **Latency**: Low (local processing)
- **Throughput**: Limited by CPU, but very efficient

Benchmark: Generate 1000 chars in ~2-5 seconds on modern CPU.

## Deployment Options

### Local Development
```bash
pip install piper-tts
piper --model en_US-lessac-medium ...
```

### Docker Container
```bash
docker run -v $(pwd):/data rhasspy/piper \
  --model en_US-lessac-medium \
  --output_file /data/output.wav < input.txt
```

### Systemd Service (Linux)
```ini
[Unit]
Description=Piper TTS Service

[Service]
ExecStart=/usr/local/bin/piper --model en_US-lessac-medium
Restart=always

[Install]
WantedBy=multi-user.target
```

## Documentation

- [Piper GitHub](https://github.com/rhasspy/piper)
- [Voice Models List](https://github.com/rhasspy/piper/blob/master/VOICES.md)
- [Docker Hub](https://hub.docker.com/r/rhasspy/piper)

## Recommendation

**Start with Piper for:**
1. Initial testing (zero cost)
2. Proof of concept
3. Understanding your actual TTS volume

**Then migrate to:**
- Google Cloud Standard ($4/million) for production with decent quality
- Google Neural2 ($16/million) if you need premium quality
- Keep Piper for offline/edge use cases

This phased approach minimizes risk and cost!
