from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class DocumentStatus(StrEnum):
    uploaded = "uploaded"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: str | None = None
    size_bytes: int = Field(ge=0)
    source_type: str
    status: DocumentStatus
    message: str
    r2_original_key: str | None = None
    r2_original_url: str | None = None
    markdown_available: bool
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None = None


class DocumentUploadResponse(DocumentResponse):
    pass


class DocumentStatusResponse(BaseModel):
    id: str
    status: DocumentStatus
    message: str
    markdown_available: bool
    error_message: str | None = None
    updated_at: datetime

class DocumentMarkdownResponse(BaseModel):
    id: str
    markdown_content: str
    markdown_checksum: str | None = None

class DocumentStoreResponse(BaseModel):
    document_id: str
    question_count: int = Field(ge=0)
    formula_count: int = Field(ge=0)
    classification_success_count: int = Field(default=0, ge=0)
    classification_failed_count: int = Field(default=0, ge=0)
    embedding_success_count: int = Field(default=0, ge=0)
    embedding_failed_count: int = Field(default=0, ge=0)
    embedding_pending_count: int = Field(default=0, ge=0)
    embedding_failed_question_ids: list[str] = Field(default_factory=list)
