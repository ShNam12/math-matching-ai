from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import questions as questions_endpoint


def make_question(question_id: str = "question-id"):
    now = datetime.now(UTC)

    return SimpleNamespace(
        id=question_id,
        document_id="document-id",
        sequence_number=1,
        marker="Bai",
        marker_number="1",
        statement="Tinh dao ham cua ham so y = 5x^3.",
        solution=None,
        answer="15x^2",
        formulas=[],
        subject="Giải tích 1",
        chapter="Chương 1",
        difficulty="easy",
        skills=["derivative_computation"],
        subject_code="CALCULUS_1",
        chapter_code="GT1_C1_Differential_Calculus_One_Variable",
        chapter_name="Chương 1: Phép tính vi phân hàm một biến số",
        topic_code="GT1_C1_08_Derivatives_Differentials",
        topic_name="Đạo hàm và vi phân",
        problem_type_code="GT1_C1_08_T01_Basic_Derivative",
        problem_type_name="Tính đạo hàm cơ bản",
        taxonomy_id="calculus_1_hust_mi1111",
        taxonomy_version="1.0.0",
        taxonomy_confidence=1.0,
        taxonomy_reason="Matched by test.",
        review_status="auto_accept",
        classification_status="completed",
        classification_model="fake-model",
        classification_error=None,
        classified_at=now,
        embedding_status="completed",
        embedding_model="fake-embedding",
        embedding_dimension=768,
        embedding_error=None,
        embedded_at=now,
        created_at=now,
        updated_at=now,
    )


class FakeQuestionRepository:
    def __init__(self) -> None:
        self.filters = None

    async def list_by_taxonomy(
        self,
        *,
        chapter_code=None,
        topic_code=None,
        problem_type_code=None,
        limit=50,
        offset=0,
    ):
        self.filters = {
            "chapter_code": chapter_code,
            "topic_code": topic_code,
            "problem_type_code": problem_type_code,
            "limit": limit,
            "offset": offset,
        }

        return [make_question()]


def test_list_questions_by_taxonomy(monkeypatch) -> None:
    fake_repository = FakeQuestionRepository()

    monkeypatch.setattr(
        questions_endpoint,
        "QuestionRepository",
        lambda session: fake_repository,
    )

    client = TestClient(app)

    response = client.get(
        "/questions",
        params={
            "topic_code": "GT1_C1_08_Derivatives_Differentials",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == "question-id"
    assert payload[0]["topic_code"] == (
        "GT1_C1_08_Derivatives_Differentials"
    )
    assert payload[0]["problem_type_name"] == "Tính đạo hàm cơ bản"

    assert fake_repository.filters["topic_code"] == (
        "GT1_C1_08_Derivatives_Differentials"
    )


def test_list_questions_by_taxonomy_requires_filter() -> None:
    client = TestClient(app)

    response = client.get("/questions")

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "At least one taxonomy filter is required"
    )