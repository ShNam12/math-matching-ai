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
                marker="Bai",
                marker_number="1",
                statement="Tinh tich phan tung phan.",
                solution=None,
                answer=None,
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
    assert filters.skill == "integration_by_parts"
    assert filters.difficulty == "medium"

    assert fake_client.closed is True