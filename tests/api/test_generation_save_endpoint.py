from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import generation as generation_endpoint


class FakeQdrantClient:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class FakeGenerationService:
    def __init__(self) -> None:
        self.calls = []

    async def save_generated_question(
        self,
        *,
        source_question_id: str,
        candidate,
    ):
        self.calls.append(
            {
                "source_question_id": source_question_id,
                "candidate": candidate,
            }
        )

        return SimpleNamespace(
            id="generated-id",
            document_id="document-id",
            sequence_number=3,
            marker="Generated",
            marker_number="3",
            statement=candidate.statement,
            solution=candidate.solution,
            answer=candidate.answer,
            subject=candidate.subject,
            chapter=candidate.chapter,
            difficulty=candidate.difficulty,
            skills=candidate.skills,
            formulas=candidate.formulas,
            embedding_status="pending",
        )


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.document_ids = []

    async def embed_document(self, document_id: str):
        self.document_ids.append(document_id)


def test_generation_save_endpoint_saves_candidate_and_embeds_document(
    monkeypatch,
) -> None:
    fake_client = FakeQdrantClient()
    fake_generation_service = FakeGenerationService()
    fake_embedding_service = FakeEmbeddingService()

    async def fake_refresh(question):
        question.embedding_status = "completed"

    monkeypatch.setattr(
        generation_endpoint,
        "create_qdrant_client",
        lambda: fake_client,
    )
    monkeypatch.setattr(
        generation_endpoint,
        "create_question_generation_service",
        lambda session: fake_generation_service,
    )
    monkeypatch.setattr(
        generation_endpoint,
        "create_question_embedding_service",
        lambda *, session, client: fake_embedding_service,
    )
    monkeypatch.setattr(
        generation_endpoint.AsyncSession,
        "refresh",
        lambda self, question: fake_refresh(question),
    )

    client = TestClient(app)

    response = client.post(
        "/generation/questions/save",
        json={
            "source_question_id": "source-id",
            "candidate": {
                "statement": "Tinh $x+1$.",
                "solution": None,
                "answer": "$x+1$",
                "subject": "math",
                "chapter": "algebra",
                "difficulty": "easy",
                "skills": ["simplify"],
                "formulas": [
                    {
                        "latex": "x+1",
                        "normalized_latex": "x+1",
                        "source": "statement",
                    }
                ],
                "quality_warnings": [],
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["question_id"] == "generated-id"
    assert payload["document_id"] == "document-id"
    assert payload["sequence_number"] == 3
    assert payload["marker"] == "Generated"
    assert payload["marker_number"] == "3"
    assert payload["statement"] == "Tinh $x+1$."
    assert payload["embedding_status"] == "completed"
    assert fake_generation_service.calls[0]["source_question_id"] == "source-id"
    assert fake_generation_service.calls[0]["candidate"].statement == "Tinh $x+1$."
    assert fake_embedding_service.document_ids == ["document-id"]
    assert fake_client.closed is True


def test_generation_save_endpoint_returns_400_for_service_error(
    monkeypatch,
) -> None:
    fake_client = FakeQdrantClient()

    class ErrorGenerationService:
        async def save_generated_question(self, **kwargs):
            raise ValueError("Generated question duplicates an existing question")

    monkeypatch.setattr(
        generation_endpoint,
        "create_qdrant_client",
        lambda: fake_client,
    )
    monkeypatch.setattr(
        generation_endpoint,
        "create_question_generation_service",
        lambda session: ErrorGenerationService(),
    )

    client = TestClient(app)

    response = client.post(
        "/generation/questions/save",
        json={
            "source_question_id": "source-id",
            "candidate": {
                "statement": "Tinh $x+1$.",
                "solution": None,
                "answer": "$x+1$",
                "subject": "math",
                "chapter": "algebra",
                "difficulty": "easy",
                "skills": ["simplify"],
                "formulas": [
                    {
                        "latex": "x+1",
                        "normalized_latex": "x+1",
                        "source": "statement",
                    }
                ],
                "quality_warnings": [],
            },
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Generated question duplicates an existing question"
    )
    assert fake_client.closed is True