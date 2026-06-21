from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.models.search import (
    FormulaSearchItem,
    FormulaSearchRequest,
    FormulaSearchResponse,
    QuestionSearchItem,
    QuestionSearchRequest,
    QuestionSearchResponse,
)
from apps.api.v1.endpoints.questions import (
    to_choice_items,
    to_validation_report_item,
)
from core.config.settings import settings
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import get_db_session
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder

from modules.semantic_search import (
    FormulaSearchFilters,
    QuestionSearchFilters,
    SemanticSearchService,
)

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/questions", response_model=QuestionSearchResponse)
async def search_questions(
    request: QuestionSearchRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionSearchResponse:
    client = create_qdrant_client()

    try:
        service = SemanticSearchService(
            question_repository=QuestionRepository(session),
            vector_repository=EmbeddingVectorRepository(
                client=client,
                dimension=settings.embedding_dimension,
                question_collection=settings.qdrant_question_collection,
                formula_collection=settings.qdrant_formula_collection,
            ),
            embedder=GeminiEmbedder(),
        )

        results = await service.search_questions(
            query=request.query,
            limit=request.limit,
            filters=QuestionSearchFilters(
                subject=request.subject,
                chapter=request.chapter,
                question_type=request.question_type,
                chapter_code=request.chapter_code,
                topic_code=request.topic_code,
                problem_type_code=request.problem_type_code,
                difficulty=request.difficulty,
                skill=request.skill,
            ),
        )

        return QuestionSearchResponse(
            query=request.query,
            results=[
                QuestionSearchItem(
                    question_id=result.question_id,
                    document_id=result.document_id,
                    score=result.score,
                    semantic_score=result.semantic_score,
                    taxonomy_score=result.taxonomy_score,
                    formula_score=result.formula_score,
                    difficulty_score=result.difficulty_score,
                    skill_score=result.skill_score,
                    choice_structure_score=getattr(
                        result,
                        "choice_structure_score",
                        0.0,
                    ),
                    marker=result.marker,
                    marker_number=result.marker_number,
                    statement=result.statement,
                    solution=(
                        result.solution
                        if request.include_answers
                        else None
                    ),
                    answer=(
                        result.answer
                        if request.include_answers
                        else None
                    ),
                    question_type=getattr(
                        result,
                        "question_type",
                        "free_response",
                    ),
                    choices=to_choice_items(
                        getattr(result, "choices", []),
                        include_answers=request.include_answers,
                    ),
                    correct_choice=(
                        getattr(result, "correct_choice", None)
                        if request.include_answers
                        else None
                    ),
                    validation_report=to_validation_report_item(
                        getattr(result, "validation_report", {})
                    ),
                    generation_method=getattr(
                        result,
                        "generation_method",
                        None,
                    ),
                    solver_code=getattr(result, "solver_code", None),
                    subject=result.subject,
                    chapter=result.chapter,
                    difficulty=result.difficulty,
                    skills=result.skills,
                    subject_code=result.subject_code,
                    chapter_code=result.chapter_code,
                    chapter_name=result.chapter_name,
                    topic_code=result.topic_code,
                    topic_name=result.topic_name,
                    problem_type_code=result.problem_type_code,
                    problem_type_name=result.problem_type_name,
                    taxonomy_confidence=result.taxonomy_confidence,
                    review_status=result.review_status,
                    classification_status=result.classification_status,
                )
                for result in results
            ],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await client.close()

@router.post("/formulas", response_model=FormulaSearchResponse)
async def search_formulas(
    request: FormulaSearchRequest,
    session: AsyncSession = Depends(get_db_session),
) -> FormulaSearchResponse:
    client = create_qdrant_client()

    try:
        service = SemanticSearchService(
            question_repository=QuestionRepository(session),
            vector_repository=EmbeddingVectorRepository(
                client=client,
                dimension=settings.embedding_dimension,
                question_collection=settings.qdrant_question_collection,
                formula_collection=settings.qdrant_formula_collection,
            ),
            embedder=GeminiEmbedder(),
        )

        results = await service.search_formulas(
            latex=request.latex,
            limit=request.limit,
            filters=FormulaSearchFilters(
                source=request.source,
            ),
        )

        return FormulaSearchResponse(
            latex=request.latex,
            results=[
                FormulaSearchItem(
                    question_id=result.question_id,
                    document_id=result.document_id,
                    formula_index=result.formula_index,
                    latex=result.latex,
                    normalized_latex=result.normalized_latex,
                    source=result.source,
                    score=result.score,
                    marker=result.marker,
                    marker_number=result.marker_number,
                    statement=result.statement,
                    solution=(
                        result.solution
                        if request.include_answers
                        else None
                    ),
                    answer=(
                        result.answer
                        if request.include_answers
                        else None
                    ),
                    question_type=getattr(
                        result,
                        "question_type",
                        "free_response",
                    ),
                    choices=to_choice_items(
                        getattr(result, "choices", []),
                        include_answers=request.include_answers,
                    ),
                    correct_choice=(
                        getattr(result, "correct_choice", None)
                        if request.include_answers
                        else None
                    ),
                    subject=result.subject,
                    chapter=result.chapter,
                    difficulty=result.difficulty,
                    skills=result.skills,
                )
                for result in results
            ],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await client.close()
