"""
GLM-4-Voice Demo: End-to-End Voice Conversation

This demo shows how to use GLM-4-Voice for voice conversations.
Note: GLM-4-Voice is an end-to-end model (not STT), it takes audio in
and produces audio out with language understanding in between.

IMPORTANT:
- Requires Python 3.10 (NOT 3.8/3.9/3.12)
- Requires GPU with 12GB+ VRAM (INT4) or 20GB+ VRAM (BFloat16)
- Only supports Chinese and English (NO Vietnamese)

Usage:
    # First, download models
    huggingface-cli download THUDM/glm-4-voice-tokenizer
    huggingface-cli download THUDM/glm-4-voice-9b
    huggingface-cli download THUDM/glm-4-voice-decoder

    # Run demo
    python demo_glm_voice.py --audio input.wav
"""

import argparse
import sys
import os

# Check Python version
if sys.version_info[:2] != (3, 10):
    print(f"Error: GLM-4-Voice requires Python 3.10")
    print(f"Current version: {sys.version}")
    print("Create conda environment: conda create -n GLM-4-Voice python=3.10")
    sys.exit(1)


def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []

    try:
        import torch
        if not torch.cuda.is_available():
            print("Warning: CUDA not available. GLM-4-Voice requires GPU.")
    except ImportError:
        missing.append("torch")

    try:
        import transformers
    except ImportError:
        missing.append("transformers")

    try:
        import soundfile
    except ImportError:
        missing.append("soundfile")

    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        sys.exit(1)


def check_models_downloaded():
    """Check if GLM-4-Voice models are downloaded."""
    from huggingface_hub import hf_hub_download, HfFolder

    models = [
        "THUDM/glm-4-voice-tokenizer",
        "THUDM/glm-4-voice-9b",
    ]

    print("Checking model availability...")

    for model in models:
        try:
            # This will check if model exists locally or can be accessed
            from huggingface_hub import model_info
            info = model_info(model)
            print(f"  ✓ {model}")
        except Exception as e:
            print(f"  ✗ {model} - {e}")
            print(f"\nDownload with: huggingface-cli download {model}")
            return False

    return True


def load_model(model_path: str, dtype: str = "int4", device: str = "cuda:0"):
    """
    Load GLM-4-Voice model.

    Args:
        model_path: HuggingFace model path (e.g., "THUDM/glm-4-voice-9b")
        dtype: "bfloat16" (20GB VRAM) or "int4" (12GB VRAM)
        device: CUDA device

    Returns:
        Loaded model and tokenizer
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"Loading model: {model_path}")
    print(f"Dtype: {dtype}, Device: {device}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        "THUDM/glm-4-voice-tokenizer",
        trust_remote_code=True
    )

    # Load model with appropriate precision
    if dtype == "int4":
        from transformers import BitsAndBytesConfig

        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=quantization_config,
            device_map=device,
            trust_remote_code=True
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map=device,
            trust_remote_code=True
        )

    print("Model loaded successfully!")
    return model, tokenizer


def transcribe_audio(audio_path: str, tokenizer):
    """
    Convert audio to tokens using GLM-4-Voice tokenizer.

    Note: This is NOT traditional STT - it creates discrete tokens
    that the GLM model understands directly.
    """
    import soundfile as sf

    print(f"Loading audio: {audio_path}")

    # Load audio
    audio, sample_rate = sf.read(audio_path)

    # Resample to 16kHz if needed
    if sample_rate != 16000:
        import librosa
        audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)

    # Tokenize audio
    # Note: The actual tokenization process depends on the specific
    # GLM-4-Voice-Tokenizer implementation
    print(f"Audio duration: {len(audio) / 16000:.2f}s")

    return audio


def run_conversation(model, tokenizer, audio_tokens, prompt: str = None):
    """
    Run voice conversation with GLM-4-Voice.

    Args:
        model: Loaded GLM model
        tokenizer: Loaded tokenizer
        audio_tokens: Tokenized audio input
        prompt: Optional text prompt to guide the response

    Returns:
        Generated audio response
    """
    import torch

    # Build input
    if prompt:
        text_input = f"<|user|>\n{prompt}\n<|assistant|>\n"
    else:
        text_input = "<|user|>\n<|assistant|>\n"

    # Note: The actual inference process depends on the specific
    # GLM-4-Voice implementation which combines audio and text tokens

    print("Running inference...")
    print("(This is a simplified demo - see official repo for full implementation)")

    # In the actual implementation, you would:
    # 1. Combine audio tokens with text tokens
    # 2. Run through the GLM-4-Voice-9B model
    # 3. Decode output tokens through GLM-4-Voice-Decoder to audio

    return None


def main():
    parser = argparse.ArgumentParser(description="GLM-4-Voice Demo")
    parser.add_argument("--audio", type=str, help="Input audio file path")
    parser.add_argument("--prompt", type=str, default=None, help="Optional text prompt")
    parser.add_argument("--dtype", type=str, default="int4", choices=["int4", "bfloat16"])
    parser.add_argument("--device", type=str, default="cuda:0")
    parser.add_argument("--check-only", action="store_true", help="Only check setup")

    args = parser.parse_args()

    print("=" * 60)
    print("GLM-4-Voice Demo")
    print("=" * 60)
    print()
    print("Note: GLM-4-Voice only supports Chinese and English.")
    print("For Vietnamese, use Soniox instead (experiments/soniox/)")
    print()

    # Check dependencies
    check_dependencies()

    # Check models
    if not check_models_downloaded():
        print("\nPlease download the models first.")
        sys.exit(1)

    if args.check_only:
        print("\nSetup check complete!")
        sys.exit(0)

    if not args.audio:
        print("\nNo audio file provided. Use --audio to specify input.")
        print("\nExample usage:")
        print("  python demo_glm_voice.py --audio input.wav")
        print("  python demo_glm_voice.py --audio input.wav --prompt 'Translate this to Chinese'")
        sys.exit(0)

    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        sys.exit(1)

    # Load model
    model, tokenizer = load_model(
        "THUDM/glm-4-voice-9b",
        dtype=args.dtype,
        device=args.device
    )

    # Process audio
    audio = transcribe_audio(args.audio, tokenizer)

    # Run conversation
    response = run_conversation(model, tokenizer, audio, args.prompt)

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
    print("\nFor full voice conversation demo, run the official web demo:")
    print("  python web_demo.py --tokenizer-path THUDM/glm-4-voice-tokenizer \\")
    print("                     --model-path THUDM/glm-4-voice-9b \\")
    print("                     --flow-path ./glm-4-voice-decoder")


if __name__ == "__main__":
    main()
