import random
from dataclasses import dataclass
from typing import Any

from modules.neuro_symbolic.solver_executor import SolverExecutor
from modules.neuro_symbolic.solver_registry import SolverRegistry


class ParameterSamplingError(ValueError):
    """Raised when a valid parameter set cannot be produced."""


@dataclass(frozen=True)
class ParameterSampleResult:
    solver_code: str
    params: dict[str, object]
    attempts: int


class ParameterSampler:
    def __init__(
        self,
        registry: SolverRegistry | None = None,
        executor: SolverExecutor | None = None,
        *,
        seed: int | None = None,
        max_attempts: int = 20,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self.registry = registry or SolverRegistry()
        self.executor = executor or SolverExecutor(self.registry)
        self.seed = seed
        self.max_attempts = max_attempts

    def sample_from_schema(
        self,
        param_schema: dict[str, Any] | None,
        *,
        seed: int | None = None,
    ) -> dict[str, object]:
        rng = self._rng(seed)
        properties = self._properties(param_schema)

        return {
            name: self._sample_property(name, spec, rng)
            for name, spec in properties.items()
        }

    def sample_for_solver(
        self,
        solver_code: str,
        *,
        seed: int | None = None,
    ) -> dict[str, object]:
        return self.sample_result_for_solver(solver_code, seed=seed).params

    def sample_result_for_solver(
        self,
        solver_code: str,
        *,
        seed: int | None = None,
    ) -> ParameterSampleResult:
        solver = self.registry.get_solver(solver_code)
        rng = self._rng(seed)
        last_error: str | None = None

        for attempt in range(1, self.max_attempts + 1):
            params = self._sample_from_properties(
                self._properties(solver.param_schema),
                rng,
            )
            result = self.executor.execute(solver.code, params)
            if result.success:
                return ParameterSampleResult(
                    solver_code=solver.code,
                    params=params,
                    attempts=attempt,
                )
            last_error = result.error

        raise ParameterSamplingError(
            f"Could not sample valid params for {solver.code}: {last_error}"
        )

    def _rng(self, seed: int | None) -> random.Random:
        return random.Random(self.seed if seed is None else seed)

    def _properties(
        self,
        param_schema: dict[str, Any] | None,
    ) -> dict[str, dict[str, Any]]:
        if not param_schema:
            return {}

        raw_properties = param_schema.get("properties", {})
        if not isinstance(raw_properties, dict):
            raise ParameterSamplingError("param_schema.properties must be a mapping")

        properties: dict[str, dict[str, Any]] = {}
        for name, spec in raw_properties.items():
            if isinstance(name, str) and isinstance(spec, dict):
                properties[name] = spec
        return properties

    def _sample_from_properties(
        self,
        properties: dict[str, dict[str, Any]],
        rng: random.Random,
    ) -> dict[str, object]:
        return {
            name: self._sample_property(name, spec, rng)
            for name, spec in properties.items()
        }

    def _sample_property(
        self,
        name: str,
        spec: dict[str, Any],
        rng: random.Random,
    ) -> object:
        choices = self._choices(spec)
        if choices is not None:
            return rng.choice(choices)

        value_type = spec.get("type")
        if value_type == "integer":
            return self._sample_integer(name, spec, rng)

        if value_type == "number":
            return self._sample_number(name, spec, rng)

        if "default" in spec:
            return spec["default"]

        if value_type == "boolean":
            return rng.choice([False, True])

        return ""

    def _choices(self, spec: dict[str, Any]) -> list[object] | None:
        raw_choices = spec.get("choices", spec.get("choice", spec.get("enum")))
        if raw_choices is None:
            return None

        if not isinstance(raw_choices, list) or not raw_choices:
            raise ParameterSamplingError("choices must be a non-empty list")

        choices = [
            choice
            for choice in raw_choices
            if not self._is_excluded(choice, spec)
        ]
        if not choices:
            raise ParameterSamplingError("choices are exhausted by exclude rules")
        return choices

    def _sample_integer(
        self,
        name: str,
        spec: dict[str, Any],
        rng: random.Random,
    ) -> int:
        default = spec.get("default")
        minimum = self._bound(spec, "minimum", "min")
        maximum = self._bound(spec, "maximum", "max")

        if minimum is None and maximum is None:
            if default is not None:
                value = int(default)
                if self._is_excluded(value, spec):
                    raise ParameterSamplingError(
                        f"default for {name} is excluded: {value}"
                    )
                return value
            minimum = -5
            maximum = 5
        elif minimum is None:
            minimum = min(0, maximum)
        elif maximum is None:
            maximum = max(0, minimum)

        if minimum > maximum:
            raise ParameterSamplingError(f"invalid integer range for {name}")

        candidates = [
            value
            for value in range(int(minimum), int(maximum) + 1)
            if not self._is_excluded(value, spec)
        ]
        if not candidates:
            raise ParameterSamplingError(f"integer range for {name} has no values")

        if default is not None and int(default) in candidates:
            return int(default)

        return rng.choice(candidates)

    def _sample_number(
        self,
        name: str,
        spec: dict[str, Any],
        rng: random.Random,
    ) -> float:
        default = spec.get("default")
        if default is not None:
            value = float(default)
            if self._is_excluded(value, spec):
                raise ParameterSamplingError(f"default for {name} is excluded: {value}")
            return value

        minimum = self._bound(spec, "minimum", "min")
        maximum = self._bound(spec, "maximum", "max")
        minimum = 0 if minimum is None else float(minimum)
        maximum = minimum if maximum is None else float(maximum)

        if minimum > maximum:
            raise ParameterSamplingError(f"invalid number range for {name}")

        for _ in range(100):
            value = rng.uniform(minimum, maximum)
            if not self._is_excluded(value, spec):
                return value

        raise ParameterSamplingError(f"number range for {name} has no values")

    def _bound(
        self,
        spec: dict[str, Any],
        primary_key: str,
        fallback_key: str,
    ) -> int | float | None:
        value = spec.get(primary_key, spec.get(fallback_key))
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ParameterSamplingError(f"{primary_key} must be numeric")
        return value

    def _is_excluded(self, value: object, spec: dict[str, Any]) -> bool:
        excludes = self._excludes(spec)
        return any(value == excluded for excluded in excludes)

    def _excludes(self, spec: dict[str, Any]) -> list[object]:
        excludes: list[object] = []
        raw_exclude = spec.get("exclude")

        if isinstance(raw_exclude, list):
            excludes.extend(raw_exclude)
        elif raw_exclude is not None:
            excludes.append(raw_exclude)

        raw_not = spec.get("not")
        if isinstance(raw_not, dict) and "const" in raw_not:
            excludes.append(raw_not["const"])
        elif raw_not is not None and not isinstance(raw_not, dict):
            excludes.append(raw_not)

        return excludes
