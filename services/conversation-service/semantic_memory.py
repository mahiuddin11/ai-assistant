import sys
import os
import uuid
import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sqlalchemy.orm import Session

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
from config_loader import get_secret  # noqa: E402

from embeddings import get_embedding
from models import MemorySemantic

logger = structlog.get_logger()

QDRANT_URL = get_secret("QDRANT_URL", vault_path="conversation-service", default="http://localhost:6333")
qdrant_client = QdrantClient(url=QDRANT_URL)

COLLECTION_NAME = "semantic_memory"


def store_memory(db: Session, content: str, user_id: str | None = None, conversation_id: str | None = None) -> None:
    """একটা নতুন ফ্যাক্ট/তথ্য Qdrant (ভেক্টর) + Postgres (মেটাডেটা) দুই জায়গায় সেভ করে।"""
    point_id = str(uuid.uuid4())
    vector = get_embedding(content)

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=point_id, vector=vector, payload={"content": content})],
    )

    record = MemorySemantic(
        user_id=user_id,
        conversation_id=conversation_id,
        content=content,
        qdrant_point_id=point_id,
    )
    db.add(record)
    db.commit()

    logger.info("semantic_memory_stored", point_id=point_id)


def retrieve_relevant_memories(query: str, top_k: int = 3) -> list[str]:
    """Query-এর সাথে সবচেয়ে প্রাসঙ্গিক top-k মেমোরি খুঁজে টেক্সট হিসেবে রিটার্ন করে।"""
    query_vector = get_embedding(query)

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
    ).points

    memories = [hit.payload["content"] for hit in results]
    logger.info("semantic_memory_retrieved", count=len(memories))
    return memories