from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import search as search_endpoint


class FakeQdrantClient:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class FakeSemanticSearchService:
    def __init__(self, *args, **kwargs) -> None:
        self.calls = []

    async def search_questions(
        self,
        *,
        query: str,
        limit: int,
        filters,
    ):
        self.calls.append(
            {
                "query": query,
                "limit": limit,
                "filters": filters,
            }
        )

        return [
            SimpleNamespace(
                question_id="question-id",
                document_id="document-id",
                score=0.95,
                semantic_score=0.90,
                taxonomy_score=1.0,
                formula_score=0.0,
                difficulty_score=1.0,
                skill_score=1.0,
                marker="Bai",
                marker_number="1",
                statement="Tinh tich phan tung phan.",
                solution="$0+1=1$.",
                answer="1",
                question_type="multiple_choice",
                choices=[
                    {"key": "A", "text": "0"},
                    {"key": "B", "text": "1", "is_correct": True},
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
                subject="Giai tich 1",
                chapter="Chuong 2",
                difficulty="medium",
                skills=["integration_by_parts"],
                subject_code="CALCULUS_1",
                chapter_code=(
                    "GT1_C2_Integral_Calculus_One_Variable"
                ),
                chapter_name="Chuong 2",
                topic_code="GT1_C2_01_Indefinite_Integrals",
                topic_name="Tich phan bat dinh",
                problem_type_code=(
                    "GT1_C2_01_T03_Integration_By_Parts"
                ),
                problem_type_name="Tich phan tung phan",
                taxonomy_confidence=0.95,
                review_status="auto_accept",
                classification_status="completed",
            )
        ]

    async def search_formulas(
        self,
        *,
        latex: str,
        limit: int,
        filters,
    ):
        self.calls.append(
            {
                "latex": latex,
                "limit": limit,
                "filters": filters,
            }
        )

        return [
            SimpleNamespace(
                question_id="question-id",
                document_id="document-id",
                formula_index=2,
                latex=r"\frac{1}{2}",
                normalized_latex=r"\frac{1}{2}",
                source="choice",
                score=0.91,
                marker="Bai",
                marker_number="1",
                statement="Tinh tich phan tung phan.",
                solution="$0+1=1$.",
                answer="1",
                question_type="multiple_choice",
                choices=[
                    {"key": "A", "text": "0"},
                    {"key": "B", "text": "1", "is_correct": True},
                ],
                correct_choice="B",
                subject="Giai tich 1",
                chapter="Chuong 2",
                difficulty="medium",
                skills=["integration_by_parts"],
            )
        ]


def test_search_questions_accepts_taxonomy_filters(monkeypatch) -> None:
    fake_client = FakeQdrantClient()
    fake_service = FakeSemanticSearchService()

    monkeypatch.setattr(
        search_endpoint,
        "create_qdrant_client",
        lambda: fake_client,
    )
    monkeypatch.setattr(
        search_endpoint,
        "SemanticSearchService",
        lambda **kwargs: fake_service,
    )

    client = TestClient(app)

    response = client.post(
        "/search/questions",
        json={
            "query": "tich phan tung phan",
            "limit": 5,
            "chapter_code": "GT1_C2_Integral_Calculus_One_Variable",
            "topic_code": "GT1_C2_01_Indefinite_Integrals",
            "problem_type_code": (
                "GT1_C2_01_T03_Integration_By_Parts"
            ),
            "question_type": "multiple_choice",
            "skill": "integration_by_parts",
            "difficulty": "medium",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["query"] == "tich phan tung phan"
    assert len(payload["results"]) == 1

    result = payload["results"][0]
    assert result["question_id"] == "question-id"
    assert result["chapter_code"] == (
        "GT1_C2_Integral_Calculus_One_Variable"
    )
    assert result["topic_code"] == "GT1_C2_01_Indefinite_Integrals"
    assert result["problem_type_code"] == (
        "GT1_C2_01_T03_Integration_By_Parts"
    )
    assert result["skills"] == ["integration_by_parts"]
    assert result["taxonomy_confidence"] == 0.95
    assert result["classification_status"] == "completed"
    assert result["question_type"] == "multiple_choice"
    assert result["choices"][1]["key"] == "B"
    assert result["choices"][1]["is_correct"] is True
    assert result["correct_choice"] == "B"
    assert result["answer"] == "1"
    assert result["solution"] == "$0+1=1$."
    assert result["validation_report"]["can_save"] is True
    assert result["generation_method"] == "ai_symbolic"
    assert result["solver_code"] == "INT_BY_PARTS"

    assert result["semantic_score"] == 0.90
    assert result["taxonomy_score"] == 1.0
    assert result["formula_score"] == 0.0
    assert result["difficulty_score"] == 1.0
    assert result["skill_score"] == 1.0

    assert fake_service.calls[0]["query"] == "tich phan tung phan"
    assert fake_service.calls[0]["limit"] == 5

    filters = fake_service.calls[0]["filters"]
    assert filters.chapter_code == (
        "GT1_C2_Integral_Calculus_One_Variable"
    )
    assert filters.topic_code == "GT1_C2_01_Indefinite_Integrals"
    assert filters.problem_type_code == (
        "GT1_C2_01_T03_Integration_By_Parts"
    )
    assert filters.question_type == "multiple_choice"
    assert filters.skill == "integration_by_parts"
    assert filters.difficulty == "medium"

    assert fake_client.closed is True


def test_search_questions_can_hide_answers(monkeypatch) -> None:
    fake_client = FakeQdrantClient()
    fake_service = FakeSemanticSearchService()

    monkeypatch.setattr(
        search_endpoint,
        "create_qdrant_client",
        lambda: fake_client,
    )
    monkeypatch.setattr(
        search_endpoint,
        "SemanticSearchService",
        lambda **kwargs: fake_service,
    )

    client = TestClient(app)

    response = client.post(
        "/search/questions",
        json={
            "query": "tich phan tung phan",
            "include_answers": False,
        },
    )

    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["answer"] is None
    assert result["solution"] is None
    assert result["correct_choice"] is None
    assert result["choices"][1]["key"] == "B"
    assert result["choices"][1]["text"] == "1"
    assert result["choices"][1]["is_correct"] is False

    assert fake_client.closed is True


def test_formula_search_returns_mcq_fields(monkeypatch) -> None:
    fake_client = FakeQdrantClient()
    fake_service = FakeSemanticSearchService()

    monkeypatch.setattr(
        search_endpoint,
        "create_qdrant_client",
        lambda: fake_client,
    )
    monkeypatch.setattr(
        search_endpoint,
        "SemanticSearchService",
        lambda **kwargs: fake_service,
    )

    client = TestClient(app)

    response = client.post(
        "/search/formulas",
        json={
            "latex": r"\frac{1}{2}",
            "limit": 5,
            "source": "choice",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["latex"] == r"\frac{1}{2}"
    assert payload["results"][0]["source"] == "choice"
    assert payload["results"][0]["question_type"] == "multiple_choice"
    assert payload["results"][0]["choices"][1]["key"] == "B"
    assert payload["results"][0]["choices"][1]["is_correct"] is True
    assert payload["results"][0]["correct_choice"] == "B"
    assert payload["results"][0]["answer"] == "1"
    assert payload["results"][0]["solution"] == "$0+1=1$."

    assert fake_service.calls[0]["latex"] == r"\frac{1}{2}"
    assert fake_service.calls[0]["filters"].source == "choice"
    assert fake_client.closed is True


def test_formula_search_can_hide_answers(monkeypatch) -> None:
    fake_client = FakeQdrantClient()
    fake_service = FakeSemanticSearchService()

    monkeypatch.setattr(
        search_endpoint,
        "create_qdrant_client",
        lambda: fake_client,
    )
    monkeypatch.setattr(
        search_endpoint,
        "SemanticSearchService",
        lambda **kwargs: fake_service,
    )

    client = TestClient(app)

    response = client.post(
        "/search/formulas",
        json={
            "latex": r"\frac{1}{2}",
            "include_answers": False,
        },
    )

    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["answer"] is None
    assert result["solution"] is None
    assert result["correct_choice"] is None
    assert result["choices"][1]["key"] == "B"
    assert result["choices"][1]["is_correct"] is False
    assert fake_client.closed is True
