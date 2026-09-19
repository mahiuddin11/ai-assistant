import sys
import os
import time
import structlog
from openai import OpenAI, APITimeoutError as OpenAICompatTimeoutError, APIStatusError as OpenAICompatStatusError, APIError as OpenAICompatAPIError
import anthropic

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
from config_loader import get_secret  # noqa: E402

logger = structlog.get_logger()

MAX_RETRIES_PER_PROVIDER = 2


# ---------------------------------------------------------
# প্রতিটা provider-এর নিজস্ব "call" ফাংশন — ভিন্ন SDK/ফরম্যাট থাকলেও
# বাইরে থেকে একই সিগনেচারে (user_message, system_prompt) -> text স্ট্রিং রিটার্ন করে
# ---------------------------------------------------------

def _call_openai_compatible(client, model: str, user_message: str, system_prompt: str) -> str:
    response = client.chat.completions.create(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def _call_claude(client, model: str, user_message: str, system_prompt: str) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


# ---------------------------------------------------------
# Provider রেজিস্ট্রি বিল্ডার — API key Vault-এ না থাকলে None রিটার্ন করে (চুপচাপ স্কিপ হয়)
# ---------------------------------------------------------

def _build_openai_compatible_provider(name: str, api_key_name: str, model: str, base_url: str | None = None) -> dict | None:
    api_key = get_secret(api_key_name, vault_path="conversation-service", default=None)
    if not api_key:
        return None
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=30.0) if base_url else OpenAI(api_key=api_key, timeout=30.0)
    return {
        "name": name,
        "call": lambda msg, sys_prompt: _call_openai_compatible(client, model, msg, sys_prompt),
        "timeout_errors": (OpenAICompatTimeoutError,),
        "status_errors": (OpenAICompatStatusError,),
        "generic_errors": (OpenAICompatAPIError,),
    }


def _build_claude_provider(name: str, api_key_name: str, model: str) -> dict | None:
    api_key = get_secret(api_key_name, vault_path="conversation-service", default=None)
    if not api_key:
        return None
    client = anthropic.Anthropic(api_key=api_key, timeout=30.0)
    return {
        "name": name,
        "call": lambda msg, sys_prompt: _call_claude(client, model, msg, sys_prompt),
        "timeout_errors": (anthropic.APITimeoutError,),
        "status_errors": (anthropic.APIStatusError,),
        "generic_errors": (anthropic.APIError,),
    }


# ---------------------------------------------------------
# অগ্রাধিকার ক্রম: Gemini → Claude → OpenAI → Grok
# নতুন provider যোগ করতে শুধু এখানে একটা লাইন যোগ করুন — বাকি কোড অপরিবর্তিত থাকবে
# ---------------------------------------------------------
_PROVIDERS = [
    _build_openai_compatible_provider("gemini", "GEMINI_API_KEY", "gemini-3.6-flash", "https://generativelanguage.googleapis.com/v1beta/openai/"),
    _build_claude_provider("claude", "ANTHROPIC_API_KEY", "claude-sonnet-4-5"),
    _build_openai_compatible_provider("openai", "OPENAI_API_KEY", "gpt-4o"),
    _build_openai_compatible_provider("grok", "GROK_API_KEY", "grok-4", "https://api.x.ai/v1"),
]
_ACTIVE_PROVIDERS = [p for p in _PROVIDERS if p is not None]

if not _ACTIVE_PROVIDERS:
    raise RuntimeError("No LLM provider API keys found in Vault — at least one is required")

logger.info("llm_providers_active", providers=[p["name"] for p in _ACTIVE_PROVIDERS])


# ---------------------------------------------------------
# একটা provider-কে retry সহ কল করা
# ---------------------------------------------------------

def _call_provider_with_retry(provider: dict, user_message: str, system_prompt: str) -> str:
    last_error = None
    for attempt in range(1, MAX_RETRIES_PER_PROVIDER + 1):
        try:
            result = provider["call"](user_message, system_prompt)
            logger.info("llm_call_success", provider=provider["name"], attempt=attempt)
            return result

        except provider["timeout_errors"] as e:
            last_error = e
            logger.warning("llm_call_timeout", provider=provider["name"], attempt=attempt)
        except provider["status_errors"] as e:
            last_error = e
            logger.warning("llm_call_error", provider=provider["name"], attempt=attempt)
        except provider["generic_errors"] as e:
            last_error = e
            logger.warning("llm_call_api_error", provider=provider["name"], attempt=attempt, error=str(e))

        if attempt < MAX_RETRIES_PER_PROVIDER:
            time.sleep(2 ** attempt)

    raise RuntimeError(f"{provider['name']} failed after {MAX_RETRIES_PER_PROVIDER} attempts: {last_error}")


# ---------------------------------------------------------
# পাবলিক ফাংশন — _ACTIVE_PROVIDERS-এর ক্রম অনুযায়ী একটা একটা করে ট্রাই করে
# ---------------------------------------------------------

def send_message(user_message: str, system_prompt: str = "You are a helpful AI assistant.") -> dict:
    errors = {}

    for provider in _ACTIVE_PROVIDERS:
        try:
            reply = _call_provider_with_retry(provider, user_message, system_prompt)
            return {"reply": reply, "provider_used": provider["name"]}
        except RuntimeError as e:
            errors[provider["name"]] = str(e)
            logger.warning("provider_failed_trying_next", provider=provider["name"])

    logger.error("all_llm_providers_failed", errors=errors)
    raise RuntimeError(f"All LLM providers failed: {errors}")