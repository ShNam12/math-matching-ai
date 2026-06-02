import asyncio

from infra.db.repositories.documents import DocumentRepository
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from modules.question_catalog import QuestionCatalogService


async def main() -> None:
    async with AsyncSessionLocal() as session:
        document_repository = DocumentRepository(session)
        question_repository = QuestionRepository(session)

        service = QuestionCatalogService(
            document_repository=document_repository,
            question_repository=question_repository,
        )

        documents = await document_repository.list_documents()
        completed_documents = [
            document
            for document in documents
            if document.status == "completed" and document.markdown_content
        ]

        if not completed_documents:
            raise RuntimeError("No completed document with Markdown was found")

        document = completed_documents[0]
        questions = await service.segment_document(document.id)

        print("Document:", document.id)
        print("Filename:", document.filename)
        print("Question count:", len(questions))

        for question in questions:
            print()
            print(f"{question.marker} {question.marker_number}")
            print("Sequence:", question.sequence_number)
            print("Statement:")
            print(question.statement)
            print("Formula count:", len(question.formulas))


if __name__ == "__main__":
    asyncio.run(main())