import sys
import os
import json
import asyncio
import structlog
import nats

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
from config_loader import get_secret  # noqa: E402

logger = structlog.get_logger()

NATS_URL = get_secret("NATS_URL", vault_path="conversation-service", default="nats://localhost:4222")


async def _publish_async(subject: str, payload: dict) -> None:
    try:
        nc = await nats.connect(NATS_URL)
        await nc.publish(subject, json.dumps(payload).encode())
        await nc.flush()
        await nc.close()
        logger.info("event_published", subject=subject)
    except Exception as e:
        # ইভেন্ট পাঠাতে ব্যর্থ হলেও মূল task operation ব্যর্থ হওয়া উচিত না,
        # তাই এখানে শুধু warning — exception raise করা হচ্ছে না
        logger.warning("event_publish_failed", subject=subject, error=str(e))


def publish_task_event(event_type: str, task_id: str, status: str) -> None:
    """
    event_type: "created" | "updated" | "completed"
    Sync ফাংশন থেকে async NATS কল চালানোর জন্য।
    """
    subject = f"task.{event_type}"
    payload = {"task_id": task_id, "status": status}

    try:
        asyncio.run(_publish_async(subject, payload))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.create_task(_publish_async(subject, payload))