from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import generation as generation_endpoint
from modules.question_generation import (
    GeneratedQuestionCandidate,
    MultipleChoiceOption,
    QuestionGenerationPreview,
)
from modules.question_quality import QuestionValidationReport


class FakeQdrantClient:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.question_ids = []

    async def embed_question(self, question_id: str):
        self.question_ids.append(question_id)


def make_candidate() -> GeneratedQuestionCandidate:
    return GeneratedQuestionCandidate(
        statement="Chon ket qua cua $1+1$.",
        solution="$1+1=2$.",
        answer="2",
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["addition"],
        formulas=[
            {
                "latex": "1+1",
                "normalized_latex": "1+1",
                "source": "statement",
            }
        ],
        quality_warnings=[],
        question_type="multiple_choice",
        choices=[
            MultipleChoiceOption(key="A", text="1"),
            MultipleChoiceOption(key="B", text="2", is_correct=True),
            MultipleChoiceOption(key="C", text="3"),
            MultipleChoiceOption(key="D", text="4"),
        ],
        correct_choice="B",
        generation_method="ai_convert",
        validation_report=QuestionValidationReport(),
    )


class FakeGenerationService:
    def __init__(self) -> None:
        self.preview_calls = []
        self.save_calls = []

    async def preview_convert_to_mcq(
        self,
        *,
        source_question_id: str,
        generation_count: int = 1,
        constraints=None,
    ):
        self.preview_calls.append(
            {
                "source_question_id": source_question_id,
                "generation_count": generation_count,
                "constraints": constraints,
            }
        )
        return QuestionGenerationPreview(
            source_question_id=source_question_id,
            candidates=[make_candidate()],
        )

    async def save_convert_to_mcq(self, *, source_question_id: str, candidate):
        self.save_calls.append(
            {
                "source_question_id": source_question_id,
                "candidate": candidate,
            }
        )
        return SimpleNamespace(
            id="converted-id",
            document_id="document-id",
            sequence_number=4,
            marker="Generated",
            marker_number="4",
            statement=candidate.statement,
            solution=candidate.solution,
            answer=candidate.answer,
            question_type=candidate.question_type,
            choices=[choice.to_dict() for choice in candidate.choices],
            correct_choice=candidate.correct_choice,
            validation_report=candidate.validation_report.to_dict(),
            generation_method=candidate.generation_method,
            solver_code=candidate.solver_code,
            subject=candidate.subject,
            chapter=candidate.chapter,
            difficulty=candidate.difficulty,
            skills=candidate.skills,
            formulas=candidate.formulas,
            embedding_status="pending",
        )


def test_convert_to_mcq_preview_endpoint(monkeypatch) -> None:
    fake_generation_service = FakeGenerationService()
    monkeypatch.setattr(
        generation_endpoint,
        "create_question_generation_service",
        lambda session: fake_generation_service,
    )

    client = TestClient(app)

    response = client.post(
        "/generation/questions/source-id/convert-to-mcq/preview",
        json={"generation_count": 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_question_id"] == "source-id"
    assert payload["candidates"][0]["question_type"] == "multiple_choice"
    assert payload["candidates"][0]["correct_choice"] == "B"
    assert fake_generation_service.preview_calls[0]["source_question_id"] == (
        "source-id"
    )


def test_convert_to_mcq_preview_endpoint_returns_404(monkeypatch) -> None:
    class ErrorGenerationService:
        async def preview_convert_to_mcq(self, **kwargs):
            raise LookupError("Source question not found")

    monkeypatch.setattr(
        generation_endpoint,
        "create_question_generation_service",
        lambda session: ErrorGenerationService(),
    )

    client = TestClient(app)

    response = client.post(
        "/generation/questions/missing/convert-to-mcq/preview",
        json={"generation_count": 1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Source question not found"


def test_convert_to_mcq_save_endpoint_saves_and_embeds(monkeypatch) -> None:
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
        "/generation/questions/source-id/convert-to-mcq/save",
        json={"candidate": make_candidate().to_dict()},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["question_id"] == "converted-id"
    assert payload["question_type"] == "multiple_choice"
    assert payload["correct_choice"] == "B"
    assert payload["embedding_status"] == "completed"
    assert fake_generation_service.save_calls[0]["source_question_id"] == (
        "source-id"
    )
    assert fake_embedding_service.question_ids == ["converted-id"]
    assert fake_client.closed is True


def test_convert_to_mcq_save_endpoint_returns_400_for_quality_error(
    monkeypatch,
) -> None:
    fake_client = FakeQdrantClient()

    class ErrorGenerationService:
        async def save_convert_to_mcq(self, **kwargs):
            raise ValueError(
                "Generated question failed quality checks: "
                "mcq_duplicate_choice_content"
            )

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
        "/generation/questions/source-id/convert-to-mcq/save",
        json={"candidate": make_candidate().to_dict()},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Generated question failed quality checks: "
        "mcq_duplicate_choice_content"
    )
    assert fake_client.closed is True
