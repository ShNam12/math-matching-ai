import asyncio
from types import SimpleNamespace

from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.semantic_search import FormulaSearchFilters


class FakeQdrantClient:
    def __init__(self) -> None:
        self.collection_name = None
        self.query = None
        self.query_filter = None
        self.limit = None
        self.with_payload = None
        self.with_vectors = None

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
                    score=0.94,
                    payload={
                        "question_id": "question-id",
                        "document_id": "document-id",
                        "formula_index": 2,
                        "latex": "x^2 + 1",
                        "normalized_latex": "x^2 + 1",
                        "source": "statement",
                    },
                )
            ]
        )


def test_search_formulas_calls_qdrant_with_filters() -> None:
    client = FakeQdrantClient()
    repository = EmbeddingVectorRepository(
        client=client,
        dimension=3,
        question_collection="question_embeddings",
        formula_collection="formula_embeddings",
    )

    hits = asyncio.run(
        repository.search_formulas(
            vector=[0.1, 0.2, 0.3],
            limit=5,
            filters=FormulaSearchFilters(source="statement"),
        )
    )

    assert client.collection_name == "formula_embeddings"
    assert client.query == [0.1, 0.2, 0.3]
    assert client.limit == 5
    assert client.with_payload is True
    assert client.with_vectors is False
    assert client.query_filter is not None

    assert len(hits) == 1
    assert hits[0].question_id == "question-id"
    assert hits[0].document_id == "document-id"
    assert hits[0].formula_index == 2
    assert hits[0].latex == "x^2 + 1"
    assert hits[0].normalized_latex == "x^2 + 1"
    assert hits[0].source == "statement"
    assert hits[0].score == 0.94