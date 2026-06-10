from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import generation as generation_endpoint
from modules.question_quality.schemas import QualityIssue, QuestionQualityReport


class FakeQdrantClient:
    async def close(self) -> None:
        pass


class FakeQuestionRepository:
    def __init__(self, session) -> None:
        self.source_question = SimpleNamespace(
            id="source-id",
            document_id="document-id",
            marker="Bai",
            marker_number="1",
            statement="Tinh $x+1$.",
            solution=None,
            answer=None,
            subject="math",
            chapter="algebra",
            difficulty="medium",
            skills=["simplify"],
        )

    async def get_question(self, question_id: str):
        if question_id == "source-id":
            return self.source_question

        return None

    async def list_by_document(self, document_id: str):
        return [self.source_question]


class FakeQualityService:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def assess_candidate(self, **kwargs):
        return QuestionQualityReport(
            warnings=[
                QualityIssue(
                    code="missing_solution",
                    message="Generated question does not include a solution",
                    severity="warning",
                    field="solution",
                )
            ],
            blocking_issues=[],
            semantic_duplicates=[],
        )


def test_generation_quality_endpoint_returns_report(monkeypatch) -> None:
    monkeypatch.setattr(
        generation_endpoint,
        "create_qdrant_client",
        lambda: FakeQdrantClient(),
    )
    monkeypatch.setattr(
        generation_endpoint,
        "QuestionRepository",
        FakeQuestionRepository,
    )
    monkeypatch.setattr(
        generation_endpoint,
        "QuestionQualityService",
        FakeQualityService,
    )

    client = TestClient(app)

    response = client.post(
        "/generation/questions/quality",
        json={
            "source_question_id": "source-id",
            "requested_difficulty": "medium",
            "candidate": {
                "statement": "Tinh $x+2$.",
                "solution": None,
                "answer": "$x+2$",
                "subject": "math",
                "chapter": "algebra",
                "difficulty": "medium",
                "skills": ["simplify"],
                "formulas": [
                    {
                        "latex": "x+2",
                        "normalized_latex": "x+2",
                        "source": "statement",
                    }
                ],
                "quality_warnings": [],
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["can_save"] is True
    assert payload["quality_warnings"] == ["missing_solution"]
    assert payload["warnings"][0]["field"] == "solution"
    assert payload["blocking_issues"] == []
    assert payload["semantic_duplicates"] == []


def test_generation_quality_endpoint_returns_400_for_missing_source(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        generation_endpoint,
        "create_qdrant_client",
        lambda: FakeQdrantClient(),
    )
    monkeypatch.setattr(
        generation_endpoint,
        "QuestionRepository",
        FakeQuestionRepository,
    )

    client = TestClient(app)

    response = client.post(
        "/generation/questions/quality",
        json={
            "source_question_id": "missing",
            "candidate": {
                "statement": "Tinh $x+2$.",
                "solution": None,
                "answer": "$x+2$",
                "subject": "math",
                "chapter": "algebra",
                "difficulty": "medium",
                "skills": ["simplify"],
                "formulas": [
                    {
                        "latex": "x+2",
                        "normalized_latex": "x+2",
                        "source": "statement",
                    }
                ],
                "quality_warnings": [],
            },
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Source question not found"