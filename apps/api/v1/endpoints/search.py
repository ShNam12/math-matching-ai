from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.models.search import (
    QuestionSearchItem,
    QuestionSearchRequest,
    QuestionSearchResponse,
)
from core.config.settings import settings
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import get_db_session
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder
from modules.semantic_search import (
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
                difficulty=request.difficulty,
            ),
        )

        return QuestionSearchResponse(
            query=request.query,
            results=[
                QuestionSearchItem(
                    question_id=result.question_id,
                    document_id=result.document_id,
                    score=result.score,
                    marker=result.marker,
                    marker_number=result.marker_number,
                    statement=result.statement,
                    solution=result.solution,
                    answer=result.answer,
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