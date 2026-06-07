import asyncio
import sys

from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from modules.question_generation import (
    GeminiQuestionGenerator,
    GenerationConstraints,
    QuestionGenerationService,
)


async def main() -> None:
    document_id = sys.argv[1] if len(sys.argv) > 1 else None

    async with AsyncSessionLocal() as session:
        repository = QuestionRepository(session)

        if document_id:
            questions = await repository.list_by_document(document_id)
        else:
            print("Usage:")
            print("  python -m scripts.test_question_generation <document_id>")
            print()
            print("Tip:")
            print("  Use a document_id that already has questions in PostgreSQL.")
            return

        if not questions:
            print(f"No questions found for document_id: {document_id}")
            print("Run sync_question_storage first, or use another document_id.")
            return

        source_question = questions[-1]

        service = QuestionGenerationService(
            question_repository=repository,
            generator=GeminiQuestionGenerator(),
        )

        preview = await service.preview_questions(
            source_question_id=source_question.id,
            generation_count=2,
            constraints=GenerationConstraints(
                difficulty=source_question.difficulty,
                skills=source_question.skills,
                preserve_formula_style=True,
                avoid_duplicate=True,
            ),
        )

        print("Source question:", source_question.marker, source_question.marker_number)
        print("Source ID:", source_question.id)
        print("Document ID:", source_question.document_id)
        print("Statement:", source_question.statement)
        print()

        for index, candidate in enumerate(preview.candidates, start=1):
            print("=" * 80)
            print("Candidate:", index)
            print("Statement:", candidate.statement)
            print("Solution:", candidate.solution)
            print("Answer:", candidate.answer)
            print("Subject:", candidate.subject)
            print("Chapter:", candidate.chapter)
            print("Difficulty:", candidate.difficulty)
            print("Skills:", candidate.skills)
            print("Formulas:", candidate.formulas)
            print("Warnings:", candidate.quality_warnings)


if __name__ == "__main__":
    asyncio.run(main())