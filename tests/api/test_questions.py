from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import questions as questions_endpoint
from apps.api.v1.endpoints.questions import to_question_response
from infra.db.models import Question


def test_to_question_response_maps_classification_metadata() -> None:
    now = datetime.now(UTC)

    question = Question(
        id="question-1",
        document_id="document-1",
        sequence_number=1,
        marker="Bài",
        marker_number="1",
        statement="Tính tích phân bằng phương pháp từng phần.",
        solution=None,
        answer=None,
        question_type="multiple_choice",
        choices=[
            {
                "key": "A",
                "text": r"\int x e^x dx",
                "latex": r"\int x e^x dx",
                "is_correct": False,
            },
            {
                "key": "B",
                "text": r"(x-1)e^x+C",
                "latex": r"(x-1)e^x+C",
                "is_correct": True,
            },
        ],
        correct_choice="B",
        validation_report={
            "can_save": True,
            "warnings": [],
            "blocking_issues": [],
            "symbolic_checks": [],
        },
        generation_method="ai_symbolic",
        solver_code="INT_BY_PARTS",
        formulas=[
            {
                "latex": r"\int x e^x dx",
                "normalized_latex": r"\int x e^x dx",
                "source": "statement",
            }
        ],
        subject="Giải tích 1",
        subject_code="CALCULUS_1",
        chapter="Chương 2: Phép tính tích phân hàm một biến số",
        chapter_code="GT1_C2_Integral_Calculus_One_Variable",
        chapter_name="Chương 2: Phép tính tích phân hàm một biến số",
        topic_code="GT1_C2_01_Indefinite_Integrals",
        topic_name="Tích phân bất định",
        problem_type_code=(
            "GT1_C2_01_T03_Integration_By_Parts"
        ),
        problem_type_name="Tích phân từng phần",
        difficulty="medium",
        skills=[
            "integration_by_parts",
            "indefinite_integral",
        ],
        taxonomy_id="calculus_1_hust_mi1111",
        taxonomy_version="1.0.0",
        taxonomy_confidence=0.95,
        taxonomy_reason=(
            "Đề bài sử dụng phương pháp tích phân từng phần."
        ),
        review_status="auto_accept",
        classification_status="completed",
        classification_model="fake-model",
        classification_error=None,
        classified_at=now,
        embedding_status="completed",
        embedding_model="fake-embedding-model",
        embedding_dimension=768,
        embedding_error=None,
        embedded_at=now,
        created_at=now,
        updated_at=now,
    )

    response = to_question_response(question)

    assert response.id == question.id
    assert response.document_id == question.document_id
    assert response.question_type == "multiple_choice"
    assert response.correct_choice == "B"
    assert response.choices[1].key == "B"
    assert response.choices[1].is_correct is True
    assert response.validation_report.can_save is True
    assert response.generation_method == "ai_symbolic"
    assert response.solver_code == "INT_BY_PARTS"

    assert response.subject_code == question.subject_code

    assert response.chapter_code == question.chapter_code
    assert response.chapter_name == question.chapter_name
    assert response.topic_code == question.topic_code
    assert response.topic_name == question.topic_name
    assert (
        response.problem_type_code
        == question.problem_type_code
    )
    assert (
        response.problem_type_name
        == question.problem_type_name
    )

    assert response.difficulty == question.difficulty
    assert response.skills == question.skills

    assert response.taxonomy_id == question.taxonomy_id
    assert response.taxonomy_version == question.taxonomy_version
    assert (
        response.taxonomy_confidence
        == question.taxonomy_confidence
    )
    assert response.taxonomy_reason == question.taxonomy_reason
    assert response.review_status == question.review_status

    assert response.classification_status == "completed"
    assert (
        response.classification_model
        == question.classification_model
    )
    assert response.classification_error is None
    assert response.classified_at == question.classified_at

    assert len(response.formulas) == 1
    assert response.formulas[0].latex == r"\int x e^x dx"


def test_to_question_response_can_hide_answers() -> None:
    question = make_api_question()

    response = to_question_response(question, include_answers=False)

    assert response.answer is None
    assert response.solution is None
    assert response.correct_choice is None
    assert response.choices[1].key == "B"
    assert response.choices[1].text == "2"
    assert response.choices[1].is_correct is False


def make_api_question(*, review_status: str | None = "validated"):
    now = datetime.now(UTC)

    return SimpleNamespace(
        id="question-id",
        document_id="document-id",
        sequence_number=1,
        marker="Bai",
        marker_number="1",
        statement="Tinh $1+1$.",
        solution="$1+1=2$.",
        answer="2",
        question_type="multiple_choice",
        choices=[
            {"key": "A", "text": "1", "is_correct": False},
            {"key": "B", "text": "2", "is_correct": True},
            {"key": "C", "text": "3", "is_correct": False},
            {"key": "D", "text": "4", "is_correct": False},
        ],
        correct_choice="B",
        validation_report={
            "can_save": True,
            "warnings": [],
            "blocking_issues": [],
            "symbolic_checks": [],
        },
        generation_method="ai_symbolic",
        solver_code="ADD_INT",
        formulas=[],
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["addition"],
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
        review_status=review_status,
        classification_status="completed",
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


class FakeReviewQuestionRepository:
    def __init__(self, question) -> None:
        self.question = question
        self.updated_statuses = []

    async def get_question(self, question_id: str):
        if self.question is None or question_id != self.question.id:
            return None

        return self.question

    async def update_review_status(self, question, *, review_status: str):
        if review_status not in {
            "draft",
            "generated",
            "validated",
            "needs_review",
            "approved",
            "rejected",
        }:
            raise ValueError("Invalid review_status")

        question.review_status = review_status
        self.updated_statuses.append(review_status)
        return question


def test_get_question_defaults_to_admin_answer_view(monkeypatch) -> None:
    fake_repository = FakeReviewQuestionRepository(make_api_question())

    monkeypatch.setattr(
        questions_endpoint,
        "QuestionRepository",
        lambda session: fake_repository,
    )

    client = TestClient(app)
    response = client.get("/questions/question-id")

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "2"
    assert payload["solution"] == "$1+1=2$."
    assert payload["correct_choice"] == "B"
    assert payload["choices"][1]["is_correct"] is True


def test_get_question_can_hide_answers_for_public_view(monkeypatch) -> None:
    fake_repository = FakeReviewQuestionRepository(make_api_question())

    monkeypatch.setattr(
        questions_endpoint,
        "QuestionRepository",
        lambda session: fake_repository,
    )

    client = TestClient(app)
    response = client.get("/questions/question-id?include_answers=false")

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] is None
    assert payload["solution"] is None
    assert payload["correct_choice"] is None
    assert payload["choices"][1]["key"] == "B"
    assert payload["choices"][1]["text"] == "2"
    assert payload["choices"][1]["is_correct"] is False


def test_update_question_review_status_approves_question(monkeypatch) -> None:
    fake_repository = FakeReviewQuestionRepository(make_api_question())
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
        "try_sync_question_classification_payload",
        fake_sync_question_payload,
    )

    client = TestClient(app)
    response = client.patch(
        "/questions/question-id/review-status",
        json={"review_status": "approved"},
    )

    assert response.status_code == 200
    assert response.json()["review_status"] == "approved"
    assert fake_repository.updated_statuses == ["approved"]
    assert synced_question_ids == ["question-id"]


def test_update_question_review_status_rejects_question(monkeypatch) -> None:
    fake_repository = FakeReviewQuestionRepository(make_api_question())

    async def fake_sync_question_payload(question):
        return None

    monkeypatch.setattr(
        questions_endpoint,
        "QuestionRepository",
        lambda session: fake_repository,
    )
    monkeypatch.setattr(
        questions_endpoint,
        "try_sync_question_classification_payload",
        fake_sync_question_payload,
    )

    client = TestClient(app)
    response = client.patch(
        "/questions/question-id/review-status",
        json={"review_status": "rejected"},
    )

    assert response.status_code == 200
    assert response.json()["review_status"] == "rejected"
    assert fake_repository.updated_statuses == ["rejected"]


def test_update_question_review_status_rejects_invalid_status(monkeypatch) -> None:
    fake_repository = FakeReviewQuestionRepository(make_api_question())

    monkeypatch.setattr(
        questions_endpoint,
        "QuestionRepository",
        lambda session: fake_repository,
    )

    client = TestClient(app)
    response = client.patch(
        "/questions/question-id/review-status",
        json={"review_status": "published"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid review_status"
