import asyncio
from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import generation as generation_endpoint
from modules.question_generation.service import QuestionQualityCheckError
from modules.question_quality.schemas import (
    QualityIssue,
    QuestionQualityReport,
    QualityRuleResult,
)


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
            question_type=candidate.question_type,
            choices=[
                choice.to_dict()
                for choice in candidate.choices
            ],
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


async def fake_classify_saved_question(*, question, session):
    question.classification_status = "completed"
    question.classification_error = None
    question.chapter_code = "GT1_C1_Differential_Calculus_One_Variable"
    question.topic_code = "GT1_C1_08_Derivatives_Differentials"
    question.problem_type_code = "GT1_C1_08_T04_Chain_Rule"
    return question


def test_classify_saved_question_keeps_corpus_record_when_matching_fails(
    monkeypatch,
) -> None:
    question = SimpleNamespace(
        id="generated-id",
        embedding_status="completed",
    )
    sync_calls = []

    class FailingClassificationService:
        def classify_question(self, _question):
            raise RuntimeError("classification quota exhausted")

    class FakeRepository:
        async def mark_classification_failed(
            self,
            question,
            *,
            error_message,
            classification_model,
        ):
            question.classification_status = "failed"
            question.classification_error = error_message
            question.classification_model = classification_model
            return question

    async def fake_sync(updated_question):
        sync_calls.append(updated_question.id)

    monkeypatch.setattr(
        generation_endpoint,
        "QuestionRepository",
        lambda session: FakeRepository(),
    )
    monkeypatch.setattr(
        generation_endpoint,
        "create_question_classification_service",
        lambda: FailingClassificationService(),
    )
    monkeypatch.setattr(
        generation_endpoint,
        "try_sync_question_classification_payload",
        fake_sync,
    )

    updated_question = asyncio.run(
        generation_endpoint.classify_saved_question(
            question=question,
            session=object(),
        )
    )

    assert updated_question.classification_status == "failed"
    assert "quota exhausted" in updated_question.classification_error
    assert sync_calls == ["generated-id"]


def test_generation_save_endpoint_saves_candidate_and_embeds_question(
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
    monkeypatch.setattr(
        generation_endpoint,
        "classify_saved_question",
        fake_classify_saved_question,
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
    assert payload["classification_status"] == "completed"
    assert payload["problem_type_code"] == "GT1_C1_08_T04_Chain_Rule"
    assert fake_generation_service.calls[0]["source_question_id"] == "source-id"
    assert fake_generation_service.calls[0]["candidate"].statement == "Tinh $x+1$."
    assert fake_embedding_service.question_ids == ["generated-id"]
    assert fake_client.closed is True


def test_generation_save_endpoint_returns_mcq_fields(monkeypatch) -> None:
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
    monkeypatch.setattr(
        generation_endpoint,
        "classify_saved_question",
        fake_classify_saved_question,
    )

    client = TestClient(app)

    response = client.post(
        "/generation/questions/save",
        json={
            "source_question_id": "source-id",
            "candidate": {
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
                "generation_method": "ai_symbolic",
                "solver_code": "ADD_INT",
            },
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["question_type"] == "multiple_choice"
    assert payload["choices"][1]["key"] == "B"
    assert payload["choices"][1]["is_correct"] is True
    assert payload["correct_choice"] == "B"
    assert payload["generation_method"] == "ai_symbolic"
    assert payload["solver_code"] == "ADD_INT"
    assert fake_generation_service.calls[0]["candidate"].question_type == (
        "multiple_choice"
    )
    assert fake_embedding_service.question_ids == ["generated-id"]


def test_generation_save_endpoint_returns_400_for_service_error(
    monkeypatch,
) -> None:
    fake_client = FakeQdrantClient()

    class ErrorGenerationService:
        async def save_generated_question(self, **kwargs):
            raise ValueError(
                "Generated question failed quality checks: exact_duplicate_statement"
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
        "Generated question failed quality checks: exact_duplicate_statement"
    )
    assert fake_client.closed is True


def test_generation_save_endpoint_returns_structured_quality_report(
    monkeypatch,
) -> None:
    fake_client = FakeQdrantClient()

    class ErrorGenerationService:
        async def save_generated_question(self, **kwargs):
            report = QuestionQualityReport(
                blocking_issues=[
                    QualityIssue(
                        code="exact_duplicate_statement",
                        message="Generated statement duplicates an existing question",
                        severity="error",
                        field="statement",
                    )
                ],
                rule_results=[
                    QualityRuleResult(
                        rule_id="exact_duplicate",
                        title="No exact duplicate",
                        category="Duplicate",
                        status="fail",
                    )
                ],
            )
            raise QuestionQualityCheckError(report)

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
            "candidate": {"statement": "Tinh x", "formulas": []},
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "quality_check_failed"
    assert detail["quality_report"]["can_save"] is False
    assert detail["quality_report"]["rule_results"][0]["rule_id"] == (
        "exact_duplicate"
    )
    assert fake_client.closed is True


def test_generation_save_endpoint_returns_400_for_duplicate_mcq_choice(
    monkeypatch,
) -> None:
    fake_client = FakeQdrantClient()

    class ErrorGenerationService:
        async def save_generated_question(self, **kwargs):
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
        "/generation/questions/save",
        json={
            "source_question_id": "source-id",
            "candidate": {
                "statement": "Tinh $1+1$.",
                "solution": "$1+1=2$.",
                "answer": "2",
                "question_type": "multiple_choice",
                "choices": [
                    {"key": "A", "text": "2"},
                    {"key": "B", "text": "2", "is_correct": True},
                    {"key": "C", "text": "3"},
                    {"key": "D", "text": "4"},
                ],
                "correct_choice": "B",
            },
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Generated question failed quality checks: "
        "mcq_duplicate_choice_content"
    )
    assert fake_client.closed is True


def test_generation_save_endpoint_returns_400_for_symbolic_mismatch(
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
        "/generation/questions/save",
        json={
            "source_question_id": "source-id",
            "candidate": {
                "statement": "Tinh dao ham cua $y=x$.",
                "solution": "$(x)'=1$.",
                "answer": "2",
                "question_type": "multiple_choice",
                "choices": [
                    {"key": "A", "text": "0"},
                    {"key": "B", "text": "2", "is_correct": True},
                    {"key": "C", "text": "1"},
                    {"key": "D", "text": "-1"},
                ],
                "correct_choice": "B",
                "solver_code": "DERIV_MONOMIAL",
            },
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Generated question failed quality checks: "
        "symbolic_correct_answer_mismatch"
    )
    assert fake_client.closed is True
