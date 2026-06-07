from dataclasses import dataclass


@dataclass(frozen=True)
class QuestionSearchFilters:
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None


@dataclass(frozen=True)
class QuestionSearchVectorHit:
    question_id: str
    document_id: str
    score: float


@dataclass(frozen=True)
class QuestionSearchResult:
    question_id: str
    document_id: str
    score: float
    marker: str
    marker_number: str
    statement: str
    solution: str | None
    answer: str | None
    subject: str | None
    chapter: str | None
    difficulty: str | None
    skills: list[str]

@dataclass(frozen=True)
class FormulaSearchFilters:
    source: str | None = None


@dataclass(frozen=True)
class FormulaSearchVectorHit:
    question_id: str
    document_id: str
    formula_index: int
    latex: str
    normalized_latex: str
    source: str
    score: float


@dataclass(frozen=True)
class FormulaSearchResult:
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
    solution: str | None
    answer: str | None
    subject: str | None
    chapter: str | None
    difficulty: str | None
    skills: list[str]