from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.models.generation import (
    GeneratedFormulaItem,
    GeneratedQuestionCandidateItem,
    GenerationConstraintsRequest,
    QuestionGenerationPreviewRequest,
    QuestionGenerationPreviewResponse,
    QuestionGenerationSaveRequest,
    QuestionGenerationSaveResponse,
)
from core.config.settings import settings
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import get_db_session
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder, QuestionEmbeddingService
from modules.question_generation import (
    GeneratedQuestionCandidate,
    GeminiQuestionGenerator,
    GenerationConstraints,
    QuestionGenerationService,
)

router = APIRouter(prefix="/generation", tags=["generation"])

def create_question_generation_service(
    session: AsyncSession,
) -> QuestionGenerationService:
    return QuestionGenerationService(
        question_repository=QuestionRepository(session),
        generator=GeminiQuestionGenerator(),
    )


def create_question_embedding_service(
    *,
    session: AsyncSession,
    client,
) -> QuestionEmbeddingService:
    return QuestionEmbeddingService(
        question_repository=QuestionRepository(session),
        vector_repository=EmbeddingVectorRepository(
            client=client,
            dimension=settings.embedding_dimension,
            question_collection=settings.qdrant_question_collection,
            formula_collection=settings.qdrant_formula_collection,
        ),
        embedder=GeminiEmbedder(),
    )


def _to_generation_constraints(
    request: GenerationConstraintsRequest | None,
) -> GenerationConstraints:
    if request is None:
        return GenerationConstraints()

    return GenerationConstraints(
        subject=request.subject,
        chapter=request.chapter,
        difficulty=request.difficulty,
        skills=request.skills,
        preserve_formula_style=request.preserve_formula_style,
        avoid_duplicate=request.avoid_duplicate,
    )


def _to_candidate_response(
    candidate: GeneratedQuestionCandidate,
) -> GeneratedQuestionCandidateItem:
    return GeneratedQuestionCandidateItem(
        statement=candidate.statement,
        solution=candidate.solution,
        answer=candidate.answer,
        subject=candidate.subject,
        chapter=candidate.chapter,
        difficulty=candidate.difficulty,
        skills=candidate.skills,
        formulas=[
            GeneratedFormulaItem(
                latex=formula["latex"],
                normalized_latex=formula["normalized_latex"],
                source=formula["source"],
            )
            for formula in candidate.formulas
        ],
        quality_warnings=candidate.quality_warnings,
    )


def _to_generated_candidate(
    candidate: GeneratedQuestionCandidateItem,
) -> GeneratedQuestionCandidate:
    return GeneratedQuestionCandidate(
        statement=candidate.statement,
        solution=candidate.solution,
        answer=candidate.answer,
        subject=candidate.subject,
        chapter=candidate.chapter,
        difficulty=candidate.difficulty,
        skills=candidate.skills,
        formulas=[
            formula.model_dump()
            for formula in candidate.formulas
        ],
        quality_warnings=candidate.quality_warnings,
    )


@router.post(
    "/questions/preview",
    response_model=QuestionGenerationPreviewResponse,
)
async def preview_generated_questions(
    request: QuestionGenerationPreviewRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionGenerationPreviewResponse:
    try:
        service = create_question_generation_service(session)

        preview = await service.preview_questions(
            source_question_id=request.source_question_id,
            generation_count=request.generation_count,
            constraints=_to_generation_constraints(request.constraints),
        )

        return QuestionGenerationPreviewResponse(
            source_question_id=preview.source_question_id,
            candidates=[
                _to_candidate_response(candidate)
                for candidate in preview.candidates
            ],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/questions/save",
    response_model=QuestionGenerationSaveResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_generated_question(
    request: QuestionGenerationSaveRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionGenerationSaveResponse:
    client = create_qdrant_client()

    try:
        generation_service = create_question_generation_service(session)

        saved_question = await generation_service.save_generated_question(
            source_question_id=request.source_question_id,
            candidate=_to_generated_candidate(request.candidate),
        )

        embedding_service = create_question_embedding_service(
            session=session,
            client=client,
        )

        await embedding_service.embed_document(saved_question.document_id)
        await session.refresh(saved_question)

        return QuestionGenerationSaveResponse(
            question_id=saved_question.id,
            document_id=saved_question.document_id,
            sequence_number=saved_question.sequence_number,
            marker=saved_question.marker,
            marker_number=saved_question.marker_number,
            statement=saved_question.statement,
            solution=saved_question.solution,
            answer=saved_question.answer,
            subject=saved_question.subject,
            chapter=saved_question.chapter,
            difficulty=saved_question.difficulty,
            skills=saved_question.skills,
            formulas=[
                GeneratedFormulaItem(
                    latex=formula["latex"],
                    normalized_latex=formula["normalized_latex"],
                    source=formula["source"],
                )
                for formula in saved_question.formulas
            ],
            embedding_status=saved_question.embedding_status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await client.close()