from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    GenerationConstraints,
    MultipleChoiceOption,
    QuestionGenerationPreview,
)
from modules.question_quality.schemas import QualityIssue, QuestionValidationReport
import pytest


def test_generation_constraints_default_values() -> None:
    constraints = GenerationConstraints()

    assert constraints.subject is None
    assert constraints.chapter is None
    assert constraints.difficulty is None
    assert constraints.skills == []
    assert constraints.preserve_formula_style is True
    assert constraints.avoid_duplicate is True


def test_generation_constraints_skills_are_not_shared() -> None:
    first = GenerationConstraints()
    second = GenerationConstraints()

    assert first.skills is not second.skills


def test_generated_question_candidate_stores_generation_payload() -> None:
    candidate = GeneratedQuestionCandidate(
        statement="Tinh $x^2$.",
        solution="Binh phuong x.",
        answer="$x^2$",
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["power"],
        formulas=[
            {
                "latex": "x^2",
                "normalized_latex": "x^2",
                "source": "statement",
            }
        ],
        quality_warnings=[],
    )

    assert candidate.statement == "Tinh $x^2$."
    assert candidate.solution == "Binh phuong x."
    assert candidate.answer == "$x^2$"
    assert candidate.skills == ["power"]
    assert candidate.formulas[0]["source"] == "statement"
    assert candidate.quality_warnings == []
    assert candidate.question_type == "free_response"
    assert candidate.choices == []
    assert candidate.correct_choice is None
    assert candidate.validation_report.can_save is True


def test_generated_question_candidate_supports_multiple_choice_payload() -> None:
    candidate = GeneratedQuestionCandidate(
        statement="Tinh $1+1$.",
        solution="$1+1=2$.",
        answer="2",
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["addition"],
        formulas=[],
        quality_warnings=[],
        question_type="multiple_choice",
        choices=[
            MultipleChoiceOption(key="A", text="1"),
            MultipleChoiceOption(key="B", text="2", is_correct=True),
            MultipleChoiceOption(key="C", text="3"),
            MultipleChoiceOption(key="D", text="4"),
        ],
        correct_choice="b",
        symbolic_answer="2",
        generation_method="ai_symbolic",
        solver_code="ADD_INT",
        validation_report=QuestionValidationReport(),
    )

    assert candidate.question_type == "multiple_choice"
    assert len(candidate.choices) == 4
    assert candidate.correct_choice == "B"
    assert candidate.choices[1].is_correct is True
    assert candidate.symbolic_answer == "2"
    assert candidate.generation_method == "ai_symbolic"
    assert candidate.solver_code == "ADD_INT"


def test_multiple_choice_option_requires_key() -> None:
    with pytest.raises(ValueError, match="key"):
        MultipleChoiceOption(key=" ", text="2")


def test_multiple_choice_option_requires_boolean_is_correct() -> None:
    with pytest.raises(ValueError, match="boolean"):
        MultipleChoiceOption(key="A", text="2", is_correct="yes")


def test_generated_question_candidate_round_trips_choices() -> None:
    candidate = GeneratedQuestionCandidate(
        statement="Tinh $1+1$.",
        solution="$1+1=2$.",
        answer="2",
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["addition"],
        formulas=[],
        quality_warnings=[],
        question_type="multiple_choice",
        choices=[
            MultipleChoiceOption(key="A", text="1"),
            MultipleChoiceOption(key="B", text="2", is_correct=True),
            MultipleChoiceOption(key="C", text="3"),
            MultipleChoiceOption(key="D", text="4"),
        ],
        correct_choice="B",
        validation_report=QuestionValidationReport(
            blocking_issues=[
                QualityIssue(
                    code="mcq_duplicate_choice_content",
                    message="Duplicate choice content",
                    severity="error",
                    field="choices",
                )
            ]
        ),
    )

    restored = GeneratedQuestionCandidate.from_dict(candidate.to_dict())

    assert restored.question_type == "multiple_choice"
    assert [choice.key for choice in restored.choices] == ["A", "B", "C", "D"]
    assert restored.choices[1].text == "2"
    assert restored.choices[1].is_correct is True
    assert restored.correct_choice == "B"
    assert restored.validation_report.can_save is False
    assert restored.validation_report.blocking_issues[0].code == (
        "mcq_duplicate_choice_content"
    )


def test_question_generation_preview_contains_candidates() -> None:
    candidate = GeneratedQuestionCandidate(
        statement="Tinh $x+1$.",
        solution=None,
        answer=None,
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
        formulas=[
            {
                "latex": "x+1",
                "normalized_latex": "x+1",
                "source": "statement",
            }
        ],
        quality_warnings=[],
    )

    preview = QuestionGenerationPreview(
        source_question_id="source-id",
        candidates=[candidate],
    )

    assert preview.source_question_id == "source-id"
    assert len(preview.candidates) == 1
    assert preview.candidates[0].statement == "Tinh $x+1$."
