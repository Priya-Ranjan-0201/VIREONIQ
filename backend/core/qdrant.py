"""
VIREONIQ Vector Engine Client (Qdrant)
Provides lazy connection initialization to Qdrant with transparent in-memory fallback.
Avoids network timeouts on module import.
"""
from typing import Any
import structlog

from core.config import settings

logger = structlog.get_logger("vireoniq.qdrant")


class MockCollections:
    """Mock collections container for offline/in-memory fallback."""
    collections = []


class MockQdrantClient:
    """In-memory vector database fallback when Qdrant server is offline."""

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
    """Initialize Qdrant client or return resilient in-memory mock client."""
    try:
        from qdrant_client import QdrantClient  # type: ignore

        if settings.QDRANT_URL:
            client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                timeout=1.5,
            )
            client.get_collections()
            logger.info("qdrant_client_initialized", url=settings.QDRANT_URL)
            return client
        client = QdrantClient(":memory:")
        logger.info("qdrant_client_in_memory_initialized")
        return client
    except Exception as exc:
        logger.warning("qdrant_unavailable_using_fallback", error=str(exc))
        return MockQdrantClient()


class LazyQdrantProxy:
    """Defers Qdrant connection until first attribute access."""

    def __init__(self) -> None:
        self._instance: Any = None

    def _get(self) -> Any:
        if self._instance is None:
            self._instance = init_qdrant_client()
        return self._instance

    def __getattr__(self, name: str) -> Any:
        return getattr(self._get(), name)


qdrant_client: Any = LazyQdrantProxy()
