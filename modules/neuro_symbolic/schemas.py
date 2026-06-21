from dataclasses import dataclass, field
from typing import Any, Callable


SolverFunction = Callable[[dict[str, Any]], "SolverOutput"]


@dataclass(frozen=True)
class SolverOutput:
    statement: str
    solution: str
    answer: str
    answer_latex: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SolverDefinition:
    code: str
    name: str
    param_schema: dict[str, Any]
    solve: SolverFunction
    taxonomy_hint: str | None = None
    statement_template: str | None = None
    solution_template: str | None = None
    answer_expression: str | None = None
    test_cases: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        normalized_code = self.code.strip().upper()

        if not normalized_code:
            raise ValueError("Solver code must not be empty")

        if not self.name.strip():
            raise ValueError("Solver name must not be empty")

        object.__setattr__(self, "code", normalized_code)


@dataclass(frozen=True)
class SolverExecutionResult:
    solver_code: str
    success: bool
    output: SolverOutput | None = None
    error: str | None = None


@dataclass(frozen=True)
class DistractorCandidate:
    value: str
    latex: str
    text: str
    error_type: str
    rationale: str
