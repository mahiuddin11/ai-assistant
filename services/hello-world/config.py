"""
Config loader — Vault-first, .env fallback.

Dev-এ Vault চালু না থাকলে বা ভ্যালু না পাওয়া গেলে .env থেকে পড়া হবে।
Staging/Prod-এ Vault বাধ্যতামূলক হবে (architecture.md — secrets never hardcoded).
"""

import os

import structlog
from dotenv import load_dotenv

try:
    import hvac
except ImportError:
    hvac = None

load_dotenv()

logger = structlog.get_logger()

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://localhost:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "dev-root-token")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")


def _get_vault_client():
    """Vault client বানানোর চেষ্টা করে; ব্যর্থ হলে None রিটার্ন করে."""
    if hvac is None:
        return None

    try:
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
        if client.is_authenticated():
            return client
    except Exception as e:  # noqa: BLE001
        logger.warning("vault_connection_failed", error=str(e))

    return None


def get_secret(key: str, default: str | None = None) -> str | None:
    """
    Vault থেকে secret পড়ার চেষ্টা করে (path: secret/hello-world).

    Vault না পাওয়া গেলে বা key না থাকলে .env / environment variable
    থেকে পড়ে।
    """
    client = _get_vault_client()

    if client is not None:
        try:
            response = client.secrets.kv.v2.read_secret_version(
                path="hello-world"
            )
            value = response["data"]["data"].get(key)

            if value is not None:
                logger.info("secret_loaded_from_vault", key=key)
                return value

        except Exception as e:  # noqa: BLE001
            logger.warning("vault_read_failed", key=key, error=str(e))

    # Fallback: .env / environment variable
    value = os.getenv(key, default)

    if value is not None:
        logger.info("secret_loaded_from_env", key=key)
    else:
        logger.warning("secret_not_found", key=key)

    return value


# --------------------------------------------------------
# অ্যাপ্লিকেশনের জন্য কনফিগ ভ্যালুগুলো এখানে লোড হবে
# --------------------------------------------------------
DATABASE_URL = get_secret("DATABASE_URL")
NATS_URL = get_secret("NATS_URL", "nats://localhost:4222")
SERVICE_NAME = get_secret("SERVICE_NAME", "hello-world")