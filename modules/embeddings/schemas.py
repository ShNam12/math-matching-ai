from dataclasses import dataclass


@dataclass(frozen=True)
class QuestionVector:
    question_id: str
    document_id: str
    sequence_number: int
    marker: str
    marker_number: str
    statement: str
    subject: str | None
    chapter: str | None
    difficulty: str | None
    skills: list[str]
    vector: list[float]


@dataclass(frozen=True)
class FormulaVector:
    question_id: str
    document_id: str
    formula_index: int
    latex: str
    normalized_latex: str
    source: str
    vector: list[float]


@dataclass(frozen=True)
class EmbeddingResult:
    document_id: str
    question_count: int
    formula_count: int