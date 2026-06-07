import asyncio

from core.config.settings import settings
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder
from modules.semantic_search import (
    FormulaSearchFilters,
    SemanticSearchService,
)


async def main() -> None:
    async with AsyncSessionLocal() as session:
        client = create_qdrant_client()

        try:
            service = SemanticSearchService(
                question_repository=QuestionRepository(session),
                vector_repository=EmbeddingVectorRepository(
                    client=client,
                    dimension=settings.embedding_dimension,
                    question_collection=settings.qdrant_question_collection,
                    formula_collection=settings.qdrant_formula_collection,
                ),
                embedder=GeminiEmbedder(),
            )

            results = await service.search_formulas(
                latex=r"(1+i\sqrt{3})^{9}",
                limit=5,
                filters=FormulaSearchFilters(),
            )

            if not results:
                print("No formula search results were found")
                return

            for index, result in enumerate(results, start=1):
                print()
                print("Rank:", index)
                print("Score:", result.score)
                print("Question ID:", result.question_id)
                print("Document ID:", result.document_id)
                print("Question:", result.marker, result.marker_number)
                print("Formula index:", result.formula_index)
                print("Latex:", result.latex)
                print("Normalized:", result.normalized_latex)
                print("Source:", result.source)
                print("Statement:", result.statement[:300])
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())