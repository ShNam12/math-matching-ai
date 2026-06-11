import asyncio
from types import SimpleNamespace

import pytest

from modules.semantic_search import (
    QuestionSearchFilters,
    QuestionSearchVectorHit,
    SemanticSearchService,
)


class FakeQuestionRepository:
    def __init__(self, questions) -> None:
        self.questions = questions
        self.question_ids = None

    async def list_by_ids(self, question_ids: list[str]):
        self.question_ids = question_ids
        questions_by_id = {
            question.id: question
            for question in self.questions
        }

        return [
            questions_by_id[question_id]
            for question_id in question_ids
            if question_id in questions_by_id
        ]


class FakeVectorRepository:
    def __init__(self, hits) -> None:
        self.hits = hits
        self.vector = None
        self.limit = None
        self.filters = None

    async def search_questions(
        self,
        *,
        vector: list[float],
        limit: int,
        filters: QuestionSearchFilters,
    ):
        self.vector = vector
        self.limit = limit
        self.filters = filters
        return self.hits


class FakeEmbedder:
    def __init__(self) -> None:
        self.texts = []

    def embed_text(self, text: str) -> list[float]:
        self.texts.append(text)
        return [0.1, 0.2, 0.3]


def make_question(
    *,
    question_id: str,
    embedding_status: str = "completed",
):
    return SimpleNamespace(
        id=question_id,
        document_id="document-id",
        marker="Bai",
        marker_number="27",
        statement="Tinh dao ham cua ham so.",
        solution="Lay dao ham theo cong thuc.",
        answer="2x",
        subject="calculus",
        chapter="derivative",
        difficulty="easy",
        skills=["derivative"],
        embedding_status=embedding_status,
    )


def test_search_questions_returns_enriched_results_in_score_order() -> None:
    q1 = make_question(question_id="q1")
    q2 = make_question(question_id="q2")

    vector_repository = FakeVectorRepository(
        [
            QuestionSearchVectorHit(
                question_id="q2",
                document_id="document-id",
                score=0.95,
            ),
            QuestionSearchVectorHit(
                question_id="q1",
                document_id="document-id",
                score=0.90,
            ),
        ]
    )
    question_repository = FakeQuestionRepository([q1, q2])
    embedder = FakeEmbedder()

    service = SemanticSearchService(
        question_repository=question_repository,
        vector_repository=vector_repository,
        embedder=embedder,
    )

    results = asyncio.run(
        service.search_questions(
            query="dao ham ham so",
            limit=2,
            filters=QuestionSearchFilters(
                subject="calculus",
                chapter="derivative",
                difficulty="easy",
            ),
        )
    )

    assert embedder.texts == ["dao ham ham so"]
    assert vector_repository.vector == [0.1, 0.2, 0.3]
    assert vector_repository.limit == 2 * 3
    assert vector_repository.filters == QuestionSearchFilters()
    assert question_repository.question_ids == ["q2", "q1"]

    assert [result.question_id for result in results] == ["q2", "q1"]
    assert results[0].score == 0.95
    assert results[0].statement == "Tinh dao ham cua ham so."


def test_search_questions_rejects_empty_query() -> None:
    service = SemanticSearchService(
        question_repository=FakeQuestionRepository([]),
        vector_repository=FakeVectorRepository([]),
        embedder=FakeEmbedder(),
    )

    with pytest.raises(ValueError, match="Search query must not be empty"):
        asyncio.run(service.search_questions(query="   "))


def test_search_questions_rejects_invalid_limit() -> None:
    service = SemanticSearchService(
        question_repository=FakeQuestionRepository([]),
        vector_repository=FakeVectorRepository([]),
        embedder=FakeEmbedder(),
    )

    with pytest.raises(ValueError, match="Search limit"):
        asyncio.run(service.search_questions(query="dao ham", limit=100))


def test_search_questions_skips_non_completed_questions() -> None:
    question = make_question(
        question_id="q1",
        embedding_status="failed",
    )

    service = SemanticSearchService(
        question_repository=FakeQuestionRepository([question]),
        vector_repository=FakeVectorRepository(
            [
                QuestionSearchVectorHit(
                    question_id="q1",
                    document_id="document-id",
                    score=0.91,
                )
            ]
        ),
        embedder=FakeEmbedder(),
    )

    results = asyncio.run(service.search_questions(query="dao ham"))

    assert results == []