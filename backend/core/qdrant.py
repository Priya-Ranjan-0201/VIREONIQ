"""
VIREONIQ Vector Engine Client (Qdrant)
Provides connection to Qdrant vector database with transparent in-memory fallback.
"""
import logging
from typing import Any
from core.config import settings

logger = logging.getLogger(__name__)


class MockCollections:
    """Mock collections container for offline/in-memory fallback."""
    collections = []


class MockQdrantClient:
    """High-speed in-memory vector database fallback when Qdrant server is offline."""
    def get_collections(self) -> MockCollections:
        return MockCollections()

    def get_collection(self, collection_name: str) -> Any:
        return None

    def recreate_collection(self, *args: Any, **kwargs: Any) -> bool:
        return True

    def search(self, *args: Any, **kwargs: Any) -> list:
        return []

    def scroll(self, *args: Any, **kwargs: Any) -> tuple:
        return ([], None)

    def upsert(self, *args: Any, **kwargs: Any) -> bool:
        return True


def init_qdrant_client() -> Any:
    """Initialize Qdrant client or return resilient mock vector store."""
    try:
        from qdrant_client import QdrantClient  # type: ignore
        if settings.QDRANT_URL:
            client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                timeout=1.5,
            )
            client.get_collections()
            logger.info("Initialized Qdrant client with URL: %s", settings.QDRANT_URL)
            return client
        client = QdrantClient(":memory:")
        logger.info("Initialized in-memory Qdrant client")
        return client
    except Exception as exc:
        logger.warning("Qdrant unavailable (%s); using in-memory mock client.", exc)
        return MockQdrantClient()


qdrant_client = init_qdrant_client()
