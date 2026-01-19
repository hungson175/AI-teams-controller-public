# GLM-4-Voice Experiments

This directory contains demo code for GLM-4-Voice, an open-source end-to-end speech model from Zhipu AI.

## Important Note

**GLM-4-Voice does NOT support Vietnamese.** It only supports Chinese and English.

This makes it unsuitable for our AI Controller voice command use case which requires Vietnamese support. The demo code here is for **educational purposes** to understand how GLM-4-Voice works.

For Vietnamese STT, see `experiments/soniox/` instead.

## What is GLM-4-Voice?

Unlike traditional STT APIs (Whisper, Soniox), GLM-4-Voice is an **end-to-end voice LLM**:
- Input: Speech audio
- Output: Speech audio (with understanding in between)
- No separate STT→LLM→TTS pipeline

## Requirements

### Hardware
- GPU with 12GB+ VRAM (INT4 quantized)
- Or 20GB+ VRAM (BFloat16)

### Software
- Python 3.10 (NOT 3.8/3.9/3.12)
- CUDA support
- ~10GB for model downloads

## Setup

```bash
# Create conda environment
conda create -n GLM-4-Voice python=3.10
conda activate GLM-4-Voice

# Clone repository
git clone https://github.com/THUDM/GLM-4-Voice
cd GLM-4-Voice

# Install dependencies
pip install -r requirements.txt
```

## Demo Scripts

### 1. Official Web Demo (Requires GPU)

```bash
# Download models first
huggingface-cli download THUDM/glm-4-voice-tokenizer
huggingface-cli download THUDM/glm-4-voice-9b
huggingface-cli download THUDM/glm-4-voice-decoder

# Run web demo
python web_demo.py \
  --tokenizer-path THUDM/glm-4-voice-tokenizer \
  --model-path THUDM/glm-4-voice-9b \
  --flow-path ./glm-4-voice-decoder

# Access at http://127.0.0.1:8888
```

### 2. Simplified Demo (demo_glm_voice.py)

See `demo_glm_voice.py` for a simplified example of how to use GLM-4-Voice programmatically.

## Comparison with Other Options

| Feature | GLM-4-Voice | Soniox | GPT Realtime |
|---------|-------------|--------|--------------|
| Vietnamese | ❌ | ✅ | ✅ |
| English | ✅ | ✅ | ✅ |
| Chinese | ✅ | ✅ | ✅ |
| Self-hosted | ✅ | ❌ | ❌ |
| Pure STT | ❌ | ✅ | ✅ |
| Cost | Free (GPU) | $0.12/hr | $0.38/hr |

## When to Use GLM-4-Voice

✅ Good for:
- Chinese voice assistants
- Need emotion/tone control
- Self-hosting requirement
- Full voice AI (not just STT)

❌ Not good for:
- Vietnamese support needed
- Just need transcription (use Soniox/Whisper)
- No GPU available

## Research Document

See `GLM_VOICE_RESEARCH.md` for detailed research including:
- Architecture details
- Cost comparison
- Feature comparison with GPT Realtime API
- Limitations analysis
