"""
GLM-4-Voice API Demo: Using Zhipu AI Cloud API

This demo shows how to use GLM models via Zhipu AI's cloud API.
Note: The real-time voice API documentation requires login to access.

For text-based API (which is well documented), this demo shows integration.

Usage:
    export ZHIPU_API_KEY=your_api_key
    python demo_zhipu_api.py
"""

import os
import sys

# Check for API key
API_KEY = os.environ.get("ZHIPU_API_KEY")

if not API_KEY:
    print("=" * 60)
    print("Zhipu AI API Demo")
    print("=" * 60)
    print()
    print("ZHIPU_API_KEY not set.")
    print()
    print("To get an API key:")
    print("1. Sign up at https://open.bigmodel.cn (Chinese)")
    print("   or https://z.ai (International)")
    print("2. Navigate to API Keys section")
    print("3. Generate a new API key")
    print("4. Export: export ZHIPU_API_KEY=your_key")
    print()
    print("Note: GLM-Realtime (voice) API details are not publicly")
    print("documented. This demo shows text API usage.")
    sys.exit(0)


def demo_text_completion():
    """Demo GLM text completion via API."""
    import requests
    import json

    print("Testing GLM-4 text completion...")

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "glm-4",
        "messages": [
            {
                "role": "user",
                "content": "Hello! Can you tell me about yourself?"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        print("\nResponse:")
        print("-" * 40)
        print(content)
        print("-" * 40)

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")


def demo_langchain_integration():
    """Demo using GLM via LangChain."""
    try:
        from langchain_community.chat_models import ChatZhipuAI
        from langchain_core.messages import HumanMessage

        print("\nTesting GLM via LangChain...")

        chat = ChatZhipuAI(
            model="glm-4",
            temperature=0.7,
            api_key=API_KEY,
        )

        messages = [
            HumanMessage(content="What languages do you support?")
        ]

        response = chat.invoke(messages)

        print("\nLangChain Response:")
        print("-" * 40)
        print(response.content)
        print("-" * 40)

    except ImportError:
        print("\nLangChain not installed. Install with:")
        print("  pip install langchain-community")


def show_voice_api_info():
    """Show information about GLM voice API."""
    print("\n" + "=" * 60)
    print("GLM-Realtime Voice API Information")
    print("=" * 60)
    print()
    print("The GLM-Realtime voice API documentation is available at:")
    print("  https://open.bigmodel.cn/dev/api/rtav/GLM-Realtime")
    print()
    print("However, detailed documentation requires login and is not")
    print("publicly accessible.")
    print()
    print("What we know:")
    print("  - Supports Chinese and English voice")
    print("  - Real-time streaming capability")
    print("  - Integrated in Samsung Galaxy S25")
    print()
    print("For voice features, consider:")
    print("  1. Self-hosted GLM-4-Voice (requires GPU)")
    print("  2. Contact Zhipu AI for enterprise access")
    print("  3. Use Soniox/GPT Realtime for Vietnamese support")
    print()


def main():
    print("=" * 60)
    print("Zhipu AI (GLM) API Demo")
    print("=" * 60)

    # Demo text API
    demo_text_completion()

    # Demo LangChain
    demo_langchain_integration()

    # Voice API info
    show_voice_api_info()


if __name__ == "__main__":
    main()
