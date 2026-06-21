import pytest

from modules.neuro_symbolic import (
    SolverDefinition,
    SolverNotFoundError,
    SolverOutput,
    SolverRegistry,
)


def fake_solver(params: dict[str, object]) -> SolverOutput:
    return SolverOutput(
        statement="statement",
        solution="solution",
        answer="answer",
    )


def test_registry_lists_builtin_solvers() -> None:
    registry = SolverRegistry()

    solver_codes = [
        solver.code
        for solver in registry.list_solvers()
    ]

    assert "INT_MONOMIAL" in solver_codes
    assert "DERIV_MONOMIAL" in solver_codes


def test_registry_gets_solver_by_code() -> None:
    registry = SolverRegistry()

    solver = registry.get_solver("int_monomial")

    assert solver.code == "INT_MONOMIAL"
    assert solver.name == "Indefinite integral of a monomial"
    assert solver.param_schema["required"] == ["coefficient", "power"]


def test_registry_missing_solver_returns_clear_error() -> None:
    registry = SolverRegistry()

    with pytest.raises(SolverNotFoundError, match="Solver not found: MISSING"):
        registry.get_solver("missing")


def test_registry_rejects_duplicate_solver_code() -> None:
    solver = SolverDefinition(
        code="SAMPLE",
        name="Sample solver",
        param_schema={},
        solve=fake_solver,
    )
    registry = SolverRegistry([solver])

    with pytest.raises(ValueError, match="Duplicate solver code: SAMPLE"):
        registry.register(solver)

