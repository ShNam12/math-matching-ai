from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from apps.api.v1.models.documents import (
    DocumentResponse,
    DocumentStatusResponse,
    DocumentUploadResponse,
)
from apps.api.v1.services.documents import document_service


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF or Markdown document to upload")],
) -> DocumentUploadResponse:
    try:
        return await document_service.create_from_upload(file)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str) -> DocumentResponse:
    document = document_service.get(document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(document_id: str) -> DocumentStatusResponse:
    document = document_service.get(document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return DocumentStatusResponse(
        id=document.id,
        status=document.status,
        message=document.message,
    )

