from datetime import datetime

from pydantic import BaseModel, Field


class QuestionFormulaItem(BaseModel):
    latex: str
    normalized_latex: str
    source: str


class QuestionResponse(BaseModel):
    id: str
    document_id: str
    sequence_number: int
    marker: str
    marker_number: str
    statement: str
    solution: str | None = None
    answer: str | None = None
    formulas: list[QuestionFormulaItem] = Field(default_factory=list)
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str] = Field(default_factory=list)
    embedding_status: str
    embedding_model: str | None = None
    embedding_dimension: int | None = None
    embedding_error: str | None = None
    embedded_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

class QuestionUpdateRequest(BaseModel):
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str] | None = None