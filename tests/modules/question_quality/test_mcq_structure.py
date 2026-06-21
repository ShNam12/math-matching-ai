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
        answer="2",
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["addition"],
    )


def make_choice(key: str, text: str, *, is_correct: bool = False):
    return MultipleChoiceOption(
        key=key,
        text=text,
        is_correct=is_correct,
    )


def make_mcq_candidate(
    *,
    choices=None,
    correct_choice: str | None = "B",
):
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
        choices=choices if choices is not None else [
            make_choice("A", "1"),
            make_choice("B", "2", is_correct=True),
            make_choice("C", "3"),
            make_choice("D", "4"),
        ],
        correct_choice=correct_choice,
    )


def assess(candidate: GeneratedQuestionCandidate):
    service = QuestionQualityService()
    source_question = make_source_question()

    return asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
            requested_difficulty="easy",
        )
    )


def assert_blocking_code(candidate, code: str) -> None:
    report = assess(candidate)

    assert report.can_save is False
    assert code in report.quality_warnings


def test_valid_mcq_structure_passes() -> None:
    report = assess(make_mcq_candidate())

    assert report.can_save is True
    assert not [
        code
        for code in report.quality_warnings
        if code.startswith("mcq_")
    ]


def test_mcq_missing_choices_is_blocking() -> None:
    assert_blocking_code(
        make_mcq_candidate(choices=[]),
        "mcq_missing_choices",
    )


def test_mcq_invalid_choice_count_is_blocking() -> None:
    assert_blocking_code(
        make_mcq_candidate(
            choices=[
                make_choice("A", "1"),
                make_choice("B", "2", is_correct=True),
                make_choice("C", "3"),
            ]
        ),
        "mcq_invalid_choice_count",
    )


def test_mcq_invalid_choice_key_is_blocking() -> None:
    assert_blocking_code(
        make_mcq_candidate(
            choices=[
                make_choice("A", "1"),
                make_choice("B", "2", is_correct=True),
                make_choice("C", "3"),
                make_choice("E", "4"),
            ]
        ),
        "mcq_invalid_choice_key",
    )


def test_mcq_duplicate_choice_key_is_blocking() -> None:
    assert_blocking_code(
        make_mcq_candidate(
            choices=[
                make_choice("A", "1"),
                make_choice("B", "2", is_correct=True),
                make_choice("B", "3"),
                make_choice("D", "4"),
            ]
        ),
        "mcq_duplicate_choice_key",
    )


def test_mcq_missing_correct_choice_is_blocking() -> None:
    assert_blocking_code(
        make_mcq_candidate(correct_choice=None),
        "mcq_missing_correct_choice",
    )


def test_mcq_correct_choice_not_found_is_blocking() -> None:
    assert_blocking_code(
        make_mcq_candidate(correct_choice="E"),
        "mcq_correct_choice_not_found",
    )


def test_mcq_correct_choice_must_match_flagged_choice() -> None:
    assert_blocking_code(
        make_mcq_candidate(correct_choice="A"),
        "mcq_correct_choice_not_found",
    )


def test_mcq_multiple_correct_choices_is_blocking() -> None:
    assert_blocking_code(
        make_mcq_candidate(
            choices=[
                make_choice("A", "1", is_correct=True),
                make_choice("B", "2", is_correct=True),
                make_choice("C", "3"),
                make_choice("D", "4"),
            ]
        ),
        "mcq_multiple_correct_choices",
    )


def test_mcq_no_correct_choice_flagged_is_blocking() -> None:
    assert_blocking_code(
        make_mcq_candidate(
            choices=[
                make_choice("A", "1"),
                make_choice("B", "2"),
                make_choice("C", "3"),
                make_choice("D", "4"),
            ]
        ),
        "mcq_no_correct_choice_flagged",
    )


def test_mcq_empty_choice_text_is_blocking() -> None:
    assert_blocking_code(
        make_mcq_candidate(
            choices=[
                make_choice("A", "1"),
                make_choice("B", "2", is_correct=True),
                make_choice("C", " "),
                make_choice("D", "4"),
            ]
        ),
        "mcq_empty_choice_text",
    )


def test_free_response_does_not_require_choices() -> None:
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
        question_type="free_response",
        choices=[],
        correct_choice=None,
    )

    report = assess(candidate)

    assert report.can_save is True
    assert "mcq_missing_choices" not in report.quality_warnings
