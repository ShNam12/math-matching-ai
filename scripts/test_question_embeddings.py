import asyncio

from core.config.settings import settings
from infra.db.repositories.documents import DocumentRepository
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder, QuestionEmbeddingService


async def main() -> None:
    async with AsyncSessionLocal() as session:
        document_repository = DocumentRepository(session)
        question_repository = QuestionRepository(session)
        client = create_qdrant_client()

        try:
            vector_repository = EmbeddingVectorRepository(
                client=client,
                dimension=settings.embedding_dimension,
                question_collection=settings.qdrant_question_collection,
                formula_collection=settings.qdrant_formula_collection,
            )
            service = QuestionEmbeddingService(
                question_repository=question_repository,
                vector_repository=vector_repository,
                embedder=GeminiEmbedder(),
            )

            documents = await document_repository.list_documents()

            for document in documents:
                questions = await question_repository.list_by_document(document.id)

                if questions:
                    break
            else:
                raise RuntimeError("No document with segmented questions was found")

            result = await service.embed_document(document.id)

            question_count = await vector_repository.count_for_document(
                collection_name=settings.qdrant_question_collection,
                document_id=document.id,
            )
            formula_count = await vector_repository.count_for_document(
                collection_name=settings.qdrant_formula_collection,
                document_id=document.id,
            )

            print("Document:", document.id)
            print("Filename:", document.filename)
            print("Embedded questions:", result.question_count)
            print("Embedded formulas:", result.formula_count)
            print("Qdrant question points:", question_count)
            print("Qdrant formula points:", formula_count)
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())