from pydantic import BaseModel, Field


class QuestionSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None


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