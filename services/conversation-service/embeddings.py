import sys
import os
import structlog
from google import genai

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
from config_loader import get_secret  # noqa: E402

logger = structlog.get_logger()

GEMINI_API_KEY = get_secret("GEMINI_API_KEY", vault_path="conversation-service")
genai_client = genai.Client(api_key=GEMINI_API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"


def get_embedding(text: str) -> list[float]:
    """টেক্সট থেকে একটা vector embedding বানায় (Gemini দিয়ে)।"""
    try:
        result = genai_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config={"output_dimensionality": 768},
        )
        return result.embeddings[0].values
    except Exception as e:
        logger.error("embedding_generation_failed", error=str(e))
        raise RuntimeError(f"Failed to generate embedding: {e}")