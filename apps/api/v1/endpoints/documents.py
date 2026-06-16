from typing import Annotated
import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status

from apps.api.v1.models.documents import (
    DocumentMarkdownResponse,
    DocumentResponse,
    DocumentStatusResponse,
    DocumentStoreResponse,
    DocumentUploadResponse,
)

from modules.question_classification import (
    GeminiQuestionClassifier,
    QuestionClassificationService,
)

from apps.api.v1.models.questions import (
    DocumentClassificationResponse,
    QuestionResponse,
)

from apps.api.v1.endpoints.questions import to_question_response

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.services.documents import DocumentService
from core.config.settings import settings
from infra.db.repositories.documents import DocumentRepository
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal, get_db_session
from infra.storage.r2_client import R2StorageClient
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder, QuestionEmbeddingService
from modules.ingestion.service import IngestionService
from modules.question_catalog import QuestionCatalogService
from modules.question_storage.service import QuestionStorageService


router = APIRouter(prefix="/documents", tags=["documents"])

async def run_ingestion_background(
    document_id: str,
    filename: str,
    content_type: str | None,
    file_bytes: bytes,
) -> None:
    async with AsyncSessionLocal() as session:
        repo = DocumentRepository(session)
        ingestion = IngestionService(
            document_repository=repo,
            storage_client=R2StorageClient(),
        )

        await ingestion.ingest_document(
            document_id=document_id,
            filename=filename,
            content_type=content_type,
            file_bytes=file_bytes,
        )


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(description="PDF or Markdown document to upload")],
    session: AsyncSession = Depends(get_db_session),
) -> DocumentUploadResponse:
    try:
        repo = DocumentRepository(session)
        service = DocumentService(repo)
        document, file_bytes = await service.create_from_upload(file)

        background_tasks.add_task(
            run_ingestion_background,
            document.id,
            document.filename,
            document.content_type,
            file_bytes,
        )

        return document
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    
@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    session: AsyncSession = Depends(get_db_session),
) -> list[DocumentResponse]:
    repo = DocumentRepository(session)
    service = DocumentService(repo)
    return await service.list()

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> DocumentResponse:
    repo = DocumentRepository(session)
    service = DocumentService(repo)
    document = await service.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> DocumentStatusResponse:
    repo = DocumentRepository(session)
    service = DocumentService(repo)
    document = await service.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return DocumentStatusResponse(
        id=document.id,
        status=document.status,
        message=document.message,
        markdown_available=document.markdown_available,
        error_message=document.error_message,
        updated_at=document.updated_at,
    )

@router.get("/{document_id}/markdown", response_model=DocumentMarkdownResponse)
async def get_document_markdown(
    document_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> DocumentMarkdownResponse:
    repo = DocumentRepository(session)
    service = DocumentService(repo)
    document = await service.get_markdown(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if not document.markdown_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Markdown content is not available",
        )

    return DocumentMarkdownResponse(
        id=document.id,
        markdown_content=document.markdown_content,
        markdown_checksum=document.markdown_checksum,
    )

@router.post("/{document_id}/store", response_model=DocumentStoreResponse)
async def store_document(
    document_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> DocumentStoreResponse:
    client = create_qdrant_client()

    try:
        document_repository = DocumentRepository(session)
        question_repository = QuestionRepository(session)

        storage_service = QuestionStorageService(
            question_catalog_service=QuestionCatalogService(
                document_repository=document_repository,
                question_repository=question_repository,
            ),
            classification_service=QuestionClassificationService(
                classifier=GeminiQuestionClassifier(),
            ),
            question_repository=question_repository,
            embedding_service=QuestionEmbeddingService(
                question_repository=question_repository,
                vector_repository=EmbeddingVectorRepository(
                    client=client,
                    dimension=settings.embedding_dimension,
                    question_collection=settings.qdrant_question_collection,
                    formula_collection=settings.qdrant_formula_collection,
                ),
                embedder=GeminiEmbedder(),
            ),
            classification_model=settings.gemini_model,
        )

        result = await storage_service.store_document(document_id)

        return DocumentStoreResponse(
            document_id=result.document_id,
            question_count=result.question_count,
            formula_count=result.formula_count,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await client.close()

@router.post(
    "/{document_id}/classify",
    response_model=DocumentClassificationResponse,
)
async def classify_document(
    document_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> DocumentClassificationResponse:
    document_repository = DocumentRepository(session)
    document = await document_repository.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    question_repository = QuestionRepository(session)
    questions = await question_repository.list_by_document(document_id)

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No segmented questions were found: {document_id}",
        )

    classification_service = QuestionClassificationService(
        classifier=GeminiQuestionClassifier(),
    )

    success_count = 0
    failed_count = 0

    await question_repository.mark_classification_pending_for_document(
        document_id
    )

    for question in questions:
        try:
            result = await asyncio.to_thread(
                classification_service.classify_question,
                question,
            )
            await question_repository.update_classification(
                question,
                result=result,
                classification_model=settings.gemini_model,
            )
            success_count += 1
        except Exception as exc:
            await question_repository.mark_classification_failed(
                question,
                error_message=str(exc),
                classification_model=settings.gemini_model,
            )
            failed_count += 1

    return DocumentClassificationResponse(
        document_id=document_id,
        question_count=len(questions),
        success_count=success_count,
        failed_count=failed_count,
    )

@router.get("/{document_id}/questions", response_model=list[QuestionResponse])
async def list_document_questions(
    document_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> list[QuestionResponse]:
    document_repository = DocumentRepository(session)
    document = await document_repository.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    question_repository = QuestionRepository(session)
    questions = await question_repository.list_by_document(document_id)

    return [
        to_question_response(question)
        for question in questions
    ]