from pydantic import BaseModel, Field


class QuestionSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)
    subject: str | None = None
    chapter: str | None = None
    chapter_code: str | None = None
    topic_code: str | None = None
    problem_type_code: str | None = None
    difficulty: str | None = None
    skill: str | None = None

class QuestionSearchItem(BaseModel):
    question_id: str
    document_id: str
    score: float
    marker: str
    marker_number: str
    statement: str
    solution: str | None = None
    answer: str | None = None
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str]
    subject_code: str | None = None
    chapter_code: str | None = None
    chapter_name: str | None = None
    topic_code: str | None = None
    topic_name: str | None = None
    problem_type_code: str | None = None
    problem_type_name: str | None = None
    taxonomy_confidence: float | None = None
    review_status: str | None = None
    classification_status: str


class QuestionSearchResponse(BaseModel):
    query: str
    results: list[QuestionSearchItem]

class FormulaSearchRequest(BaseModel):
    latex: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)
    source: str | None = None


class FormulaSearchItem(BaseModel):
    question_id: str
    document_id: str
    formula_index: int
    latex: str
    normalized_latex: str
    source: str
    score: float
    marker: str
    marker_number: str
    statement: str
    solution: str | None = None
    answer: str | None = None
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str]


class FormulaSearchResponse(BaseModel):
    latex: str
    results: list[FormulaSearchItem]