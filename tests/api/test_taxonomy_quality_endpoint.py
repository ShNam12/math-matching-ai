from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import questions as questions_endpoint


def make_question(**overrides):
    now = datetime.now(UTC)

    data = {
        "id": "question-id",
        "document_id": "document-id",
        "sequence_number": 1,
        "marker": "Bai",
        "marker_number": "1",
        "statement": "Tinh dao ham cua ham so.",
        "solution": None,
        "answer": None,
        "formulas": [],
        "subject": "Giải tích 1",
        "chapter": "Chương 1",
        "difficulty": "easy",
        "skills": ["derivative_computation"],
        "subject_code": "CALCULUS_1",
        "chapter_code": "GT1_C1_Differential_Calculus_One_Variable",
        "chapter_name": "Chương 1",
        "topic_code": "GT1_C1_08_Derivatives_Differentials",
        "topic_name": "Đạo hàm và vi phân",
        "problem_type_code": "GT1_C1_08_T01_Basic_Derivative",
        "problem_type_name": "Tính đạo hàm cơ bản",
        "taxonomy_id": "calculus_1_hust_mi1111",
        "taxonomy_version": "1.0.0",
        "taxonomy_confidence": 0.95,
        "taxonomy_reason": "Matched.",
        "review_status": "auto_accept",
        "classification_status": "completed",
        "classification_model": "fake-model",
        "classification_error": None,
        "classified_at": now,
        "embedding_status": "completed",
        "embedding_model": "fake-embedding",
        "embedding_dimension": 768,
        "embedding_error": None,
        "embedded_at": now,
        "created_at": now,
        "updated_at": now,
    }

    data.update(overrides)
    return SimpleNamespace(**data)


class FakeQuestionRepository:
    def __init__(self, question=None):
        self.question = question

    async def get_question(self, question_id: str):
        if self.question is None:
            return None

        if self.question.id != question_id:
            return None

        return self.question


def test_question_taxonomy_quality_returns_report(monkeypatch):
    monkeypatch.setattr(
        questions_endpoint,
        "QuestionRepository",
        lambda session: FakeQuestionRepository(
            make_question(taxonomy_confidence=0.5)
        ),
    )

    client = TestClient(app)
    response = client.get("/questions/question-id/taxonomy-quality")

    assert response.status_code == 200

    payload = response.json()
    assert payload["question_id"] == "question-id"
    assert payload["can_accept"] is True
    assert payload["warnings"][0]["code"] == "low_confidence"


def test_question_taxonomy_quality_returns_404(monkeypatch):
    monkeypatch.setattr(
        questions_endpoint,
        "QuestionRepository",
        lambda session: FakeQuestionRepository(None),
    )

    client = TestClient(app)
    response = client.get("/questions/missing/taxonomy-quality")

    assert response.status_code == 404