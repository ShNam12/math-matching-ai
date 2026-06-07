import asyncio
from typing import Protocol

from infra.db.repositories.questions import QuestionRepository
from modules.embeddings.text_builder import build_formula_embedding_text
from modules.question_segmenter.formula_extractor import normalize_formula
from modules.semantic_search.schemas import (
    FormulaSearchFilters,
    FormulaSearchResult,
    FormulaSearchVectorHit,
    QuestionSearchFilters,
    QuestionSearchResult,
    QuestionSearchVectorHit,
)


class TextEmbedder(Protocol):
    def embed_text(self, text: str) -> list[float]:
        ...


class QuestionVectorSearchRepository(Protocol):
    async def search_questions(
        self,
        *,
        vector: list[float],
        limit: int,
        filters: QuestionSearchFilters,
    ) -> list[QuestionSearchVectorHit]:
        ...

    async def search_formulas(
        self,
        *,
        vector: list[float],
        limit: int,
        filters: FormulaSearchFilters,
    ) -> list[FormulaSearchVectorHit]:
        ...

class SemanticSearchService:
    def __init__(
        self,
        *,
        question_repository: QuestionRepository,
        vector_repository: QuestionVectorSearchRepository,
        embedder: TextEmbedder,
    ) -> None:
        self.question_repository = question_repository
        self.vector_repository = vector_repository
        self.embedder = embedder

    async def search_questions(
        self,
        *,
        query: str,
        limit: int = 10,
        filters: QuestionSearchFilters | None = None,
    ) -> list[QuestionSearchResult]:
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("Search query must not be empty")

        if limit < 1 or limit > 50:
            raise ValueError("Search limit must be between 1 and 50")

        filters = filters or QuestionSearchFilters()

        query_vector = await asyncio.to_thread(
            self.embedder.embed_text,
            normalized_query,
        )

        hits = await self.vector_repository.search_questions(
            vector=query_vector,
            limit=limit,
            filters=filters,
        )

        if not hits:
            return []

        question_ids = [hit.question_id for hit in hits]
        questions = await self.question_repository.list_by_ids(question_ids)
        questions_by_id = {
            question.id: question
            for question in questions
        }

        results: list[QuestionSearchResult] = []

        for hit in hits:
            question = questions_by_id.get(hit.question_id)

            if question is None:
                continue

            if question.embedding_status != "completed":
                continue

            results.append(
                QuestionSearchResult(
                    question_id=question.id,
                    document_id=question.document_id,
                    score=hit.score,
                    marker=question.marker,
                    marker_number=question.marker_number,
                    statement=question.statement,
                    solution=question.solution,
                    answer=question.answer,
                    subject=question.subject,
                    chapter=question.chapter,
                    difficulty=question.difficulty,
                    skills=question.skills,
                )
            )

        return results

    async def search_formulas(
        self,
        *,
        latex: str,
        limit: int = 10,
        filters: FormulaSearchFilters | None = None,
    ) -> list[FormulaSearchResult]:
        normalized_latex = normalize_formula(latex)

        if not normalized_latex:
            raise ValueError("Formula query must not be empty")

        if limit < 1 or limit > 50:
            raise ValueError("Search limit must be between 1 and 50")

        filters = filters or FormulaSearchFilters()

        query_vector = await asyncio.to_thread(
            self.embedder.embed_text,
            build_formula_embedding_text(normalized_latex),
        )

        hits = await self.vector_repository.search_formulas(
            vector=query_vector,
            limit=limit,
            filters=filters,
        )

        if not hits:
            return []

        question_ids = [hit.question_id for hit in hits]
        questions = await self.question_repository.list_by_ids(question_ids)
        questions_by_id = {
            question.id: question
            for question in questions
        }

        results: list[FormulaSearchResult] = []

        for hit in hits:
            question = questions_by_id.get(hit.question_id)

            if question is None:
                continue

            if question.embedding_status != "completed":
                continue

            results.append(
                FormulaSearchResult(
                    question_id=question.id,
                    document_id=question.document_id,
                    formula_index=hit.formula_index,
                    latex=hit.latex,
                    normalized_latex=hit.normalized_latex,
                    source=hit.source,
                    score=hit.score,
                    marker=question.marker,
                    marker_number=question.marker_number,
                    statement=question.statement,
                    solution=question.solution,
                    answer=question.answer,
                    subject=question.subject,
                    chapter=question.chapter,
                    difficulty=question.difficulty,
                    skills=question.skills,
                )
            )

        return results