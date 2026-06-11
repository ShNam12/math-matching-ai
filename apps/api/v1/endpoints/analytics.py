from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.models.analytics import AnalyticsSummaryResponse
from infra.db.models import Document, Question
from infra.db.session import get_db_session


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    session: AsyncSession = Depends(get_db_session),
) -> AnalyticsSummaryResponse:
    document_status_result = await session.execute(
        select(Document.status, func.count(Document.id)).group_by(Document.status)
    )
    document_status_counts = {
        status: count
        for status, count in document_status_result.all()
    }

    embedding_status_result = await session.execute(
        select(Question.embedding_status, func.count(Question.id)).group_by(
            Question.embedding_status
        )
    )
    embedding_status_counts = {
        status: count
        for status, count in embedding_status_result.all()
    }

    difficulty_result = await session.execute(
        select(Question.difficulty, func.count(Question.id)).group_by(
            Question.difficulty
        )
    )
    difficulty_counts = {
        difficulty or "unknown": count
        for difficulty, count in difficulty_result.all()
    }

    chapter_result = await session.execute(
        select(Question.chapter, func.count(Question.id)).group_by(Question.chapter)
    )
    chapter_counts = {
        chapter or "unknown": count
        for chapter, count in chapter_result.all()
    }

    question_count = sum(embedding_status_counts.values())

    formula_result = await session.execute(
        select(Question.formulas)
    )
    formula_count = sum(
        len(formulas or [])
        for formulas in formula_result.scalars().all()
    )

    return AnalyticsSummaryResponse(
        document_count=sum(document_status_counts.values()),
        completed_document_count=document_status_counts.get("completed", 0),
        failed_document_count=document_status_counts.get("failed", 0),
        question_count=question_count,
        embedded_question_count=embedding_status_counts.get("completed", 0),
        formula_count=formula_count,
        embedding_status_counts=embedding_status_counts,
        difficulty_counts=difficulty_counts,
        chapter_counts=chapter_counts,
    )