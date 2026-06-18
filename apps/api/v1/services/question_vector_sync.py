import logging

from core.config.settings import settings
from infra.db.models import Question
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository


logger = logging.getLogger(__name__)


async def sync_question_classification_payload(
    question: Question,
) -> None:
    if question.embedding_status != "completed":
        return

    client = create_qdrant_client()

    try:
        repository = EmbeddingVectorRepository(
            client=client,
            dimension=settings.embedding_dimension,
            question_collection=settings.qdrant_question_collection,
            formula_collection=settings.qdrant_formula_collection,
        )

        await repository.update_question_classification_payload(question)
    finally:
        await client.close()


async def try_sync_question_classification_payload(
    question: Question,
) -> None:
    try:
        await sync_question_classification_payload(question)
    except Exception:
        logger.exception(
            "Failed to sync question classification payload to Qdrant: %s",
            question.id,
        )