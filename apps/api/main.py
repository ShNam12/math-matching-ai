from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.settings import settings
from infra.db.session import get_db_session
from infra.vector_db.qdrant_client import create_qdrant_client

from apps.api.v1.endpoints.documents import router as documents_router
from apps.api.v1.endpoints.generation import router as generation_router
from apps.api.v1.endpoints.questions import router as questions_router
from apps.api.v1.endpoints.search import router as search_router
from apps.api.v1.endpoints.analytics import router as analytics_router
from apps.api.v1.endpoints.taxonomy import router as taxonomy_router


app = FastAPI(
    title="AI Matching API",
    description="Backend API for document ingestion and processing workflows.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {"message": "AI Matching API is running"}


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/ready", tags=["health"])
async def readiness_check(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    checks: dict[str, bool] = {
        "database": False,
        "qdrant": False,
    }

    await session.execute(text("SELECT 1"))
    checks["database"] = True

    client = create_qdrant_client()
    try:
        await client.get_collections()
        checks["qdrant"] = True
    finally:
        await client.close()

    return {
        "status": "ready",
        "checks": checks,
    }

app.include_router(documents_router)
app.include_router(search_router)
app.include_router(generation_router)
app.include_router(questions_router)
app.include_router(analytics_router)
app.include_router(taxonomy_router)