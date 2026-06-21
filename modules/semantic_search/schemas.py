from dataclasses import dataclass


@dataclass(frozen=True)
class QuestionSearchFilters:
    subject: str | None = None
    chapter: str | None = None
    question_type: str | None = None
    chapter_code: str | None = None
    topic_code: str | None = None
    problem_type_code: str | None = None
    difficulty: str | None = None
    skill: str | None = None


@dataclass(frozen=True)
class QuestionSearchVectorHit:
    question_id: str
    document_id: str
    score: float


@dataclass(frozen=True, kw_only=True)
class QuestionSearchResult:
    question_id: str
    document_id: str
    score: float
    semantic_score: float
    taxonomy_score: float
    formula_score: float
    difficulty_score: float
    skill_score: float
    choice_structure_score: float = 0.0
    marker: str
    marker_number: str
    statement: str
    solution: str | None
    answer: str | None
    question_type: str
    choices: list[dict[str, object]]
    correct_choice: str | None
    validation_report: dict[str, object]
    generation_method: str | None
    solver_code: str | None
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
    question_type: str
    choices: list[dict[str, object]]
    correct_choice: str | None
    subject: str | None
    chapter: str | None
    difficulty: str | None
    skills: list[str]
