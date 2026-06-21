import pytest

from modules.neuro_symbolic import (
    DEFAULT_PROBLEM_TYPE_SOLVER_MAP,
    SolverRegistry,
    TemplateMatcher,
)


def test_maps_problem_type_code_to_solver() -> None:
    matcher = TemplateMatcher()

    result = matcher.match(
        problem_type_code="GT1_C2_01_T03_Integration_By_Parts",
    )

    assert result is not None
    assert result.solver_code == "INT_XN_EXP"
    assert result.matched_by == "problem_type_code"
    assert result.solver.code == "INT_XN_EXP"


def test_missing_mapping_returns_none() -> None:
    matcher = TemplateMatcher()

    result = matcher.match(
        problem_type_code="UNKNOWN_PROBLEM_TYPE",
    )

    assert result is None


def test_requested_solver_code_has_priority() -> None:
    matcher = TemplateMatcher()

    result = matcher.match(
        problem_type_code="GT1_C2_01_T03_Integration_By_Parts",
        requested_solver_code="INT_XN_LN",
    )

    assert result is not None
    assert result.solver_code == "INT_XN_LN"
    assert result.matched_by == "requested_solver_code"


def test_unknown_requested_solver_falls_back_to_problem_type_mapping() -> None:
    matcher = TemplateMatcher()

    result = matcher.match(
        problem_type_code="GT1_C2_01_T03_Integration_By_Parts",
        requested_solver_code="MISSING_SOLVER",
    )

    assert result is not None
    assert result.solver_code == "INT_XN_EXP"
    assert result.matched_by == "problem_type_code"


def test_mapping_does_not_contain_unknown_solver_codes() -> None:
    registry = SolverRegistry()

    for solver_codes in DEFAULT_PROBLEM_TYPE_SOLVER_MAP.values():
        for solver_code in solver_codes:
            assert registry.get_solver(solver_code).code == solver_code


def test_invalid_custom_mapping_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="UNKNOWN_SOLVER"):
        TemplateMatcher(
            problem_type_solver_map={
                "SOME_PROBLEM": ["UNKNOWN_SOLVER"],
            }
        )


def test_no_problem_type_and_no_requested_solver_returns_none() -> None:
    matcher = TemplateMatcher()

    assert matcher.match() is None
