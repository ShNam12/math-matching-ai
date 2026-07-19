import asyncio
from types import SimpleNamespace

from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings.schemas import FormulaVector, QuestionVector
from modules.semantic_search import QuestionSearchFilters


class FakeQdrantClient:
    def __init__(self) -> None:
        self.collection_name = None
        self.query = None
        self.query_filter = None
        self.limit = None
        self.with_payload = None
        self.with_vectors = None

        self.payload_collection_name = None
        self.payload = None
        self.payload_points = None
        self.payload_wait = None
        self.delete_calls = []
        self.upsert_calls = []

    async def collection_exists(self, collection_name: str) -> bool:
        return True

    async def query_points(
        self,
        *,
        collection_name,
        query,
        query_filter,
        limit,
        with_payload,
        with_vectors,
    ):
        self.collection_name = collection_name
        self.query = query
        self.query_filter = query_filter
        self.limit = limit
        self.with_payload = with_payload
        self.with_vectors = with_vectors

        return SimpleNamespace(
            points=[
                SimpleNamespace(
                    score=0.91,
                    payload={
                        "question_id": "question-id",
                        "document_id": "document-id",
                    },
                )
            ]
        )
    
    async def set_payload(
        self,
        *,
        collection_name,
        payload,
        points,
        wait,
    ):
        self.payload_collection_name = collection_name
        self.payload = payload
        self.payload_points = points
        self.payload_wait = wait

    async def delete(
        self,
        *,
        collection_name,
        points_selector,
        wait,
    ):
        self.delete_calls.append(
            {
                "collection_name": collection_name,
                "points_selector": points_selector,
                "wait": wait,
            }
        )

    async def upsert(
        self,
        *,
        collection_name,
        points,
        wait,
    ):
        self.upsert_calls.append(
            {
                "collection_name": collection_name,
                "points": points,
                "wait": wait,
            }
        )


def test_search_questions_calls_qdrant_with_filters() -> None:
    client = FakeQdrantClient()
    repository = EmbeddingVectorRepository(
        client=client,
        dimension=3,
        question_collection="question_embeddings",
        formula_collection="formula_embeddings",
    )

    hits = asyncio.run(
        repository.search_questions(
            vector=[0.1, 0.2, 0.3],
            limit=5,
            filters=QuestionSearchFilters(
                subject="calculus",
                chapter="derivative",
                question_type="multiple_choice",
                difficulty="easy",
            ),
        )
    )

    assert client.collection_name == "question_embeddings"
    assert client.query == [0.1, 0.2, 0.3]
    assert client.limit == 5
    assert client.with_payload is True
    assert client.with_vectors is False
    assert client.query_filter is not None

    assert len(hits) == 1
    assert hits[0].question_id == "question-id"
    assert hits[0].document_id == "document-id"
    assert hits[0].score == 0.91

def test_update_question_classification_payload_updates_qdrant_payload() -> None:
    client = FakeQdrantClient()
    repository = EmbeddingVectorRepository(
        client=client,
        dimension=3,
        question_collection="question_embeddings",
        formula_collection="formula_embeddings",
    )

    question = SimpleNamespace(
        id="question-id",
        subject="Giải tích 1",
        chapter="Chương 1",
        difficulty="easy",
        skills=["derivative_computation"],
        subject_code="CALCULUS_1",
        chapter_code="GT1_C1_Differential_Calculus_One_Variable",
        chapter_name="Chương 1: Phép tính vi phân hàm một biến số",
        topic_code="GT1_C1_08_Derivatives_Differentials",
        topic_name="Đạo hàm và vi phân",
        problem_type_code="GT1_C1_08_T01_Basic_Derivative",
        problem_type_name="Tính đạo hàm cơ bản",
        taxonomy_confidence=1.0,
        taxonomy_reason="Matched by test.",
        review_status="auto_accept",
        classification_status="completed",
    )

    asyncio.run(
        repository.update_question_classification_payload(question)
    )

    assert client.payload_collection_name == "question_embeddings"
    assert client.payload_points == ["question-id"]
    assert client.payload_wait is True
    assert client.payload["chapter_code"] == (
        "GT1_C1_Differential_Calculus_One_Variable"
    )
    assert client.payload["topic_code"] == (
        "GT1_C1_08_Derivatives_Differentials"
    )
    assert client.payload["problem_type_code"] == (
        "GT1_C1_08_T01_Basic_Derivative"
    )
    assert client.payload["classification_status"] == "completed"


def test_replace_for_question_only_replaces_requested_question_points() -> None:
    client = FakeQdrantClient()
    repository = EmbeddingVectorRepository(
        client=client,
        dimension=3,
        question_collection="question_embeddings",
        formula_collection="formula_embeddings",
    )
    question = QuestionVector(
        question_id="generated-id",
        document_id="document-id",
        sequence_number=3,
        marker="Generated",
        marker_number="3",
        statement="Tinh x.",
        question_type="multiple_choice",
        subject="Calculus 1",
        chapter="Chuong 1",
        difficulty="medium",
        skills=["derivative"],
        subject_code=None,
        chapter_code=None,
        chapter_name=None,
        topic_code=None,
        topic_name=None,
        problem_type_code=None,
        problem_type_name=None,
        taxonomy_confidence=None,
        review_status="validated",
        classification_status="pending",
        vector=[0.1, 0.2, 0.3],
    )
    formula = FormulaVector(
        question_id="generated-id",
        document_id="document-id",
        formula_index=0,
        latex="x^2",
        normalized_latex="x^2",
        source="statement",
        vector=[0.3, 0.2, 0.1],
    )

    asyncio.run(
        repository.replace_for_question(
            question=question,
            formulas=[formula],
        )
    )

    assert [
        call["collection_name"] for call in client.delete_calls
    ] == ["question_embeddings", "formula_embeddings"]
    assert all(call["wait"] is True for call in client.delete_calls)
    assert all(
        call["points_selector"].filter.must[0].key == "question_id"
        for call in client.delete_calls
    )
    assert all(
        call["points_selector"].filter.must[0].match.value
        == "generated-id"
        for call in client.delete_calls
    )
    assert [
        call["collection_name"] for call in client.upsert_calls
    ] == ["question_embeddings", "formula_embeddings"]
    assert client.upsert_calls[0]["points"][0].payload["question_id"] == (
        "generated-id"
    )
    assert client.upsert_calls[1]["points"][0].payload["question_id"] == (
        "generated-id"
    )
