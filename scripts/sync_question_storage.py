import asyncio

from core.config.settings import settings
from infra.db.repositories.documents import DocumentRepository
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder, QuestionEmbeddingService
from modules.question_catalog import QuestionCatalogService
from modules.question_storage import QuestionStorageService


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
            catalog_service = QuestionCatalogService(
                document_repository=document_repository,
                question_repository=question_repository,
            )
            embedding_service = QuestionEmbeddingService(
                question_repository=question_repository,
                vector_repository=vector_repository,
                embedder=GeminiEmbedder(),
            )
            storage_service = QuestionStorageService(
                question_catalog_service=catalog_service,
                embedding_service=embedding_service,
            )

            documents = await document_repository.list_documents()
            completed_documents = [
                document
                for document in documents
                if document.status == "completed" and document.markdown_content
            ]

            if not completed_documents:
                raise RuntimeError("No completed document with Markdown was found")

            document = next(
                (
                    document
                    for document in completed_documents
                    if document.filename == "bttx.md"
                ),
                completed_documents[0],
            )

            result = await storage_service.store_document(document.id)
            status_counts = await question_repository.count_by_embedding_status(
                document.id
            )
            question_points = await vector_repository.count_for_document(
                collection_name=settings.qdrant_question_collection,
                document_id=document.id,
            )
            formula_points = await vector_repository.count_for_document(
                collection_name=settings.qdrant_formula_collection,
                document_id=document.id,
            )

            print("Document:", document.id)
            print("Filename:", document.filename)
            print("Questions stored:", result.question_count)
            print("Formulas embedded:", result.formula_count)
            print("PostgreSQL embedding statuses:", status_counts)
            print("Qdrant question points:", question_points)
            print("Qdrant formula points:", formula_points)
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())