import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
# pyrefly: ignore [missing-import]
from config_loader import get_secret  # noqa: E402

DATABASE_URL = get_secret(
    "DATABASE_URL",
    vault_path="voice-service",
    default="postgresql+psycopg://root:admin123@localhost:5432/ai_assistant",
)

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8003"))
CONVERSATION_SERVICE_URL = os.getenv("CONVERSATION_SERVICE_URL", "http://localhost:8002")
