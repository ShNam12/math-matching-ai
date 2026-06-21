from modules.neuro_symbolic import (
    SolverDefinition,
    SolverExecutor,
    SolverOutput,
    SolverRegistry,
)


def failing_solver(params: dict[str, object]) -> SolverOutput:
    raise RuntimeError("sample solver failed")


def test_execute_sample_integral_solver() -> None:
    executor = SolverExecutor()

    result = executor.execute(
        "INT_MONOMIAL",
        {
            "coefficient": 3,
            "power": 2,
        },
    )

    assert result.success is True
    assert result.solver_code == "INT_MONOMIAL"
    assert result.output is not None
    assert result.output.answer == "x^3 + C"
    assert "\\int 3x^2" in result.output.statement


def test_execute_sample_derivative_solver() -> None:
    executor = SolverExecutor()

    result = executor.execute(
        "DERIV_MONOMIAL",
        {
            "coefficient": 4,
            "power": 3,
        },
    )

    assert result.success is True
    assert result.output is not None
    assert result.output.answer == "12x^2"


def test_execute_missing_solver_returns_failure_result() -> None:
    executor = SolverExecutor()

    result = executor.execute("missing", {})

    assert result.success is False
    assert result.solver_code == "MISSING"
    assert result.output is None
    assert result.error == "Solver not found: MISSING"


def test_solver_exception_does_not_crash_executor() -> None:
    registry = SolverRegistry(
        [
            SolverDefinition(
                code="FAIL_SAMPLE",
                name="Failing sample",
                param_schema={},
                solve=failing_solver,
            )
        ]
    )
    executor = SolverExecutor(registry)

    result = executor.execute("FAIL_SAMPLE", {})

    assert result.success is False
    assert result.solver_code == "FAIL_SAMPLE"
    assert result.output is None
    assert result.error == "sample solver failed"
