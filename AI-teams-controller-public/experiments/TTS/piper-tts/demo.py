#!/usr/bin/env python3
"""
Piper TTS Demo - Open-Source Self-Hosted TTS
Cost: FREE (runs on CPU, no GPU required)
Quality: Decent for notifications
Speed: Fast and lightweight
"""

import os
import subprocess


def install_piper():
    """Install Piper TTS if not already installed."""
    try:
        subprocess.run(["piper", "--version"], capture_output=True, check=True)
        print("✓ Piper TTS is already installed")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Installing Piper TTS...")
        try:
            # Install via pip
            subprocess.run(
                ["pip", "install", "piper-tts"],
                check=True
            )
            print("✓ Piper TTS installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("ERROR: Failed to install Piper TTS")
            print("\nAlternative installation methods:")
            print("1. Docker: docker pull rhasspy/piper")
            print("2. Manual: https://github.com/rhasspy/piper")
            return False


def download_voice_model(language="en_US"):
    """Download a voice model if not present."""
    models_dir = os.path.expanduser("~/.local/share/piper/models")
    os.makedirs(models_dir, exist_ok=True)

    # Check if model exists
    model_file = f"{models_dir}/en_US-lessac-medium.onnx"
    if os.path.exists(model_file):
        print(f"✓ Voice model exists: {model_file}")
        return model_file

    print("Downloading voice model...")
    print("(This is a one-time download, ~20MB)")

    # Download using piper's built-in download
    try:
        subprocess.run(
            [
                "piper",
                "--model", "en_US-lessac-medium",
                "--download-dir", models_dir,
                "--update-voices"
            ],
            check=True
        )
        print(f"✓ Model downloaded to: {model_file}")
        return model_file
    except subprocess.CalledProcessError:
        print("ERROR: Failed to download voice model")
        print("\nManual download:")
        print("Visit: https://github.com/rhasspy/piper/releases")
        return None


def test_piper_tts(text: str, output_file: str = "output_piper.wav"):
    """
    Test Piper TTS.

    Args:
        text: Text to convert to speech
        output_file: Output audio file path
    """
    print("\n=== Testing Piper TTS (Open-Source, CPU-only) ===")

    if not install_piper():
        return

    model_path = download_voice_model()
    if not model_path:
        return

    print(f"\nGenerating speech from text ({len(text)} chars)...")
    print(f"Cost: $0 (completely free!)")

    try:
        # Run piper to generate audio
        process = subprocess.Popen(
            ["piper", "--model", "en_US-lessac-medium", "--output_file", output_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=text)

        if process.returncode == 0:
            print(f"✓ Audio saved to: {output_file}")
            print("\n=== Cost Comparison ===")
            print(f"OpenAI TTS: ${len(text) * 0.000015:.6f}")
            print(f"Google Standard: ${len(text) * 0.000004:.6f}")
            print(f"Piper TTS: $0.00 (FREE!)")

            print("\n=== Benefits ===")
            print("✓ Completely free (no API costs)")
            print("✓ Runs offline (no internet required)")
            print("✓ No GPU needed (CPU-only)")
            print("✓ Fast and lightweight")
            print("✓ Privacy-friendly (all local)")

            print("\n=== Trade-offs ===")
            print("⚠ Lower quality than commercial APIs")
            print("⚠ Fewer voice options")
            print("⚠ Manual setup required")

        else:
            print(f"ERROR: {stderr}")

    except Exception as e:
        print(f"ERROR: {e}")


def list_available_voices():
    """List available Piper voice models."""
    print("\n=== Popular Piper Voice Models ===")
    print("\nEnglish (US):")
    print("  en_US-lessac-medium - Female, clear (recommended)")
    print("  en_US-libritts-high - Various speakers, high quality")
    print("  en_US-ryan-high - Male, expressive")
    print("  en_US-amy-medium - Female, neutral")

    print("\nEnglish (UK):")
    print("  en_GB-alan-medium - Male, British")
    print("  en_GB-alba-medium - Female, Scottish")

    print("\nOther Languages:")
    print("  de_DE-thorsten-medium - German")
    print("  es_ES-sharvard-medium - Spanish")
    print("  fr_FR-upmc-medium - French")
    print("  vi_VN-* - Vietnamese (check https://github.com/rhasspy/piper)")

    print("\nDownload models:")
    print("  piper --model <model_name> --download-dir ~/.local/share/piper/models")


def docker_usage():
    """Show Docker usage for Piper."""
    print("\n=== Using Piper via Docker ===")
    print("\n1. Pull Docker image:")
    print("   docker pull rhasspy/piper")

    print("\n2. Run TTS:")
    print('   echo "Hello world" | docker run -i rhasspy/piper \\')
    print('     --model en_US-lessac-medium > output.wav')

    print("\n3. List available voices:")
    print("   docker run rhasspy/piper --help")


if __name__ == "__main__":
    # Test text
    test_text = """
    This is a test of Piper Text-to-Speech, an open-source alternative.
    It's completely free, runs on CPU without requiring a GPU,
    and works offline. Perfect for budget-conscious developers
    or applications requiring privacy.
    """

    test_piper_tts(test_text.strip())
    list_available_voices()
    docker_usage()

    print("\n=== Recommendation ===")
    print("Piper TTS is best for:")
    print("- Testing/experimentation (zero cost)")
    print("- Low-volume applications")
    print("- Privacy-sensitive use cases")
    print("- Offline/edge deployment")
    print("\nFor production with high quality, consider Google Cloud Standard ($4/million)")
