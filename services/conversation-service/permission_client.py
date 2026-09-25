import os
import structlog
import httpx

logger = structlog.get_logger()

# dev-এ auth-service লোকালি port 8001-এ চলে; ভবিষ্যতে service-discovery/K8s DNS দিয়ে বদলানো হবে
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")


def is_tool_permission_granted(user_id: str, tool_name: str) -> bool:
    """
    auth-service-কে জিজ্ঞেস করে এই user-এর এই tool ব্যবহারের অনুমতি আছে কিনা।
    auth-service unreachable হলে (network issue) নিরাপদ দিক থেকে ভুল করে —
    অর্থাৎ fail-closed (deny), fail-open (allow) না — সিকিউরিটির জন্য।
    """
    try:
        response = httpx.get(
            f"{AUTH_SERVICE_URL}/v1/permissions/check",
            params={"user_id": user_id, "tool_name": tool_name},
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json().get("allowed", False)

    except httpx.HTTPError as e:
        logger.error("permission_check_failed_fail_closed", user_id=user_id, tool_name=tool_name, error=str(e))
        return False  # fail-closed — auth-service ডাউন থাকলে টুল ব্যবহারের অনুমতি দেওয়া হবে না