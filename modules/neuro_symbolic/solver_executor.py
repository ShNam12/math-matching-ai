from modules.neuro_symbolic.schemas import SolverExecutionResult
from modules.neuro_symbolic.solver_registry import SolverRegistry


class SolverExecutor:
    def __init__(
        self,
        registry: SolverRegistry | None = None,
    ) -> None:
        self.registry = registry or SolverRegistry()

    def execute(
        self,
        solver_code: str,
        params: dict[str, object] | None = None,
    ) -> SolverExecutionResult:
        normalized_code = solver_code.strip().upper()

        try:
            solver = self.registry.get_solver(normalized_code)
            output = solver.solve(params or {})
        except Exception as exc:
            return SolverExecutionResult(
                solver_code=normalized_code,
                success=False,
                error=str(exc),
            )

        return SolverExecutionResult(
            solver_code=solver.code,
            success=True,
            output=output,
        )

