from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from apps.api.v1.models.documents import DocumentResponse, DocumentStatus


class DocumentService:
    def __init__(self) -> None:
        self._documents: dict[str, DocumentResponse] = {}
        self._upload_dir = Path("data/uploads")
        self._allowed_suffixes = {".pdf", ".md", ".markdown"}

    async def create_from_upload(self, file: UploadFile) -> DocumentResponse:
        filename = Path(file.filename or "").name
        if not filename:
            raise ValueError("Uploaded file must have a filename")

        suffix = Path(filename).suffix.lower()
        if suffix not in self._allowed_suffixes:
            raise ValueError("Only PDF and Markdown files are supported")

        content = await file.read()
        document_id = str(uuid4())
        target_dir = self._upload_dir / document_id
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / filename).write_bytes(content)

        document = DocumentResponse(
            id=document_id,
            filename=filename,
            content_type=file.content_type,
            size_bytes=len(content),
            status=DocumentStatus.uploaded,
            message="Document uploaded and waiting for processing",
            created_at=datetime.now(UTC),
        )
        self._documents[document_id] = document
        return document

    def get(self, document_id: str) -> DocumentResponse | None:
        return self._documents.get(document_id)


document_service = DocumentService()

