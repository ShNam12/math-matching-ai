import sympy as sp

from modules.neuro_symbolic import DistractorCandidate, DistractorService


def assert_not_equivalent(left: str, right: str) -> None:
    assert sp.simplify(sp.sympify(left) - sp.sympify(right)) != 0


def test_generate_three_unique_distractors_when_possible() -> None:
    service = DistractorService()

    distractors = service.generate(
        correct_answer="x + 1",
        params={"a": 2, "n": 3},
        strategies=[
            "sign_error",
            "coefficient_error",
            "partial_result",
            "swap_operands",
        ],
        count=3,
    )

    assert len(distractors) == 3
    assert all(isinstance(item, DistractorCandidate) for item in distractors)
    assert len({item.value for item in distractors}) == 3
    assert all(item.value != "x + 1" for item in distractors)
    for item in distractors:
        assert_not_equivalent(item.value, "x + 1")
        assert item.latex
        assert item.text
        assert item.rationale


def test_sign_error_works_with_number_and_expression() -> None:
    service = DistractorService()

    number = service.generate(
        correct_answer=5,
        params={},
        strategies=["sign_error"],
        count=1,
    )
    expression = service.generate(
        correct_answer="x + 1",
        params={},
        strategies=["sign_error"],
        count=1,
    )

    assert number[0].value == "-5"
    assert expression[0].value == "-x - 1"


def test_coefficient_error_creates_non_correct_answer() -> None:
    service = DistractorService()

    distractors = service.generate(
        correct_answer="x + 1",
        params={"a": 3},
        strategies=["coefficient_error"],
        count=1,
    )

    assert len(distractors) == 1
    assert distractors[0].error_type == "coefficient_error"
    assert_not_equivalent(distractors[0].value, "x + 1")


def test_adjacent_param_uses_solver_func() -> None:
    service = DistractorService()

    def solver_func(params):
        return sp.Integer(params["n"] + 10)

    distractors = service.generate(
        correct_answer=11,
        params={"n": 1},
        strategies=["adjacent_param"],
        count=1,
        solver_func=solver_func,
    )

    assert len(distractors) == 1
    assert distractors[0].value == "12"
    assert distractors[0].error_type == "adjacent_param"


def test_strategy_failure_is_skipped_and_later_strategy_continues() -> None:
    service = DistractorService()

    distractors = service.generate(
        correct_answer="x + 1",
        params={},
        strategies=["unknown_strategy", "sign_error"],
        count=1,
    )

    assert len(distractors) == 1
    assert distractors[0].error_type == "sign_error"


def test_generate_does_not_crash_with_plain_string_answer() -> None:
    service = DistractorService()

    distractors = service.generate(
        correct_answer="khong xac dinh",
        params={},
        strategies=[
            "sign_error",
            "coefficient_error",
            "random_variation",
        ],
        count=3,
    )

    assert len(distractors) == 3
    assert len({item.value for item in distractors}) == 3
    assert all(item.value != "khong xac dinh" for item in distractors)


def test_duplicate_and_correct_equivalent_distractors_are_filtered() -> None:
    service = DistractorService()

    distractors = service.generate(
        correct_answer="x + 1",
        params={},
        strategies=[
            "swap_operands",
            "sign_error",
            "sign_error",
            "random_variation",
        ],
        count=2,
    )

    assert len(distractors) == 2
    assert len({item.value for item in distractors}) == 2
    for item in distractors:
        assert_not_equivalent(item.value, "x + 1")
