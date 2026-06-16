from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import taxonomy as taxonomy_endpoint


class FakeQuestionRepository:
    async def count_by_taxonomy(self):
        return [
            {
                "chapter_code": (
                    "GT1_C2_Integral_Calculus_One_Variable"
                ),
                "topic_code": "GT1_C2_01_Indefinite_Integrals",
                "problem_type_code": (
                    "GT1_C2_01_T03_Integration_By_Parts"
                ),
                "question_count": 2,
            }
        ]


def test_get_taxonomy_returns_calculus_1_tree() -> None:
    client = TestClient(app)

    response = client.get("/taxonomy")

    assert response.status_code == 200

    payload = response.json()
    assert payload["taxonomy_id"] == "calculus_1_hust_mi1111"
    assert payload["subject_code"] == "CALCULUS_1"
    assert len(payload["chapters"]) == 3


def test_get_taxonomy_stats_returns_question_counts(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        taxonomy_endpoint,
        "QuestionRepository",
        lambda session: FakeQuestionRepository(),
    )

    client = TestClient(app)
    response = client.get("/taxonomy/stats")

    assert response.status_code == 200
    assert response.json() == [
        {
            "chapter_code": (
                "GT1_C2_Integral_Calculus_One_Variable"
            ),
            "topic_code": "GT1_C2_01_Indefinite_Integrals",
            "problem_type_code": (
                "GT1_C2_01_T03_Integration_By_Parts"
            ),
            "question_count": 2,
        }
    ]
