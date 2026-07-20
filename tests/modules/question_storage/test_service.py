import asyncio
from types import SimpleNamespace

import pytest

from modules.embeddings.schemas import EmbeddingResult
from modules.question_storage import QuestionStorageService
from infra.db.repositories.questions import infer_mcq_review_status


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
        self.questions = []
        self.failed_question_ids = set(failed_question_ids or [])

    def classify_question(self, question):
        self.question_ids.append(question.id)
        self.questions.append(question)

        if question.id in self.failed_question_ids:
            raise RuntimeError(f"classification failed: {question.id}")

        return SimpleNamespace(
            question_id=question.id,
            chapter_code="GT1_C2_Integral_Calculus_One_Variable",
        )


class FakeQuestionRepository:
    def __init__(self, questions=None) -> None:
        self.questions = questions or []
        self.updated = []
        self.failed = []

    async def list_by_document(self, document_id: str):
        return self.questions

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


def test_store_document_keeps_ingested_mcq_questions_in_pipeline() -> None:
    mcq_question = SimpleNamespace(
        id="q-mcq",
        question_type="multiple_choice",
        choices=[
            {"key": "A", "text": "1", "is_correct": False},
            {"key": "B", "text": "2", "is_correct": True},
            {"key": "C", "text": "3", "is_correct": False},
            {"key": "D", "text": "4", "is_correct": False},
        ],
        correct_choice="B",
    )
    catalog_service = FakeQuestionCatalogService(questions=[mcq_question])
    classification_service = FakeClassificationService()

    service = make_service(
        catalog_service=catalog_service,
        classification_service=classification_service,
    )

    result = asyncio.run(service.store_document("document-id"))

    classified_question = classification_service.questions[0]
    assert classified_question.question_type == "multiple_choice"
    assert classified_question.correct_choice == "B"
    assert classified_question.choices[1]["is_correct"] is True
    assert result.question_count == 1


def test_mcq_review_status_policy_marks_valid_candidate_validated() -> None:
    review_status = infer_mcq_review_status(
        question_type="multiple_choice",
        validation_report={
            "can_save": True,
            "warnings": [],
            "blocking_issues": [],
        },
    )

    assert review_status == "validated"


def test_mcq_review_status_policy_marks_warning_needs_review() -> None:
    review_status = infer_mcq_review_status(
        question_type="multiple_choice",
        validation_report={
            "can_save": True,
            "warnings": [
                {
                    "code": "solver_not_available",
                    "message": "Solver not available.",
                }
            ],
            "blocking_issues": [],
        },
    )

    assert review_status == "needs_review"


def test_review_status_policy_keeps_free_response_legacy_compatible() -> None:
    review_status = infer_mcq_review_status(
        question_type="free_response",
        validation_report=None,
    )

    assert review_status is None


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


def test_store_document_reuses_existing_questions_and_skips_completed_match() -> None:
    existing_question = SimpleNamespace(
        id="q-existing",
        classification_status="completed",
    )
    catalog_service = FakeQuestionCatalogService()
    classification_service = FakeClassificationService()
    question_repository = FakeQuestionRepository([existing_question])
    embedding_service = FakeEmbeddingService()

    service = make_service(
        catalog_service=catalog_service,
        classification_service=classification_service,
        question_repository=question_repository,
        embedding_service=embedding_service,
    )

    result = asyncio.run(service.store_document("document-id"))

    assert catalog_service.document_id is None
    assert classification_service.question_ids == []
    assert embedding_service.document_id == "document-id"
    assert result.question_count == 1
    assert result.classification_success_count == 0
