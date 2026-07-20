from typing import Any, Literal

from pydantic import BaseModel, Field

from apps.api.v1.models.questions import (
    MultipleChoiceOptionItem,
    QuestionValidationReportItem,
    SymbolicCheckResultItem,
)


class GenerationConstraintsRequest(BaseModel):
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str] = Field(default_factory=list)
    note: str | None = None
    preserve_formula_style: bool = True
    avoid_duplicate: bool = True


class QuestionGenerationPreviewRequest(BaseModel):
    source_question_id: str = Field(min_length=1)
    generation_count: int = Field(default=3, ge=1, le=10)
    constraints: GenerationConstraintsRequest | None = None


class GeneratedFormulaItem(BaseModel):
    latex: str
    normalized_latex: str
    source: str


class GeneratedQuestionCandidateItem(BaseModel):
    statement: str
    solution: str | None = None
    answer: str | None = None
    question_type: str = "free_response"
    choices: list[MultipleChoiceOptionItem] = Field(default_factory=list)
    correct_choice: str | None = None
    symbolic_answer: str | None = None
    generation_method: str | None = None
    solver_code: str | None = None
    validation_report: QuestionValidationReportItem = Field(
        default_factory=QuestionValidationReportItem
    )
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str] = Field(default_factory=list)
    formulas: list[GeneratedFormulaItem] = Field(default_factory=list)
    quality_warnings: list[str] = Field(default_factory=list)


class QuestionGenerationPreviewResponse(BaseModel):
    source_question_id: str
    candidates: list[GeneratedQuestionCandidateItem]


class ConvertToMCQPreviewRequest(BaseModel):
    generation_count: int = Field(default=1, ge=1, le=10)
    constraints: GenerationConstraintsRequest | None = None


class ConvertToMCQSaveRequest(BaseModel):
    candidate: GeneratedQuestionCandidateItem


class SymbolicMCQPreviewRequest(BaseModel):
    solver_code: str = Field(min_length=1)
    generation_count: int = Field(default=3, ge=1, le=10)
    difficulty: str | None = None
    subject: str | None = None
    chapter: str | None = None
    skills: list[str] = Field(default_factory=list)
    taxonomy: dict[str, Any] = Field(default_factory=dict)
    seed: int | None = None


class SymbolicMCQPreviewResponse(BaseModel):
    solver_code: str
    candidates: list[GeneratedQuestionCandidateItem]


class SymbolicMCQSolverItem(BaseModel):
    code: str
    name: str
    taxonomy_hint: str | None = None
    param_schema: dict[str, Any]


class SymbolicMCQSolversResponse(BaseModel):
    solvers: list[SymbolicMCQSolverItem]


class QuestionGenerationSaveRequest(BaseModel):
    source_question_id: str = Field(min_length=1)
    candidate: GeneratedQuestionCandidateItem


class QuestionGenerationSaveResponse(BaseModel):
    question_id: str
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
    review_status: str | None = None
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str]
    formulas: list[GeneratedFormulaItem]
    embedding_status: str
    classification_status: str
    classification_error: str | None = None
    chapter_code: str | None = None
    topic_code: str | None = None
    problem_type_code: str | None = None

class QuestionGenerationQualityRequest(BaseModel):
    source_question_id: str = Field(min_length=1)
    requested_difficulty: str | None = None
    candidate: GeneratedQuestionCandidateItem


class QualityIssueItem(BaseModel):
    code: str
    message: str
    severity: str
    field: str | None = None


class SemanticDuplicateItem(BaseModel):
    question_id: str
    document_id: str
    score: float
    statement: str


class QualityRuleResultItem(BaseModel):
    rule_id: str
    title: str
    category: str
    status: Literal["pass", "warn", "fail", "skipped"]
    issues: list[QualityIssueItem] = Field(default_factory=list)
    check_codes: list[str] = Field(default_factory=list)


class QuestionGenerationQualityResponse(BaseModel):
    can_save: bool
    quality_warnings: list[str]
    warnings: list[QualityIssueItem]
    blocking_issues: list[QualityIssueItem]
    symbolic_checks: list[SymbolicCheckResultItem] = Field(default_factory=list)
    semantic_duplicates: list[SemanticDuplicateItem]
    rule_results: list[QualityRuleResultItem] = Field(default_factory=list)
