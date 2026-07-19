from modules.neuro_symbolic.symbolic_validator import SymbolicMCQValidator
from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    MultipleChoiceOption,
)


def make_choice(
    key: str,
    text: str,
    *,
    latex: str | None = None,
    is_correct: bool = False,
) -> MultipleChoiceOption:
    return MultipleChoiceOption(
        key=key,
        text=text,
        latex=latex,
        is_correct=is_correct,
    )


def make_candidate(
    choices: list[MultipleChoiceOption],
    *,
    correct_choice: str = "B",
    solver_code: str | None = "INT_MONOMIAL",
) -> GeneratedQuestionCandidate:
    return GeneratedQuestionCandidate(
        statement="Tinh $\\int 3x^2\\,dx$.",
        solution="Dung cong thuc luy thua.",
        answer="x^3 + C",
        subject="calculus",
        chapter="integral",
        difficulty="easy",
        skills=["integration"],
        formulas=[],
        quality_warnings=[],
        question_type="multiple_choice",
        choices=choices,
        correct_choice=correct_choice,
        solver_code=solver_code,
    )


def validate(candidate: GeneratedQuestionCandidate):
    return SymbolicMCQValidator().validate_candidate(
        candidate,
        params={
            "coefficient": 3,
            "power": 2,
        },
    )


def test_correct_choice_matching_solver_passes() -> None:
    report = validate(
        make_candidate(
            [
                make_choice("A", "x^2 + C"),
                make_choice("B", "x^3 + C", is_correct=True),
                make_choice("C", "3*x^3 + C"),
                make_choice("D", "-x^3 + C"),
            ]
        )
    )

    assert report.can_save is True
    assert report.blocking_issues == []
    assert report.quality_warnings == []
    assert report.symbolic_checks[0].code == "symbolic_correct_answer_verified"
    assert report.symbolic_checks[0].passed is True


def test_validator_parses_raw_text_when_display_latex_is_present() -> None:
    report = validate(
        make_candidate(
            [
                make_choice("A", "x^2 + C", latex=r"x^2 + C"),
                make_choice(
                    "B",
                    "x^3 + C",
                    latex=r"x^3 + C",
                    is_correct=True,
                ),
                make_choice("C", "3*x^3 + C", latex=r"3x^3 + C"),
                make_choice("D", "-x^3 + C", latex=r"-x^3 + C"),
            ]
        )
    )

    assert report.can_save is True
    assert report.symbolic_checks[0].code == "symbolic_correct_answer_verified"


def test_wrong_correct_choice_is_blocking() -> None:
    report = validate(
        make_candidate(
            [
                make_choice("A", "x^2 + C"),
                make_choice("B", "x^2 + C", is_correct=True),
                make_choice("C", "3*x^3 + C"),
                make_choice("D", "-x^3 + C"),
            ]
        )
    )

    assert report.can_save is False
    assert "symbolic_correct_answer_mismatch" in report.quality_warnings
    assert report.blocking_issues[0].field == "correct_choice"


def test_distractor_equal_to_solver_answer_is_blocking() -> None:
    report = validate(
        make_candidate(
            [
                make_choice("A", "x^2 + C"),
                make_choice("B", "x^3 + C", is_correct=True),
                make_choice("C", "x^3 + C"),
                make_choice("D", "-x^3 + C"),
            ]
        )
    )

    assert report.can_save is False
    assert "symbolic_distractor_equals_correct" in report.quality_warnings


def test_symbolically_duplicate_distractors_are_blocking() -> None:
    report = validate(
        make_candidate(
            [
                make_choice("A", "x^2 + 1"),
                make_choice("B", "x^3 + C", is_correct=True),
                make_choice("C", "x + 1"),
                make_choice("D", "1 + x"),
            ]
        )
    )

    assert report.can_save is False
    assert "symbolic_distractor_duplicate" in report.quality_warnings


def test_missing_solver_code_returns_warning_without_crashing() -> None:
    report = validate(
        make_candidate(
            [
                make_choice("A", "x^2 + C"),
                make_choice("B", "x^3 + C", is_correct=True),
                make_choice("C", "3*x^3 + C"),
                make_choice("D", "-x^3 + C"),
            ],
            solver_code=None,
        )
    )

    assert report.can_save is True
    assert "solver_not_available" in report.quality_warnings
    assert report.warnings[0].field == "solver_code"


def test_parse_error_returns_warning() -> None:
    report = validate(
        make_candidate(
            [
                make_choice("A", "not parseable ???"),
                make_choice("B", "x^3 + C", is_correct=True),
                make_choice("C", "3*x^3 + C"),
                make_choice("D", "-x^3 + C"),
            ]
        )
    )

    assert report.can_save is True
    assert "symbolic_parse_failed" in report.quality_warnings
    assert report.warnings[0].field == "choices"
