from infra.db.models import Question
from infra.db.repositories.documents import DocumentRepository
from infra.db.repositories.questions import QuestionRepository
from modules.question_segmenter import segment_questions


class QuestionCatalogService:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        question_repository: QuestionRepository,
    ) -> None:
        self.document_repository = document_repository
        self.question_repository = question_repository

    async def segment_document(self, document_id: str) -> list[Question]:
        document = await self.document_repository.get_document(document_id)

        if document is None:
            raise ValueError(f"Document not found: {document_id}")

        if document.status != "completed":
            raise ValueError(
                f"Document is not ready for segmentation: {document_id}"
            )

        if not document.markdown_content:
            raise ValueError(
                f"Document Markdown is not available: {document_id}"
            )

        result = segment_questions(document.markdown_content)

        return await self.question_repository.replace_for_document(
            document_id=document.id,
            segmented_questions=result.questions,
        )