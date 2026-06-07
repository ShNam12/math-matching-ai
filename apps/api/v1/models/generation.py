from pydantic import BaseModel, Field


class GenerationConstraintsRequest(BaseModel):
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str] = Field(default_factory=list)
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
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str] = Field(default_factory=list)
    formulas: list[GeneratedFormulaItem] = Field(default_factory=list)
    quality_warnings: list[str] = Field(default_factory=list)


class QuestionGenerationPreviewResponse(BaseModel):
    source_question_id: str
    candidates: list[GeneratedQuestionCandidateItem]


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
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str]
    formulas: list[GeneratedFormulaItem]
    embedding_status: str