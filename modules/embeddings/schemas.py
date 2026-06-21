from dataclasses import dataclass


@dataclass(frozen=True)
class QuestionVector:
    question_id: str
    document_id: str
    sequence_number: int
    marker: str
    marker_number: str
    statement: str
    question_type: str
    subject: str | None
    chapter: str | None
    difficulty: str | None
    skills: list[str]

    subject_code: str | None
    chapter_code: str | None
    chapter_name: str | None
    topic_code: str | None
    topic_name: str | None
    problem_type_code: str | None
    problem_type_name: str | None
    taxonomy_confidence: float | None
    review_status: str | None
    classification_status: str

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
