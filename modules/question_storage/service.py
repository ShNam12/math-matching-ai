from dataclasses import dataclass

from modules.embeddings.schemas import EmbeddingResult
from modules.embeddings.service import QuestionEmbeddingService
from modules.question_catalog import QuestionCatalogService


@dataclass(frozen=True)
class QuestionStorageResult:
    document_id: str
    question_count: int
    formula_count: int


class QuestionStorageService:
    def __init__(
        self,
        *,
        question_catalog_service: QuestionCatalogService,
        embedding_service: QuestionEmbeddingService,
    ) -> None:
        self.question_catalog_service = question_catalog_service
        self.embedding_service = embedding_service

    async def store_document(self, document_id: str) -> QuestionStorageResult:
        questions = await self.question_catalog_service.segment_document(
            document_id
        )
        embedding_result: EmbeddingResult = (
            await self.embedding_service.embed_document(document_id)
        )

        return QuestionStorageResult(
            document_id=document_id,
            question_count=len(questions),
            formula_count=embedding_result.formula_count,
        )