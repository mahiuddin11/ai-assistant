
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


def _get_vault_client():
    if hvac is None:
        return None
    try:
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
        if client.is_authenticated():
            return client
    except Exception as e:
        logger.warning("vault_connection_failed", error=str(e))
    return None


def get_secret(key: str, vault_path: str, default: str | None = None) -> str | None:

    client = _get_vault_client()

    if client is not None:
        try:
            response = client.secrets.kv.v2.read_secret_version(path=vault_path)
            value = response["data"]["data"].get(key)
            if value is not None:
                logger.info("secret_loaded_from_vault", key=key, path=vault_path)
                return value
        except Exception as e:
            logger.warning("vault_read_failed", key=key, path=vault_path, error=str(e))

    value = os.getenv(key, default)
    if value is not None:
        logger.info("secret_loaded_from_env", key=key)
    else:
        logger.warning("secret_not_found", key=key)
    return value