from qdrant_client import AsyncQdrantClient

from core.config.settings import settings


def create_qdrant_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
    )