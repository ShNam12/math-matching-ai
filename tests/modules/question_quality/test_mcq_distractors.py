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
        statement="Tinh $2+2$.",
        solution=None,
        answer="4",
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["addition"],
    )


def make_choice(
    key: str,
    text: str,
    *,
    latex: str | None = None,
    is_correct: bool = False,
):
    return MultipleChoiceOption(
        key=key,
        text=text,
        latex=latex,
        is_correct=is_correct,
    )


def make_candidate(choices):
    return GeneratedQuestionCandidate(
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
        choices=choices,
        correct_choice="B",
    )


def assess(candidate: GeneratedQuestionCandidate):
    return asyncio.run(
        QuestionQualityService().assess_candidate(
            candidate=candidate,
            source_question=make_source_question(),
            existing_questions=[make_source_question()],
            requested_difficulty="easy",
        )
    )


def assert_blocking_code(candidate, code: str) -> None:
    report = assess(candidate)

    assert report.can_save is False
    assert code in report.quality_warnings


def test_duplicate_choice_text_is_blocking() -> None:
    assert_blocking_code(
        make_candidate(
            [
                make_choice("A", "2"),
                make_choice("B", "2", is_correct=True),
                make_choice("C", "3"),
                make_choice("D", "4"),
            ]
        ),
        "mcq_duplicate_choice_content",
    )


def test_duplicate_choice_latex_is_blocking() -> None:
    assert_blocking_code(
        make_candidate(
            [
                make_choice("A", "one", latex="x+1"),
                make_choice("B", "two", latex="2", is_correct=True),
                make_choice("C", "same as A", latex="x + 1"),
                make_choice("D", "four", latex="4"),
            ]
        ),
        "mcq_duplicate_choice_content",
    )


def test_symbolically_equivalent_choices_are_blocking() -> None:
    assert_blocking_code(
        make_candidate(
            [
                make_choice("A", "x+1"),
                make_choice("B", "2", is_correct=True),
                make_choice("C", "1+x"),
                make_choice("D", "x+2"),
            ]
        ),
        "mcq_duplicate_choice_content",
    )


def test_distractor_equal_to_correct_answer_is_blocking() -> None:
    candidate = make_candidate(
        [
            make_choice("A", "1"),
            make_choice("B", "2", is_correct=True),
            make_choice("C", "1+1"),
            make_choice("D", "4"),
        ]
    )
    report = assess(candidate)

    assert report.can_save is False
    assert "mcq_distractor_equals_correct_answer" in report.quality_warnings


def test_distinct_distractors_pass_duplicate_validation() -> None:
    report = assess(
        make_candidate(
            [
                make_choice("A", "1"),
                make_choice("B", "2", is_correct=True),
                make_choice("C", "3"),
                make_choice("D", "4"),
            ]
        )
    )

    assert report.can_save is True
    assert "mcq_duplicate_choice_content" not in report.quality_warnings
    assert "mcq_distractor_equals_correct_answer" not in report.quality_warnings


def test_symbolic_parse_failure_does_not_crash() -> None:
    report = assess(
        make_candidate(
            [
                make_choice("A", "half", latex=r"\frac{1}{2}"),
                make_choice("B", "one", latex="1", is_correct=True),
                make_choice("C", "root", latex=r"\sqrt{2}"),
                make_choice("D", "pi", latex=r"\pi"),
            ]
        )
    )

    assert report.can_save is True
    assert "mcq_duplicate_choice_content" not in report.quality_warnings


def test_all_choices_too_similar_is_blocking() -> None:
    report = assess(
        make_candidate(
            [
                make_choice("A", "2"),
                make_choice("B", "2", is_correct=True),
                make_choice("C", "2"),
                make_choice("D", "2"),
            ]
        )
    )

    assert report.can_save is False
    assert "mcq_all_choices_too_similar" in report.quality_warnings
