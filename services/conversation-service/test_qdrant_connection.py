import sys
import os
from qdrant_client import QdrantClient

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
from config_loader import get_secret  # noqa: E402

QDRANT_URL = get_secret("QDRANT_URL", vault_path="conversation-service", default="http://localhost:6333")

client = QdrantClient(url=QDRANT_URL)

print("Qdrant collections:", client.get_collections())
print("✅ Qdrant connection successful")