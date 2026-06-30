from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.services.auth import get_current_user
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import get_db_session
from modules.taxonomy import TaxonomyDefinition, load_taxonomy


router = APIRouter(
    prefix="/taxonomy",
    tags=["taxonomy"],
    dependencies=[Depends(get_current_user)],
)


class TaxonomyStatsItem(BaseModel):
    chapter_code: str | None = None
    topic_code: str | None = None
    problem_type_code: str | None = None
    question_count: int


@router.get("", response_model=TaxonomyDefinition)
async def get_taxonomy() -> TaxonomyDefinition:
    return load_taxonomy()


@router.get("/stats", response_model=list[TaxonomyStatsItem])
async def get_taxonomy_stats(
    session: AsyncSession = Depends(get_db_session),
) -> list[TaxonomyStatsItem]:
    repository = QuestionRepository(session)
    stats = await repository.count_by_taxonomy()

    return [
        TaxonomyStatsItem(**item)
        for item in stats
    ]
