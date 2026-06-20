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

from modules.semantic_search.hybrid_matching import (
    HybridMatchingCandidate,
    HybridMatchingContext,
    calculate_hybrid_score,
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

        hybrid_context = HybridMatchingContext(
            chapter_code=filters.chapter_code,
            topic_code=filters.topic_code,
            problem_type_code=filters.problem_type_code,
            difficulty=filters.difficulty,
            skills=[filters.skill] if filters.skill else [],
        )
        vector_filters = QuestionSearchFilters(
            subject=filters.subject,
            chapter=filters.chapter,
        )

        query_vector = await asyncio.to_thread(
            self.embedder.embed_text,
            normalized_query,
        )

        hits = await self.vector_repository.search_questions(
            vector=query_vector,
            limit=limit * 3,
            filters=vector_filters,
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

            if filters.subject and question.subject != filters.subject:
                continue

            if filters.chapter and question.chapter != filters.chapter:
                continue

            # if filters.chapter_code and question.chapter_code != filters.chapter_code:
            #     continue

            # if filters.topic_code and question.topic_code != filters.topic_code:
            #     continue

            # if (
            #     filters.problem_type_code
            #     and question.problem_type_code != filters.problem_type_code
            # ):
            #     continue

            # if filters.skill and filters.skill not in question.skills:
            #     continue

            # if filters.difficulty and question.difficulty != filters.difficulty:
            #     continue

            hybrid_score = calculate_hybrid_score(
                context=hybrid_context,
                candidate=HybridMatchingCandidate(
                    semantic_score=hit.score,
                    chapter_code=question.chapter_code,
                    topic_code=question.topic_code,
                    problem_type_code=question.problem_type_code,
                    difficulty=question.difficulty,
                    skills=question.skills,
                ),
            )            

            results.append(
                QuestionSearchResult(
                    question_id=question.id,
                    document_id=question.document_id,
                    score=hybrid_score.final_score,
                    semantic_score=hybrid_score.semantic_score,
                    taxonomy_score=hybrid_score.taxonomy_score,
                    formula_score=hybrid_score.formula_score,
                    difficulty_score=hybrid_score.difficulty_score,
                    skill_score=hybrid_score.skill_score,
                    marker=question.marker,
                    marker_number=question.marker_number,
                    statement=question.statement,
                    solution=question.solution,
                    answer=question.answer,
                    subject=question.subject,
                    chapter=question.chapter,
                    difficulty=question.difficulty,
                    skills=question.skills,
                    subject_code=question.subject_code,
                    chapter_code=question.chapter_code,
                    chapter_name=question.chapter_name,
                    topic_code=question.topic_code,
                    topic_name=question.topic_name,
                    problem_type_code=question.problem_type_code,
                    problem_type_name=question.problem_type_name,
                    taxonomy_confidence=question.taxonomy_confidence,
                    review_status=question.review_status,
                    classification_status=question.classification_status,
                )
            )

        results.sort(key=lambda result: result.score, reverse=True)

        return results[:limit]

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