from pathlib import Path

from fastapi import UploadFile

from apps.api.v1.models.documents import DocumentResponse, DocumentStatus
from core.config.settings import settings
from infra.db.models import Document
from infra.db.repositories.documents import DocumentRepository


class DocumentService:
    def __init__(self, document_repository: DocumentRepository) -> None:
        self.document_repository = document_repository
        self._allowed_suffixes = {".pdf", ".md", ".markdown"}

    async def create_from_upload(
        self,
        file: UploadFile,
    ) -> tuple[DocumentResponse, bytes]:
        filename = Path(file.filename or "").name
        if not filename:
            raise ValueError("Uploaded file must have a filename")

        source_type = self._get_source_type(filename)

        content = await file.read()
        if not content:
            raise ValueError("Uploaded file is empty")

        max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
        if len(content) > max_size_bytes:
            raise ValueError(
                f"File size must not exceed {settings.max_upload_size_mb} MB"
            )

        document = await self.document_repository.create_document(
            filename=filename,
            content_type=file.content_type,
            size_bytes=len(content),
            source_type=source_type,
        )

        return self._to_response(document), content
    
    async def get(self, document_id: str) -> DocumentResponse | None:
        document = await self.document_repository.get_document(document_id)

        if document is None:
            return None

        return self._to_response(document)
    
    async def list(self) -> list[DocumentResponse]:
        documents = await self.document_repository.list_documents()
        return [self._to_response(document) for document in documents]
    
    async def get_markdown(self, document_id: str) -> Document | None:
        return await self.document_repository.get_document(document_id)

    def _get_source_type(self, filename: str) -> str:
        suffix = Path(filename).suffix.lower()

        if suffix == ".pdf":
            return "pdf"

        if suffix in {".md", ".markdown"}:
            return "markdown"

        raise ValueError("Only PDF and Markdown files are supported")

    def _to_response(self, document: Document) -> DocumentResponse:
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            source_type=document.source_type,
            status=DocumentStatus(document.status),
            message=self._build_message(document.status),
            r2_original_key=document.r2_original_key,
            r2_original_url=document.r2_original_url,
            markdown_available=document.markdown_content is not None,
            error_message=document.error_message,
            created_at=document.created_at,
            updated_at=document.updated_at,
            processed_at=document.processed_at,
    )

    def _build_message(self, status: str) -> str:
        if status == "uploaded":
            return "Document uploaded and waiting for processing"
        if status == "processing":
            return "Document is being processed"
        if status == "completed":
            return "Document processed successfully"
        if status == "failed":
            return "Document processing failed"
        return "Document status is unknown"