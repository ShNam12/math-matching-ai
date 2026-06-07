import asyncio
from types import SimpleNamespace

import pytest

from modules.semantic_search import (
    FormulaSearchFilters,
    FormulaSearchVectorHit,
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

    async def search_questions(self, **kwargs):
        return []

    async def search_formulas(
        self,
        *,
        vector: list[float],
        limit: int,
        filters: FormulaSearchFilters,
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
        statement="Tinh $x^2 + 1$.",
        solution=None,
        answer=None,
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
        embedding_status=embedding_status,
    )


def test_search_formulas_returns_enriched_results_in_score_order() -> None:
    q1 = make_question(question_id="q1")
    q2 = make_question(question_id="q2")

    vector_repository = FakeVectorRepository(
        [
            FormulaSearchVectorHit(
                question_id="q2",
                document_id="document-id",
                formula_index=1,
                latex="x^2 + 1",
                normalized_latex="x^2 + 1",
                source="statement",
                score=0.96,
            ),
            FormulaSearchVectorHit(
                question_id="q1",
                document_id="document-id",
                formula_index=0,
                latex="x^2",
                normalized_latex="x^2",
                source="answer",
                score=0.91,
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
        service.search_formulas(
            latex="  x^2   +   1  ",
            limit=2,
            filters=FormulaSearchFilters(source="statement"),
        )
    )

    assert embedder.texts == [
        "task: sentence similarity | query: mathematical formula: x^2 + 1"
    ]
    assert vector_repository.vector == [0.1, 0.2, 0.3]
    assert vector_repository.limit == 2
    assert vector_repository.filters.source == "statement"
    assert question_repository.question_ids == ["q2", "q1"]

    assert [result.question_id for result in results] == ["q2", "q1"]
    assert results[0].formula_index == 1
    assert results[0].normalized_latex == "x^2 + 1"
    assert results[0].score == 0.96


def test_search_formulas_rejects_empty_formula() -> None:
    service = SemanticSearchService(
        question_repository=FakeQuestionRepository([]),
        vector_repository=FakeVectorRepository([]),
        embedder=FakeEmbedder(),
    )

    with pytest.raises(ValueError, match="Formula query must not be empty"):
        asyncio.run(service.search_formulas(latex="   "))


def test_search_formulas_rejects_invalid_limit() -> None:
    service = SemanticSearchService(
        question_repository=FakeQuestionRepository([]),
        vector_repository=FakeVectorRepository([]),
        embedder=FakeEmbedder(),
    )

    with pytest.raises(ValueError, match="Search limit"):
        asyncio.run(service.search_formulas(latex="x^2", limit=100))


def test_search_formulas_skips_non_completed_questions() -> None:
    question = make_question(
        question_id="q1",
        embedding_status="failed",
    )

    service = SemanticSearchService(
        question_repository=FakeQuestionRepository([question]),
        vector_repository=FakeVectorRepository(
            [
                FormulaSearchVectorHit(
                    question_id="q1",
                    document_id="document-id",
                    formula_index=0,
                    latex="x^2",
                    normalized_latex="x^2",
                    source="statement",
                    score=0.90,
                )
            ]
        ),
        embedder=FakeEmbedder(),
    )

    results = asyncio.run(service.search_formulas(latex="x^2"))

    assert results == []