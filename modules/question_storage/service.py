import asyncio
from dataclasses import dataclass

from infra.db.repositories.questions import QuestionRepository
from modules.embeddings.schemas import EmbeddingResult
from modules.embeddings.service import QuestionEmbeddingService
from modules.question_catalog import QuestionCatalogService
from modules.question_classification import QuestionClassificationService


@dataclass(frozen=True)
class QuestionStorageResult:
    document_id: str
    question_count: int
    formula_count: int
    classification_success_count: int
    classification_failed_count: int


class QuestionStorageService:
    def __init__(
        self,
        *,
        question_catalog_service: QuestionCatalogService,
        classification_service: QuestionClassificationService,
        question_repository: QuestionRepository,
        embedding_service: QuestionEmbeddingService,
        classification_model: str,
    ) -> None:
        self.question_catalog_service = question_catalog_service
        self.classification_service = classification_service
        self.question_repository = question_repository
        self.embedding_service = embedding_service
        self.classification_model = classification_model

    async def store_document(
        self,
        document_id: str,
    ) -> QuestionStorageResult:
        questions = await self.question_catalog_service.segment_document(
            document_id
        )

        if not questions:
            raise ValueError(
                f"No segmented questions were found: {document_id}"
            )

        classification_success_count = 0
        classification_failed_count = 0

        for question in questions:
            try:
                result = await asyncio.to_thread(
                    self.classification_service.classify_question,
                    question,
                )
                await self.question_repository.update_classification(
                    question,
                    result=result,
                    classification_model=self.classification_model,
                )
                classification_success_count += 1
            except Exception as exc:
                await self.question_repository.mark_classification_failed(
                    question,
                    error_message=str(exc),
                    classification_model=self.classification_model,
                )
                classification_failed_count += 1

        embedding_result: EmbeddingResult = (
            await self.embedding_service.embed_document(document_id)
        )

        return QuestionStorageResult(
            document_id=document_id,
            question_count=len(questions),
            formula_count=embedding_result.formula_count,
            classification_success_count=classification_success_count,
            classification_failed_count=classification_failed_count,
        )