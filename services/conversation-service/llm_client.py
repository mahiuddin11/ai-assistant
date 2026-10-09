import sys
import os
import time
import structlog
from openai import OpenAI, APITimeoutError as OpenAICompatTimeoutError, APIStatusError as OpenAICompatStatusError, APIError as OpenAICompatAPIError
import anthropic

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
# pyrefly: ignore [missing-import]
from config_loader import get_secret  # noqa: E402

logger = structlog.get_logger()

MOCK_LLM_RESPONSES = os.getenv("MOCK_LLM_RESPONSES", "false").lower() == "true"

MAX_RETRIES_PER_PROVIDER = 2


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


def _build_claude_provider(name: str, api_key_name: str, model: str, base_url: str | None = None) -> dict | None:
    api_key = get_secret(api_key_name, vault_path="conversation-service", default=None)
    if not api_key:
        return None
    client = anthropic.Anthropic(api_key=api_key, base_url=base_url, timeout=30.0) if base_url else anthropic.Anthropic(api_key=api_key, timeout=30.0)
    return {
        "name": name,
        "call": lambda msg, sys_prompt: _call_claude(client, model, msg, sys_prompt),
        "timeout_errors": (anthropic.APITimeoutError,),
        "status_errors": (anthropic.APIStatusError,),
        "generic_errors": (anthropic.APIError,),
    }


_PROVIDERS = [
    _build_claude_provider("tokens_bd", "TOKENS_BD_API_KEY", "google/gemini-3.7-flash", "https://tokens.bd"),
    _build_openai_compatible_provider("gemini", "GEMINI_API_KEY", "gemini-3.6-flash", "https://generativelanguage.googleapis.com/v1beta/openai/"),
    _build_openai_compatible_provider("openai", "OPENAI_API_KEY", "gpt-4o"),
    _build_openai_compatible_provider("grok", "GROK_API_KEY", "grok-4", "https://api.x.ai/v1"),
]
_ACTIVE_PROVIDERS = [p for p in _PROVIDERS if p is not None]

if not _ACTIVE_PROVIDERS:
    raise RuntimeError("No LLM provider API keys found in Vault — at least one is required")

logger.info("llm_providers_active", providers=[p["name"] for p in _ACTIVE_PROVIDERS])


def _call_provider_with_retry(provider: dict, user_message: str, system_prompt: str) -> str:
    last_error = None
    for attempt in range(1, MAX_RETRIES_PER_PROVIDER + 1):
        try:
            result = provider["call"](user_message, system_prompt)
            logger.info("llm_call_success", provider=provider["name"], attempt=attempt)
            return result

        except provider["timeout_errors"] as e:
            last_error = e
            logger.warning("llm_call_timeout", provider=provider["name"], attempt=attempt, error=str(e))
        except provider["status_errors"] as e:
            last_error = e
            logger.warning("llm_call_error", provider=provider["name"], attempt=attempt, error=str(e), status_code=getattr(e, "status_code", None))
        except provider["generic_errors"] as e:
            last_error = e
            logger.warning("llm_call_api_error", provider=provider["name"], attempt=attempt, error=str(e))

        if attempt < MAX_RETRIES_PER_PROVIDER:
            time.sleep(2 ** attempt)

    raise RuntimeError(f"{provider['name']} failed after {MAX_RETRIES_PER_PROVIDER} attempts: {last_error}")


def _call_offline_fallback(user_message: str, system_prompt: str = "") -> str:
    """Local intent & rule-based offline engine for network disconnect fallback."""
    msg_lower = user_message.lower().strip()
    
    # Greetings
    if any(k in msg_lower for k in ["hello", "hi", "hey", "সালাম", "assalamualaikum", "কেমন আছো", "how are you"]):
        if any(k in msg_lower for k in ["সালাম", "assalamualaikum"]):
            return "ওয়ালাইকুম আসসালাম! আমি আপনার লোকাল অফলাইন অ্যাসিস্ট্যান্ট। কীভাবে সাহায্য করতে পারি?"
        if any(k in msg_lower for k in ["কেমন আছো", "how are you"]):
            return "আমি অফলাইন মোডে ভালো আছি। আপনাকে কীভাবে সাহায্য করতে পারি? (I am operating well in offline mode. How can I help?)"
        return "Hello! I am operating in offline fallback mode. How can I assist you with local tasks?"

    # Identity / Info
    if any(k in msg_lower for k in ["who are you", "what are you", "তোমার নাম কি", "তুমি কে"]):
        return "আমি Max AI Assistant। ক্লাউড সংযোগ না থাকলে আমি লোকাল অফলাইন মোডে সাধারণ প্রশ্নের উত্তর ও সিস্টেম কমান্ড পরিচালনা করতে পারি।"

    # Time / Date
    if any(k in msg_lower for k in ["time", "date", "কয়টা বাজে", "সময় কত", "আজকের তারিখ"]):
        import datetime
        now = datetime.datetime.now()
        return f"লোকাল বর্তমান সময়: {now.strftime('%I:%M %p')}, তারিখ: {now.strftime('%A, %d %B %Y')}।"

    # Basic Math
    import re
    math_match = re.search(r"(\d+)\s*([\+\-\*\/])\s*(\d+)", user_message)
    if math_match:
        try:
            n1, op, n2 = float(math_match.group(1)), math_match.group(2), float(math_match.group(3))
            res = n1 + n2 if op == "+" else n1 - n2 if op == "-" else n1 * n2 if op == "*" else n1 / n2 if n2 != 0 else "Error: Division by zero"
            return f"গণনা ফলাফল: {math_match.group(0)} = {res}"
        except Exception:
            pass

    # Status / Help
    if any(k in msg_lower for k in ["status", "help", "offline", "সাহায্য"]):
        return "অফলাইন ফলব্যাক স্ট্যাটাস: সিস্টেম সক্রিয়। অফলাইন মোডে সাধারণ প্রশ্ন, সময়, হিসাব এবং লোকাল ভয়েস কমান্ড সমর্থিত।"

    return f"[Offline Fallback] ইন্টারনেট/ক্লাউড এআই সংযোগ বিচ্ছিন্ন হওয়ায় লোকাল ইঞ্জিনের মাধ্যমে রেসপন্স প্রদান করা হচ্ছে। আপনার বার্তা: \"{user_message}\"।"


def _build_offline_fallback_provider() -> dict:
    return {
        "name": "local_offline",
        "call": lambda msg, sys_prompt: _call_offline_fallback(msg, sys_prompt),
        "timeout_errors": (),
        "status_errors": (),
        "generic_errors": (),
    }


def send_message(user_message: str, system_prompt: str = "You are a helpful AI assistant.") -> dict:
    if MOCK_LLM_RESPONSES:
        logger.info("llm_call_mocked", provider="mock")
        return {
            "reply": f"[MOCK RESPONSE] This is a simulated reply to: {user_message[:50]}...",
            "provider_used": "mock",
        }

    errors = {}

    for provider in _ACTIVE_PROVIDERS:
        try:
            reply = _call_provider_with_retry(provider, user_message, system_prompt)
            return {"reply": reply, "provider_used": provider["name"]}
        except RuntimeError as e:
            errors[provider["name"]] = str(e)
            logger.warning("provider_failed_trying_next", provider=provider["name"])

    logger.warning("all_cloud_llm_providers_failed_activating_offline_fallback", errors=errors)
    # Activate Local Offline Fallback Engine
    offline_reply = _call_offline_fallback(user_message, system_prompt)
    return {
        "reply": offline_reply,
        "provider_used": "local_offline",
        "offline_fallback_active": True,
        "upstream_errors": errors,
    }