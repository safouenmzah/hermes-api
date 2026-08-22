"""
Test client for Hermes Agent API
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

def health_check():
    """Check API health"""
    print("🔍 Health check...")
    resp = requests.get(f"{BASE_URL}/health")
    print(json.dumps(resp.json(), indent=2))
    return resp.status_code == 200

def chat(message: str, config: Optional[dict] = None, conv_id: Optional[str] = None):
    """Send a chat message"""
    payload = {
        "message": message,
        "conversation_id": conv_id,
        "config": config
    }
    print(f"\n💬 Sending: {message}")
    resp = requests.post(f"{BASE_URL}/chat", json=payload)
    result = resp.json()
    print(f"✓ Response from {result['model']}:")
    print(f"  {result['response']}\n")
    return result.get("conversation_id")

def get_config():
    """Get current config"""
    print("⚙️  Current config:")
    resp = requests.get(f"{BASE_URL}/config")
    print(json.dumps(resp.json(), indent=2))

def set_config(model: str, reasoning: str, max_tokens: int):
    """Update config"""
    payload = {
        "model": model,
        "reasoning_effort": reasoning,
        "max_tokens": max_tokens
    }
    print(f"\n⚙️  Updating config: {payload}")
    resp = requests.post(f"{BASE_URL}/config", json=payload)
    print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    print("=" * 60)
    print("Hermes Agent API — Test Client")
    print("=" * 60)

    # Check health
    if not health_check():
        print("❌ API not running!")
        exit(1)

    print("\n✓ API is healthy\n")

    # Get current config
    get_config()

    # Test basic chat
    conv_id = chat("What can you help me with?")

    # Follow-up message in same conversation
    chat("Tell me more about your capabilities.", conv_id=conv_id)

    # Test with different config
    print("\n--- Testing with high reasoning ---")
    set_config("claude-opus-5", "high", 8192)
    chat("Explain how hermes agents work", config={
        "model": "claude-opus-5",
        "reasoning_effort": "high",
        "max_tokens": 8192
    })

    print("\n✓ All tests passed!")
