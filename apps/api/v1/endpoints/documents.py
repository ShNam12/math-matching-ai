from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status

from apps.api.v1.models.documents import (
    DocumentMarkdownResponse,
    DocumentResponse,
    DocumentStatusResponse,
    DocumentUploadResponse,
)

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.services.documents import DocumentService
from infra.db.repositories.documents import DocumentRepository
from infra.db.session import AsyncSessionLocal, get_db_session
from infra.storage.r2_client import R2StorageClient
from modules.ingestion.service import IngestionService


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