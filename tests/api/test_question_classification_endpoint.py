from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import questions as questions_endpoint


def make_question(
    *,
    question_id: str = "question-id",
    classification_status: str = "pending",
):
    now = datetime.now(UTC)

    return SimpleNamespace(
        id=question_id,
        document_id="document-id",
        sequence_number=1,
        marker="Bai",
        marker_number="1",
        statement="Tinh tich phan bang tung phan.",
        solution=None,
        answer=None,
        formulas=[],
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
        subject_code=None,
        chapter_code=None,
        chapter_name=None,
        topic_code=None,
        topic_name=None,
        problem_type_code=None,
        problem_type_name=None,
        taxonomy_id=None,
        taxonomy_version=None,
        taxonomy_confidence=None,
        taxonomy_reason=None,
        review_status=None,
        classification_status=classification_status,
        classification_model=None,
        classification_error=None,
        classified_at=None,
        embedding_status="pending",
        embedding_model=None,
        embedding_dimension=None,
        embedding_error=None,
        embedded_at=None,
        created_at=now,
        updated_at=now,
    )


class FakeQuestionRepository:
    def __init__(self, question=None) -> None:
        self.question = question
        self.updated_payload = None
        self.failed_payload = None

    async def get_question(self, question_id: str):
        if self.question is None:
            return None

        if self.question.id != question_id:
            return None

        return self.question

    async def update_classification(
        self,
        question,
        *,
        result,
        classification_model: str,
    ):
        self.updated_payload = {
            "question_id": question.id,
            "result": result,
            "classification_model": classification_model,
        }

        question.subject = "Giai tich 1"
        question.subject_code = "CALCULUS_1"
        question.chapter = "Chuong 2"
        question.chapter_code = "GT1_C2_Integral_Calculus_One_Variable"
        question.chapter_name = "Chuong 2"
        question.topic_code = "GT1_C2_01_Indefinite_Integrals"
        question.topic_name = "Tich phan bat dinh"
        question.problem_type_code = (
            "GT1_C2_01_T03_Integration_By_Parts"
        )
        question.problem_type_name = "Tich phan tung phan"
        question.difficulty = "medium"
        question.skills = ["integration_by_parts"]
        question.taxonomy_id = "calculus_1_hust_mi1111"
        question.taxonomy_version = "1.0.0"
        question.taxonomy_confidence = 0.95
        question.taxonomy_reason = "Matched by fake classifier."
        question.review_status = "auto_accept"
        question.classification_status = "completed"
        question.classification_model = classification_model
        question.classification_error = None
        question.classified_at = datetime.now(UTC)

        return question

    async def mark_classification_failed(
        self,
        question,
        *,
        error_message: str,
        classification_model: str,
    ):
        self.failed_payload = {
            "question_id": question.id,
            "error_message": error_message,
            "classification_model": classification_model,
        }

        question.classification_status = "failed"
        question.classification_error = error_message
        question.classification_model = classification_model

        return question


class FakeClassificationService:
    def __init__(self) -> None:
        self.question_ids = []

    def classify_question(self, question):
        self.question_ids.append(question.id)
        return SimpleNamespace(label="fake-result")


def test_classify_question_endpoint_returns_classified_question(
    monkeypatch,
) -> None:
    fake_repository = FakeQuestionRepository(make_question())
    fake_service = FakeClassificationService()

    synced_question_ids = []

    async def fake_sync_question_payload(question):
        synced_question_ids.append(question.id)

    monkeypatch.setattr(
        questions_endpoint,
        "QuestionRepository",
        lambda session: fake_repository,
    )
    monkeypatch.setattr(
        questions_endpoint,
        "create_question_classification_service",
        lambda: fake_service,
    )

    monkeypatch.setattr(
        questions_endpoint,
        "try_sync_question_classification_payload",
        fake_sync_question_payload,
    )

    client = TestClient(app)
    response = client.post("/questions/question-id/classify")

    assert response.status_code == 200

    payload = response.json()
    assert payload["id"] == "question-id"
    assert payload["classification_status"] == "completed"
    assert payload["chapter_code"] == (
        "GT1_C2_Integral_Calculus_One_Variable"
    )
    assert payload["topic_code"] == "GT1_C2_01_Indefinite_Integrals"
    assert payload["problem_type_code"] == (
        "GT1_C2_01_T03_Integration_By_Parts"
    )
    assert payload["taxonomy_confidence"] == 0.95

    assert fake_service.question_ids == ["question-id"]
    assert fake_repository.updated_payload["classification_model"]

    assert synced_question_ids == ["question-id"]


def test_classify_question_endpoint_returns_404_for_missing_question(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        questions_endpoint,
        "QuestionRepository",
        lambda session: FakeQuestionRepository(None),
    )

    client = TestClient(app)
    response = client.post("/questions/missing/classify")

    assert response.status_code == 404
    assert response.json()["detail"] == "Question not found"
