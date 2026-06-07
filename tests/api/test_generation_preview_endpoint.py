from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import generation as generation_endpoint
from modules.question_generation import (
    GeneratedQuestionCandidate,
    QuestionGenerationPreview,
)


class FakeGenerationService:
    def __init__(self) -> None:
        self.calls = []

    async def preview_questions(
        self,
        *,
        source_question_id: str,
        generation_count: int,
        constraints,
    ) -> QuestionGenerationPreview:
        self.calls.append(
            {
                "source_question_id": source_question_id,
                "generation_count": generation_count,
                "constraints": constraints,
            }
        )

        return QuestionGenerationPreview(
            source_question_id=source_question_id,
            candidates=[
                GeneratedQuestionCandidate(
                    statement="Tinh $x+1$.",
                    solution=None,
                    answer="$x+1$",
                    subject="math",
                    chapter="algebra",
                    difficulty="easy",
                    skills=["simplify"],
                    formulas=[
                        {
                            "latex": "x+1",
                            "normalized_latex": "x+1",
                            "source": "statement",
                        }
                    ],
                    quality_warnings=[],
                )
            ],
        )


def test_generation_preview_endpoint_returns_candidates(monkeypatch) -> None:
    fake_service = FakeGenerationService()

    monkeypatch.setattr(
        generation_endpoint,
        "create_question_generation_service",
        lambda session: fake_service,
    )

    client = TestClient(app)

    response = client.post(
        "/generation/questions/preview",
        json={
            "source_question_id": "source-id",
            "generation_count": 1,
            "constraints": {
                "difficulty": "easy",
                "skills": ["simplify"],
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_question_id"] == "source-id"
    assert payload["candidates"][0]["statement"] == "Tinh $x+1$."
    assert payload["candidates"][0]["formulas"][0]["normalized_latex"] == "x+1"
    assert fake_service.calls[0]["generation_count"] == 1
    assert fake_service.calls[0]["constraints"].difficulty == "easy"
    assert fake_service.calls[0]["constraints"].skills == ["simplify"]


def test_generation_preview_endpoint_returns_400_for_service_error(monkeypatch) -> None:
    class ErrorService:
        async def preview_questions(self, **kwargs):
            raise ValueError("Source question not found")

    monkeypatch.setattr(
        generation_endpoint,
        "create_question_generation_service",
        lambda session: ErrorService(),
    )

    client = TestClient(app)

    response = client.post(
        "/generation/questions/preview",
        json={
            "source_question_id": "missing",
            "generation_count": 1,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Source question not found"