from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QuestionFormulaItem(BaseModel):
    latex: str
    normalized_latex: str
    source: str


class MultipleChoiceOptionItem(BaseModel):
    key: str
    text: str
    latex: str | None = None
    is_correct: bool = False
    distractor_type: str | None = None
    rationale: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SymbolicCheckResultItem(BaseModel):
    code: str
    message: str
    passed: bool
    details: dict[str, Any] = Field(default_factory=dict)


class QuestionValidationReportItem(BaseModel):
    can_save: bool = True
    warnings: list[dict[str, Any]] = Field(default_factory=list)
    blocking_issues: list[dict[str, Any]] = Field(default_factory=list)
    symbolic_checks: list[SymbolicCheckResultItem] = Field(default_factory=list)


class QuestionResponse(BaseModel):
    id: str
    document_id: str
    sequence_number: int
    marker: str
    marker_number: str
    statement: str
    solution: str | None = None
    answer: str | None = None
    question_type: str = "free_response"
    choices: list[MultipleChoiceOptionItem] = Field(default_factory=list)
    correct_choice: str | None = None
    validation_report: QuestionValidationReportItem = Field(
        default_factory=QuestionValidationReportItem
    )
    generation_method: str | None = None
    solver_code: str | None = None
    formulas: list[QuestionFormulaItem] = Field(default_factory=list)
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str] = Field(default_factory=list)

    subject_code: str | None = None

    chapter_code: str | None = None
    chapter_name: str | None = None
    topic_code: str | None = None
    topic_name: str | None = None
    problem_type_code: str | None = None
    problem_type_name: str | None = None

    taxonomy_id: str | None = None
    taxonomy_version: str | None = None
    taxonomy_confidence: float | None = None
    taxonomy_reason: str | None = None
    review_status: str | None = None

    classification_status: str
    classification_model: str | None = None
    classification_error: str | None = None
    classified_at: datetime | None = None

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


class QuestionReviewStatusUpdateRequest(BaseModel):
    review_status: str = Field(min_length=1)


class DocumentClassificationResponse(BaseModel):
    document_id: str
    question_count: int = Field(ge=0)
    success_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)

class TaxonomyQualityIssueResponse(BaseModel):
    code: str
    message: str
    severity: str
    field: str | None = None


class TaxonomyQualityReportResponse(BaseModel):
    question_id: str
    can_accept: bool
    warnings: list[TaxonomyQualityIssueResponse] = Field(default_factory=list)
    blocking_issues: list[TaxonomyQualityIssueResponse] = Field(default_factory=list)
