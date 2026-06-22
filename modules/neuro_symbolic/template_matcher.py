from dataclasses import dataclass

from modules.neuro_symbolic.schemas import SolverDefinition
from modules.neuro_symbolic.solver_registry import SolverRegistry


DEFAULT_PROBLEM_TYPE_SOLVER_MAP: dict[str, list[str]] = {
    "GT1_C2_01_T03_Integration_By_Parts": ["INT_XN_EXP", "INT_XN_LN"],
    "GT1_C1_05_T02_Algebraic_Transformation_Limit": ["LIMIT_ZERO_ZERO"],
    "GT1_C3_01_T01_Composite_Derivative": ["DERIV_COMPOSITE"],
}


@dataclass(frozen=True)
class TemplateMatchResult:
    solver_code: str
    solver: SolverDefinition
    matched_by: str
    problem_type_code: str | None = None


class TemplateMatcher:
    def __init__(
        self,
        *,
        registry: SolverRegistry | None = None,
        problem_type_solver_map: dict[str, list[str]] | None = None,
    ) -> None:
        self.registry = registry or SolverRegistry()
        self.problem_type_solver_map = (
            problem_type_solver_map or DEFAULT_PROBLEM_TYPE_SOLVER_MAP
        )
        self._validate_mapping()

    def match(
        self,
        *,
        problem_type_code: str | None = None,
        requested_solver_code: str | None = None,
    ) -> TemplateMatchResult | None:
        if requested_solver_code:
            solver = self._get_existing_solver(requested_solver_code)

            if solver is not None:
                return TemplateMatchResult(
                    solver_code=solver.code,
                    solver=solver,
                    matched_by="requested_solver_code",
                    problem_type_code=problem_type_code,
                )

        if not problem_type_code:
            return None

        solver_codes = self.problem_type_solver_map.get(problem_type_code, [])

        for solver_code in solver_codes:
            solver = self._get_existing_solver(solver_code)

            if solver is not None:
                return TemplateMatchResult(
                    solver_code=solver.code,
                    solver=solver,
                    matched_by="problem_type_code",
                    problem_type_code=problem_type_code,
                )

        return None

    def _get_existing_solver(self, solver_code: str) -> SolverDefinition | None:
        try:
            return self.registry.get_solver(solver_code)
        except ValueError:
            return None

    def _validate_mapping(self) -> None:
        invalid_codes = []

        for solver_codes in self.problem_type_solver_map.values():
            for solver_code in solver_codes:
                if self._get_existing_solver(solver_code) is None:
                    invalid_codes.append(solver_code)

        if invalid_codes:
            unique_codes = ", ".join(sorted(set(invalid_codes)))
            raise ValueError(
                "Problem type solver mapping contains unknown solver codes: "
                f"{unique_codes}"
            )
