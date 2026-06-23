from dataclasses import dataclass, field
from typing import Any

from modules.question_quality.schemas import QuestionValidationReport

def _clean_optional_text(value: object) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None

@dataclass(frozen=True)
class GenerationConstraints:
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str] = field(default_factory=list)
    note: str | None = None
    preserve_formula_style: bool = True
    avoid_duplicate: bool = True


@dataclass(frozen=True)
class MultipleChoiceOption:
    key: str
    text: str
    latex: str | None = None
    is_correct: bool = False
    distractor_type: str | None = None
    rationale: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_key = self.key.strip().upper()

        if not normalized_key:
            raise ValueError("Multiple choice option key must not be empty")

        if not isinstance(self.is_correct, bool):
            raise ValueError("Multiple choice option is_correct must be a boolean")

        object.__setattr__(self, "key", normalized_key)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "text": self.text,
            "latex": self.latex,
            "is_correct": self.is_correct,
            "distractor_type": self.distractor_type,
            "rationale": self.rationale,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MultipleChoiceOption":
        text = _clean_optional_text(payload.get("text"))
        latex = _clean_optional_text(payload.get("latex"))

        return cls(
            key=str(payload.get("key") or ""),
            text=text or latex or "",
            latex=latex,
            is_correct=payload.get("is_correct", False),
            distractor_type=(
                str(payload["distractor_type"])
                if payload.get("distractor_type") is not None
                else None
            ),
            rationale=(
                str(payload["rationale"])
                if payload.get("rationale") is not None
                else None
            ),
            metadata=(
                payload["metadata"]
                if isinstance(payload.get("metadata"), dict)
                else {}
            ),
        )

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
    question_type: str = "free_response"
    choices: list[MultipleChoiceOption] = field(default_factory=list)
    correct_choice: str | None = None
    symbolic_answer: str | None = None
    generation_method: str | None = None
    solver_code: str | None = None
    validation_report: QuestionValidationReport = field(
        default_factory=QuestionValidationReport
    )

    def __post_init__(self) -> None:
        if self.question_type not in {"free_response", "multiple_choice"}:
            raise ValueError(
                "question_type must be free_response or multiple_choice"
            )

        if self.correct_choice is not None:
            object.__setattr__(
                self,
                "correct_choice",
                self.correct_choice.strip().upper(),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "statement": self.statement,
            "solution": self.solution,
            "answer": self.answer,
            "subject": self.subject,
            "chapter": self.chapter,
            "difficulty": self.difficulty,
            "skills": self.skills,
            "formulas": self.formulas,
            "quality_warnings": self.quality_warnings,
            "question_type": self.question_type,
            "choices": [choice.to_dict() for choice in self.choices],
            "correct_choice": self.correct_choice,
            "symbolic_answer": self.symbolic_answer,
            "generation_method": self.generation_method,
            "solver_code": self.solver_code,
            "validation_report": self.validation_report.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GeneratedQuestionCandidate":
        choices = payload.get("choices")

        return cls(
            statement=str(payload.get("statement") or ""),
            solution=(
                str(payload["solution"])
                if payload.get("solution") is not None
                else None
            ),
            answer=(
                str(payload["answer"])
                if payload.get("answer") is not None
                else None
            ),
            subject=(
                str(payload["subject"])
                if payload.get("subject") is not None
                else None
            ),
            chapter=(
                str(payload["chapter"])
                if payload.get("chapter") is not None
                else None
            ),
            difficulty=(
                str(payload["difficulty"])
                if payload.get("difficulty") is not None
                else None
            ),
            skills=[
                str(skill)
                for skill in payload.get("skills", [])
            ] if isinstance(payload.get("skills"), list) else [],
            formulas=[
                formula
                for formula in payload.get("formulas", [])
                if isinstance(formula, dict)
            ] if isinstance(payload.get("formulas"), list) else [],
            quality_warnings=[
                str(warning)
                for warning in payload.get("quality_warnings", [])
            ] if isinstance(payload.get("quality_warnings"), list) else [],
            question_type=str(payload.get("question_type") or "free_response"),
            choices=[
                MultipleChoiceOption.from_dict(choice)
                for choice in choices
                if isinstance(choice, dict)
            ] if isinstance(choices, list) else [],
            correct_choice=(
                str(payload["correct_choice"])
                if payload.get("correct_choice") is not None
                else None
            ),
            symbolic_answer=(
                str(payload["symbolic_answer"])
                if payload.get("symbolic_answer") is not None
                else None
            ),
            generation_method=(
                str(payload["generation_method"])
                if payload.get("generation_method") is not None
                else None
            ),
            solver_code=(
                str(payload["solver_code"])
                if payload.get("solver_code") is not None
                else None
            ),
            validation_report=QuestionValidationReport.from_dict(
                payload.get("validation_report")
                if isinstance(payload.get("validation_report"), dict)
                else None
            ),
        )


@dataclass(frozen=True)
class QuestionGenerationPreview:
    source_question_id: str
    candidates: list[GeneratedQuestionCandidate]
