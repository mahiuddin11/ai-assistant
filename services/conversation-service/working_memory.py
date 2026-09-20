import sys
import os
import json
import structlog
import redis

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
# pyrefly: ignore [missing-import]
from config_loader import get_secret  # noqa: E402

logger = structlog.get_logger()

REDIS_URL = get_secret("REDIS_URL", vault_path="conversation-service", default="redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

SESSION_TTL_SECONDS = 60 * 60  # ১ ঘণ্টা নিষ্ক্রিয় থাকলে মেমোরি মুছে যাবে
MAX_MESSAGES_IN_MEMORY = 20    # প্রতিটা সেশনে সর্বোচ্চ কতগুলো মেসেজ (context window সীমিত রাখতে)


def _key(conversation_id: str) -> str:
    return f"working_memory:{conversation_id}"


def get_history(conversation_id: str) -> list[dict]:
    """
    একটা conversation-এর সাম্প্রতিক মেসেজ হিস্ট্রি রিটার্ন করে।
    কিছু না থাকলে খালি লিস্ট রিটার্ন করে (নতুন conversation)।
    """
    raw = redis_client.get(_key(conversation_id))
    if raw is None:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("working_memory_corrupt", conversation_id=conversation_id)
        return []


def append_message(conversation_id: str, role: str, content: str) -> None:
    """
    একটা নতুন মেসেজ (user বা assistant) working memory-তে যোগ করে,
    এবং TTL রিফ্রেশ করে (সেশন এখনো সক্রিয় বলে ধরে নেওয়া হয়)।
    """
    history = get_history(conversation_id)
    history.append({"role": role, "content": content})

    # সর্বোচ্চ সীমার বেশি হলে পুরনো মেসেজ ছেঁটে ফেলা (FIFO)
    if len(history) > MAX_MESSAGES_IN_MEMORY:
        history = history[-MAX_MESSAGES_IN_MEMORY:]

    redis_client.set(_key(conversation_id), json.dumps(history), ex=SESSION_TTL_SECONDS)
    logger.info("working_memory_updated", conversation_id=conversation_id, message_count=len(history))


def clear_history(conversation_id: str) -> None:
    """একটা conversation-এর মেমোরি সম্পূর্ণ মুছে দেয় (right-to-forget সাপোর্টের জন্য)।"""
    redis_client.delete(_key(conversation_id))
    logger.info("working_memory_cleared", conversation_id=conversation_id)