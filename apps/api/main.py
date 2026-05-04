from fastapi import FastAPI

from apps.api.v1.endpoints.documents import router as documents_router


app = FastAPI(
    title="AI Matching API",
    description="Backend API for document ingestion and processing workflows.",
    version="0.1.0",
)


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {"message": "AI Matching API is running"}


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(documents_router)

