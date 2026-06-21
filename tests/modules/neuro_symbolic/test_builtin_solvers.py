import sympy as sp

from modules.neuro_symbolic import SolverExecutor, SolverRegistry


EXPECTED_PORTED_SOLVERS = {
    "INT_XN_EXP",
    "INT_XN_LN",
    "INT_RATIONAL",
    "DET_2X2",
    "DET_3X3",
    "LIMIT_ZERO_ZERO",
    "DERIV_COMPOSITE",
}


def test_builtin_solver_codes_are_unique() -> None:
    registry = SolverRegistry()

    codes = [
        solver.code
        for solver in registry.list_solvers()
    ]

    assert len(codes) == len(set(codes))
    assert EXPECTED_PORTED_SOLVERS.issubset(set(codes))


def test_builtin_solvers_have_param_schema_and_test_cases() -> None:
    registry = SolverRegistry()

    for solver in registry.list_solvers():
        if solver.code not in EXPECTED_PORTED_SOLVERS:
            continue

        assert solver.param_schema
        assert solver.param_schema["type"] == "object"
        assert solver.test_cases
        assert len(solver.test_cases) >= 2


def test_builtin_solver_test_cases_match_expected_symbolically() -> None:
    registry = SolverRegistry()
    executor = SolverExecutor(registry)

    for solver in registry.list_solvers():
        if solver.code not in EXPECTED_PORTED_SOLVERS:
            continue

        for test_case in solver.test_cases:
            result = executor.execute(
                solver.code,
                test_case["input"],
            )

            assert result.success is True, result.error
            assert result.output is not None
            assert result.output.answer_latex

            actual = sp.sympify(result.output.answer)
            expected = sp.sympify(test_case["expected"])
            assert sp.simplify(actual - expected) == 0
