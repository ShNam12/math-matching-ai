import asyncio

from core.config.settings import settings
from modules.question_classification import (
    GeminiQuestionClassifier,
    QuestionClassificationService,
)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.models.questions import (
    QuestionFormulaItem,
    QuestionResponse,
    QuestionUpdateRequest,
)

from infra.db.models import Question
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import get_db_session


router = APIRouter(prefix="/questions", tags=["questions"])

def create_question_classification_service() -> QuestionClassificationService:
    return QuestionClassificationService(
        classifier=GeminiQuestionClassifier(),
    )

def to_question_response(question: Question) -> QuestionResponse:
    return QuestionResponse(
        id=question.id,
        document_id=question.document_id,
        sequence_number=question.sequence_number,
        marker=question.marker,
        marker_number=question.marker_number,
        statement=question.statement,
        solution=question.solution,
        answer=question.answer,
        formulas=[
            QuestionFormulaItem(
                latex=formula.get("latex", ""),
                normalized_latex=formula.get("normalized_latex", ""),
                source=formula.get("source", ""),
            )
            for formula in question.formulas
        ],
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

        taxonomy_id=question.taxonomy_id,
        taxonomy_version=question.taxonomy_version,
        taxonomy_confidence=question.taxonomy_confidence,
        taxonomy_reason=question.taxonomy_reason,
        review_status=question.review_status,

        classification_status=question.classification_status,
        classification_model=question.classification_model,
        classification_error=question.classification_error,
        classified_at=question.classified_at,

        embedding_status=question.embedding_status,
        embedding_model=question.embedding_model,
        embedding_dimension=question.embedding_dimension,
        embedding_error=question.embedding_error,
        embedded_at=question.embedded_at,
        created_at=question.created_at,
        updated_at=question.updated_at,
    )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionResponse:
    repository = QuestionRepository(session)
    question = await repository.get_question(question_id)

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    return to_question_response(question)

@router.patch("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    payload: QuestionUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionResponse:
    repository = QuestionRepository(session)
    question = await repository.get_question(question_id)

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    updated_question = await repository.update_metadata(
        question,
        subject=payload.subject,
        chapter=payload.chapter,
        difficulty=payload.difficulty,
        skills=payload.skills,
    )

    return to_question_response(updated_question)

@router.post("/{question_id}/classify", response_model=QuestionResponse)
async def classify_question(
    question_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionResponse:
    repository = QuestionRepository(session)
    question = await repository.get_question(question_id)

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    classification_service = create_question_classification_service()

    try:
        result = await asyncio.to_thread(
            classification_service.classify_question,
            question,
        )
        updated_question = await repository.update_classification(
            question,
            result=result,
            classification_model=settings.gemini_model,
        )
    except Exception as exc:
        await repository.mark_classification_failed(
            question,
            error_message=str(exc),
            classification_model=settings.gemini_model,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return to_question_response(updated_question)