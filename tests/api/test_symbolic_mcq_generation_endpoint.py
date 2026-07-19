from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import generation as generation_endpoint
from modules.question_generation import GeneratedQuestionCandidate, MultipleChoiceOption
from modules.question_quality.schemas import QuestionValidationReport


class FakeQdrantClient:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class FakeSymbolicMCQGenerator:
    def __init__(self) -> None:
        self.calls = []

    async def generate(self, **kwargs):
        self.calls.append(kwargs)

        return [
            GeneratedQuestionCandidate(
                statement="Tinh $1+1$.",
                solution="$1+1=2$.",
                answer="2",
                subject=kwargs.get("subject"),
                chapter=kwargs.get("chapter"),
                difficulty=kwargs.get("difficulty"),
                skills=kwargs.get("skills") or [],
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
                symbolic_answer="2",
                generation_method="symbolic",
                solver_code=kwargs["solver_code"],
                validation_report=QuestionValidationReport(),
            )
        ]


class ErrorSymbolicMCQGenerator:
    async def generate(self, **kwargs):
        raise ValueError("Solver not found: MISSING")


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


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.question_ids = []

    async def embed_question(self, question_id: str):
        self.question_ids.append(question_id)


def symbolic_candidate_payload():
    return {
        "statement": "Tinh $1+1$.",
        "solution": "$1+1=2$.",
        "answer": "2",
        "question_type": "multiple_choice",
        "choices": [
            {"key": "A", "text": "1"},
            {"key": "B", "text": "2", "is_correct": True},
            {"key": "C", "text": "3"},
            {"key": "D", "text": "4"},
        ],
        "correct_choice": "B",
        "symbolic_answer": "2",
        "generation_method": "symbolic",
        "solver_code": "INT_XN_EXP",
        "subject": "math",
        "chapter": "integration",
        "difficulty": "medium",
        "skills": ["integration"],
        "formulas": [
            {
                "latex": "1+1",
                "normalized_latex": "1+1",
                "source": "statement",
            }
        ],
    }


def test_symbolic_mcq_solvers_endpoint_returns_solver_list() -> None:
    client = TestClient(app)

    response = client.get("/generation/mcq/solvers")

    assert response.status_code == 200
    payload = response.json()
    assert any(solver["code"] == "INT_XN_EXP" for solver in payload["solvers"])
    first_solver = payload["solvers"][0]
    assert set(first_solver) == {
        "code",
        "name",
        "taxonomy_hint",
        "param_schema",
    }


def test_symbolic_mcq_preview_endpoint_returns_candidates(monkeypatch) -> None:
    fake_generator = FakeSymbolicMCQGenerator()
    monkeypatch.setattr(
        generation_endpoint,
        "create_symbolic_mcq_generator",
        lambda: fake_generator,
    )
    client = TestClient(app)

    response = client.post(
        "/generation/mcq/symbolic/preview",
        json={
            "solver_code": "INT_XN_EXP",
            "generation_count": 1,
            "difficulty": "medium",
            "subject": "math",
            "chapter": "integration",
            "skills": ["integration"],
            "taxonomy": {"problem_type_code": "GT1"},
            "seed": 42,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["solver_code"] == "INT_XN_EXP"
    assert payload["candidates"][0]["question_type"] == "multiple_choice"
    assert payload["candidates"][0]["choices"][1]["is_correct"] is True
    assert fake_generator.calls[0]["generation_count"] == 1
    assert fake_generator.calls[0]["taxonomy_metadata"] == {
        "problem_type_code": "GT1"
    }
    assert fake_generator.calls[0]["seed"] == 42


def test_symbolic_mcq_preview_endpoint_returns_400_for_missing_solver(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        generation_endpoint,
        "create_symbolic_mcq_generator",
        lambda: ErrorSymbolicMCQGenerator(),
    )
    client = TestClient(app)

    response = client.post(
        "/generation/mcq/symbolic/preview",
        json={
            "solver_code": "MISSING",
            "generation_count": 1,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Solver is not supported for Calculus 1: MISSING"


def test_symbolic_mcq_save_endpoint_saves_candidate(monkeypatch) -> None:
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
        "/generation/mcq/symbolic/save",
        json={
            "source_question_id": "source-id",
            "candidate": symbolic_candidate_payload(),
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["question_id"] == "generated-id"
    assert payload["question_type"] == "multiple_choice"
    assert payload["generation_method"] == "symbolic"
    assert payload["solver_code"] == "INT_XN_EXP"
    assert payload["embedding_status"] == "completed"
    assert fake_generation_service.calls[0]["source_question_id"] == "source-id"
    assert fake_embedding_service.question_ids == ["generated-id"]
    assert fake_client.closed is True


def test_symbolic_mcq_save_endpoint_returns_400_for_quality_error(
    monkeypatch,
) -> None:
    fake_client = FakeQdrantClient()

    class ErrorGenerationService:
        async def save_generated_question(self, **kwargs):
            raise ValueError(
                "Generated question failed quality checks: "
                "symbolic_correct_answer_mismatch"
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
        "/generation/mcq/symbolic/save",
        json={
            "source_question_id": "source-id",
            "candidate": symbolic_candidate_payload(),
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Generated question failed quality checks: "
        "symbolic_correct_answer_mismatch"
    )
    assert fake_client.closed is True

def test_list_symbolic_mcq_solvers_returns_only_calculus_1(client):
    response = client.get("/generation/mcq/solvers")

    assert response.status_code == 200

    solver_codes = {
        item["code"]
        for item in response.json()["solvers"]
    }

    assert "INT_XN_EXP" in solver_codes
    assert "DERIV_COMPOSITE" in solver_codes
    assert "DET_2X2" not in solver_codes
    assert "DET_3X3" not in solver_codes

def test_preview_symbolic_mcq_rejects_linear_algebra_solver(client):
    response = client.post(
        "/generation/mcq/symbolic/preview",
        json={
            "solver_code": "DET_2X2",
            "generation_count": 1,
        },
    )

    assert response.status_code == 400
    assert "Calculus 1" in response.json()["detail"]
