import sys
import os

# packages ডিরেক্টরি পাথ যুক্ত করা
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))

from llm_client import send_message, _ACTIVE_PROVIDERS

print("=" * 60)
print("1. Active LLM Providers (Priority Order):")
for idx, p in enumerate(_ACTIVE_PROVIDERS, start=1):
    print(f"   Priority {idx}: {p['name']}")
print("=" * 60)

prompt = "Hello! Tell me in 1 sentence who you are."
print(f"\n2. Sending test prompt: '{prompt}'")
print("   Connecting to 1st priority provider (tokens_bd)...\n")

try:
    result = send_message(prompt)
    print("=" * 60)
    print("3. Response Result:")
    print(f"   [Provider Used] : {result['provider_used']}")
    print(f"   [AI Reply]      : {result['reply']}")
    print("=" * 60)
except Exception as e:
    print(f"\n[ERROR] Failed to get response: {e}")
