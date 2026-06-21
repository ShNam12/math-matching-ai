import asyncio
from types import SimpleNamespace

from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    MultipleChoiceOption,
)
from modules.question_quality.service import QuestionQualityService


def make_source_question():
    return SimpleNamespace(
        id="source-id",
        document_id="document-id",
        statement="Tinh dao ham cua $y=x$.",
        solution=None,
        answer="1",
        subject="math",
        chapter="calculus",
        difficulty="easy",
        skills=["derivative"],
    )


def make_choice(
    key: str,
    text: str,
    *,
    is_correct: bool = False,
):
    return MultipleChoiceOption(
        key=key,
        text=text,
        is_correct=is_correct,
    )


def make_candidate(
    *,
    correct_text: str = "1",
    solver_code: str | None = "DERIV_MONOMIAL",
    choices: list[MultipleChoiceOption] | None = None,
) -> GeneratedQuestionCandidate:
    return GeneratedQuestionCandidate(
        statement="Tinh dao ham cua $y=x$.",
        solution="$(x)'=1$.",
        answer=correct_text,
        subject="math",
        chapter="calculus",
        difficulty="easy",
        skills=["derivative"],
        formulas=[
            {
                "latex": "x",
                "normalized_latex": "x",
                "source": "statement",
            }
        ],
        quality_warnings=[],
        question_type="multiple_choice",
        choices=choices
        or [
            make_choice("A", "0"),
            make_choice("B", correct_text, is_correct=True),
            make_choice("C", "2"),
            make_choice("D", "-1"),
        ],
        correct_choice="B",
        solver_code=solver_code,
    )


def assess(candidate: GeneratedQuestionCandidate):
    return asyncio.run(
        QuestionQualityService().assess_candidate(
            candidate=candidate,
            source_question=make_source_question(),
            existing_questions=[],
            requested_difficulty="easy",
        )
    )


def test_mcq_with_solver_and_correct_answer_passes() -> None:
    report = assess(make_candidate())

    assert report.can_save is True
    assert "symbolic_correct_answer_mismatch" not in report.quality_warnings
    assert any(
        check.code == "symbolic_correct_answer_verified"
        and check.passed is True
        for check in report.symbolic_checks
    )


def test_mcq_with_solver_and_wrong_answer_fails() -> None:
    report = assess(make_candidate(correct_text="2"))

    assert report.can_save is False
    assert "symbolic_correct_answer_mismatch" in report.quality_warnings


def test_mcq_without_solver_only_warns() -> None:
    report = assess(make_candidate(solver_code=None))

    assert report.can_save is True
    assert "solver_not_available" in report.quality_warnings


def test_mcq_distractor_equal_to_solver_answer_fails() -> None:
    report = assess(
        make_candidate(
            choices=[
                make_choice("A", "0"),
                make_choice("B", "1", is_correct=True),
                make_choice("C", "1"),
                make_choice("D", "-1"),
            ]
        )
    )

    assert report.can_save is False
    assert "symbolic_distractor_equals_correct" in report.quality_warnings


def test_mcq_symbolic_duplicate_distractor_fails() -> None:
    report = assess(
        make_candidate(
            choices=[
                make_choice("A", "x + 1"),
                make_choice("B", "1", is_correct=True),
                make_choice("C", "1 + x"),
                make_choice("D", "-1"),
            ]
        )
    )

    assert report.can_save is False
    assert "symbolic_distractor_duplicate" in report.quality_warnings
