import sys
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))

# pyrefly: ignore [missing-import]
from config_loader import get_secret  # noqa: E402

QDRANT_URL = get_secret("QDRANT_URL", vault_path="conversation-service", default="http://localhost:6333")
client = QdrantClient(url=QDRANT_URL)

COLLECTION_NAME = "semantic_memory"
VECTOR_SIZE = 768  # Gemini text-embedding-004 এর ভেক্টর সাইজ

existing = [c.name for c in client.get_collections().collections]

if COLLECTION_NAME in existing:
    print(f"Collection '{COLLECTION_NAME}' already exists — skipping.")
else:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"✅ Collection '{COLLECTION_NAME}' created (size={VECTOR_SIZE}, distance=COSINE)")