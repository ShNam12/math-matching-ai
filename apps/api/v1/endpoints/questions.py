from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.models.questions import QuestionFormulaItem, QuestionResponse
from infra.db.models import Question
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import get_db_session


router = APIRouter(prefix="/questions", tags=["questions"])


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