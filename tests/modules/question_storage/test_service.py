import asyncio
from types import SimpleNamespace

from modules.embeddings.schemas import EmbeddingResult
from modules.question_storage import QuestionStorageService


class FakeQuestionCatalogService:
    def __init__(self) -> None:
        self.document_id = None

    async def segment_document(self, document_id: str):
        self.document_id = document_id
        return [
            SimpleNamespace(id="q1"),
            SimpleNamespace(id="q2"),
        ]


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.document_id = None

    async def embed_document(self, document_id: str) -> EmbeddingResult:
        self.document_id = document_id
        return EmbeddingResult(
            document_id=document_id,
            question_count=2,
            formula_count=7,
        )


def test_store_document_segments_before_embedding() -> None:
    catalog_service = FakeQuestionCatalogService()
    embedding_service = FakeEmbeddingService()
    service = QuestionStorageService(
        question_catalog_service=catalog_service,
        embedding_service=embedding_service,
    )

    result = asyncio.run(service.store_document("document-id"))

    assert catalog_service.document_id == "document-id"
    assert embedding_service.document_id == "document-id"
    assert result.document_id == "document-id"
    assert result.question_count == 2
    assert result.formula_count == 7