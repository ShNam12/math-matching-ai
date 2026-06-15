import asyncio
from types import SimpleNamespace

import pytest

from modules.embeddings.schemas import EmbeddingResult
from modules.question_storage import QuestionStorageService


class FakeQuestionCatalogService:
    def __init__(self, questions=None) -> None:
        self.document_id = None
        self.questions = questions

    async def segment_document(self, document_id: str):
        self.document_id = document_id

        if self.questions is not None:
            return self.questions

        return [
            SimpleNamespace(id="q1"),
            SimpleNamespace(id="q2"),
        ]


class FakeClassificationService:
    def __init__(self, *, failed_question_ids=None) -> None:
        self.question_ids = []
        self.failed_question_ids = set(failed_question_ids or [])

    def classify_question(self, question):
        self.question_ids.append(question.id)

        if question.id in self.failed_question_ids:
            raise RuntimeError(f"classification failed: {question.id}")

        return SimpleNamespace(
            question_id=question.id,
            chapter_code="GT1_C2_Integral_Calculus_One_Variable",
        )


class FakeQuestionRepository:
    def __init__(self) -> None:
        self.updated = []
        self.failed = []

    async def update_classification(
        self,
        question,
        *,
        result,
        classification_model: str,
    ) -> None:
        self.updated.append(
            {
                "question_id": question.id,
                "result": result,
                "classification_model": classification_model,
            }
        )

    async def mark_classification_failed(
        self,
        question,
        *,
        error_message: str,
        classification_model: str,
    ) -> None:
        self.failed.append(
            {
                "question_id": question.id,
                "error_message": error_message,
                "classification_model": classification_model,
            }
        )


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


def make_service(
    *,
    catalog_service=None,
    classification_service=None,
    question_repository=None,
    embedding_service=None,
):
    return QuestionStorageService(
        question_catalog_service=(
            catalog_service or FakeQuestionCatalogService()
        ),
        classification_service=(
            classification_service or FakeClassificationService()
        ),
        question_repository=(
            question_repository or FakeQuestionRepository()
        ),
        embedding_service=embedding_service or FakeEmbeddingService(),
        classification_model="fake-classification-model",
    )


def test_store_document_segments_classifies_then_embeds() -> None:
    catalog_service = FakeQuestionCatalogService()
    classification_service = FakeClassificationService()
    question_repository = FakeQuestionRepository()
    embedding_service = FakeEmbeddingService()

    service = make_service(
        catalog_service=catalog_service,
        classification_service=classification_service,
        question_repository=question_repository,
        embedding_service=embedding_service,
    )

    result = asyncio.run(service.store_document("document-id"))

    assert catalog_service.document_id == "document-id"
    assert classification_service.question_ids == ["q1", "q2"]
    assert [
        item["question_id"]
        for item in question_repository.updated
    ] == ["q1", "q2"]
    assert question_repository.failed == []
    assert embedding_service.document_id == "document-id"

    assert result.document_id == "document-id"
    assert result.question_count == 2
    assert result.formula_count == 7
    assert result.classification_success_count == 2
    assert result.classification_failed_count == 0


def test_store_document_marks_failed_classification_and_continues() -> None:
    classification_service = FakeClassificationService(
        failed_question_ids={"q2"},
    )
    question_repository = FakeQuestionRepository()
    embedding_service = FakeEmbeddingService()

    service = make_service(
        classification_service=classification_service,
        question_repository=question_repository,
        embedding_service=embedding_service,
    )

    result = asyncio.run(service.store_document("document-id"))

    assert classification_service.question_ids == ["q1", "q2"]
    assert [
        item["question_id"]
        for item in question_repository.updated
    ] == ["q1"]
    assert len(question_repository.failed) == 1
    assert question_repository.failed[0]["question_id"] == "q2"
    assert question_repository.failed[0]["classification_model"] == (
        "fake-classification-model"
    )
    assert "classification failed: q2" in (
        question_repository.failed[0]["error_message"]
    )

    assert embedding_service.document_id == "document-id"
    assert result.classification_success_count == 1
    assert result.classification_failed_count == 1


def test_store_document_rejects_document_without_questions() -> None:
    catalog_service = FakeQuestionCatalogService(questions=[])
    classification_service = FakeClassificationService()
    question_repository = FakeQuestionRepository()
    embedding_service = FakeEmbeddingService()

    service = make_service(
        catalog_service=catalog_service,
        classification_service=classification_service,
        question_repository=question_repository,
        embedding_service=embedding_service,
    )

    with pytest.raises(ValueError, match="No segmented questions"):
        asyncio.run(service.store_document("document-id"))

    assert classification_service.question_ids == []
    assert question_repository.updated == []
    assert question_repository.failed == []
    assert embedding_service.document_id is None