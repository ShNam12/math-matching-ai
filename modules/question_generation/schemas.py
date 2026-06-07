from dataclasses import dataclass, field


@dataclass(frozen=True)
class GenerationConstraints:
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str] = field(default_factory=list)
    preserve_formula_style: bool = True
    avoid_duplicate: bool = True


@dataclass(frozen=True)
class GeneratedQuestionCandidate:
    statement: str
    solution: str | None
    answer: str | None
    subject: str | None
    chapter: str | None
    difficulty: str | None
    skills: list[str]
    formulas: list[dict[str, str]]
    quality_warnings: list[str]


@dataclass(frozen=True)
class QuestionGenerationPreview:
    source_question_id: str
    candidates: list[GeneratedQuestionCandidate]