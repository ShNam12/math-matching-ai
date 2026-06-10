import asyncio
import sys

from core.config.settings import settings
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder
from modules.question_generation.schemas import GeneratedQuestionCandidate
from modules.question_quality import QuestionQualityService
from modules.semantic_search import SemanticSearchService


async def main() -> None:
    document_id = sys.argv[1] if len(sys.argv) > 1 else None

    if not document_id:
        print("Usage:")
        print("  python -m scripts.test_question_quality <document_id>")
        return

    client = create_qdrant_client()

    try:
        async with AsyncSessionLocal() as session:
            question_repository = QuestionRepository(session)
            questions = await question_repository.list_by_document(document_id)

            if not questions:
                print(f"No questions found for document_id: {document_id}")
                return

            source_question = questions[-1]

            semantic_search_service = SemanticSearchService(
                question_repository=question_repository,
                vector_repository=EmbeddingVectorRepository(
                    client=client,
                    dimension=settings.embedding_dimension,
                    question_collection=settings.qdrant_question_collection,
                    formula_collection=settings.qdrant_formula_collection,
                ),
                embedder=GeminiEmbedder(),
            )

            quality_service = QuestionQualityService(
                semantic_search_service=semantic_search_service,
            )

            candidate = GeneratedQuestionCandidate(
                statement=source_question.statement,
                solution=source_question.solution,
                answer=source_question.answer,
                subject=source_question.subject,
                chapter=source_question.chapter,
                difficulty=source_question.difficulty,
                skills=source_question.skills,
                formulas=source_question.formulas,
                quality_warnings=[],
            )

            report = await quality_service.assess_candidate(
                candidate=candidate,
                source_question=source_question,
                existing_questions=questions,
                requested_difficulty=source_question.difficulty,
            )

            print("Source question ID:", source_question.id)
            print("Document ID:", source_question.document_id)
            print("Can save:", report.can_save)
            print("Quality warnings:", report.quality_warnings)
            print("Blocking issues:", report.blocking_issues)
            print("Warnings:", report.warnings)
            print("Semantic duplicates:", report.semantic_duplicates)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())