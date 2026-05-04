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
    status: DocumentStatus
    message: str
    created_at: datetime


class DocumentUploadResponse(DocumentResponse):
    pass


class DocumentStatusResponse(BaseModel):
    id: str
    status: DocumentStatus
    message: str

