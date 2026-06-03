import asyncio

from core.config.settings import settings
from infra.db.repositories.documents import DocumentRepository
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository


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

            documents = await document_repository.list_documents()

            for document in documents:
                questions = await question_repository.list_by_document(document.id)

                if not questions:
                    continue

                expected_formula_count = sum(
                    len(question.formulas)
                    for question in questions
                )
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

                print()
                print("Document:", document.id)
                print("Filename:", document.filename)
                print("PostgreSQL questions:", len(questions))
                print("PostgreSQL formulas:", expected_formula_count)
                print("PostgreSQL embedding statuses:", status_counts)
                print("Qdrant question points:", question_points)
                print("Qdrant formula points:", formula_points)

                if question_points != len(questions):
                    print("WARNING: question point count mismatch")

                if formula_points != expected_formula_count:
                    print("WARNING: formula point count mismatch")
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())