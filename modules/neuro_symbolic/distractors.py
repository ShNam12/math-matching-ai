from collections.abc import Callable
from typing import Any

import sympy as sp

from modules.neuro_symbolic.schemas import DistractorCandidate


DEFAULT_DISTRACTOR_STRATEGIES = [
    "sign_error",
    "coefficient_error",
    "missing_bound",
    "adjacent_param",
    "random_variation",
    "partial_result",
    "swap_operands",
]


class DistractorService:
    def generate(
        self,
        *,
        correct_answer: Any,
        params: dict[str, Any] | None = None,
        strategies: list[str] | None = None,
        count: int = 3,
        solver_func: Callable[..., Any] | None = None,
    ) -> list[DistractorCandidate]:
        params = params or {}
        strategies = strategies or DEFAULT_DISTRACTOR_STRATEGIES
        distractors: list[DistractorCandidate] = []

        for strategy in strategies:
            if len(distractors) >= count:
                break

            try:
                result = self._apply_strategy(
                    strategy=strategy,
                    correct_answer=correct_answer,
                    params=params,
                    solver_func=solver_func,
                )
            except Exception:
                continue

            self._append_if_valid(
                distractors=distractors,
                correct_answer=correct_answer,
                value=result,
                error_type=strategy,
            )

        attempts = 0
        while len(distractors) < count and attempts < 20:
            attempts += 1
            try:
                result = self._random_variation(
                    correct_answer,
                    params,
                    attempts=attempts,
                )
            except Exception:
                continue

            self._append_if_valid(
                distractors=distractors,
                correct_answer=correct_answer,
                value=result,
                error_type="random_variation",
            )

        return distractors[:count]

    def _apply_strategy(
        self,
        *,
        strategy: str,
        correct_answer: Any,
        params: dict[str, Any],
        solver_func: Callable[..., Any] | None,
    ) -> Any:
        if strategy == "sign_error":
            return self._sign_error(correct_answer)

        if strategy == "missing_bound":
            return self._missing_bound(correct_answer)

        if strategy == "coefficient_error":
            return self._coefficient_error(correct_answer, params)

        if strategy == "adjacent_param":
            return self._adjacent_param(
                correct_answer,
                params,
                solver_func=solver_func,
            )

        if strategy == "random_variation":
            return self._random_variation(correct_answer, params, attempts=1)

        if strategy == "partial_result":
            return self._partial_result(correct_answer)

        if strategy == "swap_operands":
            return self._swap_operands(correct_answer)

        raise ValueError(f"Unknown distractor strategy: {strategy}")

    def _append_if_valid(
        self,
        *,
        distractors: list[DistractorCandidate],
        correct_answer: Any,
        value: Any,
        error_type: str,
    ) -> None:
        if value is None:
            return

        if self._equivalent(value, correct_answer):
            return

        if any(self._equivalent(value, distractor.value) for distractor in distractors):
            return

        distractors.append(
            self._to_candidate(
                value=value,
                error_type=error_type,
            )
        )

    def _to_candidate(
        self,
        *,
        value: Any,
        error_type: str,
    ) -> DistractorCandidate:
        expression = self._to_expression(value)

        if expression is not None:
            simplified = sp.simplify(expression)
            value_text = str(simplified)
            latex_text = sp.latex(simplified)
        else:
            value_text = str(value)
            latex_text = value_text

        return DistractorCandidate(
            value=value_text,
            latex=latex_text,
            text=value_text,
            error_type=error_type,
            rationale=self._rationale(error_type),
        )

    def _to_expression(self, value: Any):
        if isinstance(value, sp.MatrixBase):
            return value

        try:
            return sp.sympify(value)
        except Exception:
            return None

    def _equivalent(self, left: Any, right: Any) -> bool:
        left_expression = self._to_expression(left)
        right_expression = self._to_expression(right)

        if left_expression is None or right_expression is None:
            return str(left).strip() == str(right).strip()

        if isinstance(left_expression, sp.MatrixBase) or isinstance(
            right_expression,
            sp.MatrixBase,
        ):
            try:
                return (left_expression - right_expression).is_zero_matrix
            except Exception:
                return left_expression == right_expression

        try:
            return sp.simplify(left_expression - right_expression) == 0
        except Exception:
            return sp.simplify(left_expression) == sp.simplify(right_expression)

    def _sign_error(self, answer: Any) -> Any:
        expression = self._to_expression(answer)

        if expression is None:
            return f"-({answer})"

        return -expression

    def _missing_bound(self, answer: Any) -> Any:
        expression = self._to_expression(answer)

        if expression is None:
            return f"2*({answer})"

        return expression * 2

    def _coefficient_error(
        self,
        answer: Any,
        params: dict[str, Any],
    ) -> Any:
        expression = self._to_expression(answer)

        if expression is None:
            return f"2*({answer})"

        for key in ["a", "n", "coefficient", "b"]:
            if key in params:
                factor = abs(int(params[key])) or 2
                return expression * factor

        return expression * 2

    def _adjacent_param(
        self,
        answer: Any,
        params: dict[str, Any],
        *,
        solver_func: Callable[..., Any] | None,
    ) -> Any:
        if solver_func is not None and params:
            for key in ["a", "n", "b", "c", "coefficient", "power"]:
                if key not in params or not isinstance(params[key], int):
                    continue

                adjusted = dict(params)
                old_value = int(adjusted[key])
                new_value = old_value + (1 if old_value >= 0 else -1)

                if key == "a" and new_value == 0:
                    new_value = old_value - 1

                adjusted[key] = new_value

                try:
                    return solver_func(adjusted)
                except TypeError:
                    try:
                        return solver_func(**adjusted)
                    except Exception:
                        continue
                except Exception:
                    continue

        expression = self._to_expression(answer)

        if expression is None:
            return f"3/2*({answer})"

        return expression * sp.Rational(3, 2)

    def _random_variation(
        self,
        answer: Any,
        params: dict[str, Any],
        *,
        attempts: int,
    ) -> Any:
        expression = self._to_expression(answer)

        if expression is None:
            return f"{answer} + {attempts}"

        variations = [
            expression + attempts,
            expression - attempts,
            expression * (attempts + 1),
            expression * sp.Rational(attempts + 1, attempts + 2),
        ]

        return variations[(attempts - 1) % len(variations)]

    def _partial_result(self, answer: Any) -> Any:
        expression = self._to_expression(answer)

        if expression is None:
            return f"2/3*({answer})"

        if isinstance(expression, sp.MatrixBase):
            return expression * sp.Rational(2, 3)

        expanded = sp.expand(expression)

        if hasattr(expanded, "args") and len(expanded.args) > 1:
            return sum(expanded.args[:-1])

        return expanded * sp.Rational(2, 3)

    def _swap_operands(self, answer: Any) -> Any:
        expression = self._to_expression(answer)

        if expression is None:
            return f"-({answer})"

        if isinstance(expression, sp.MatrixBase):
            return -expression

        numerator, denominator = sp.fraction(expression)

        if denominator != 1 and numerator != 0:
            return denominator / numerator

        return -expression

    def _rationale(self, error_type: str) -> str:
        rationales = {
            "sign_error": "Wrong sign in the final expression.",
            "coefficient_error": "Incorrect coefficient carried through the computation.",
            "missing_bound": "Forgot or misapplied an integration bound.",
            "adjacent_param": "Solved a nearby parameter variant instead of the original.",
            "random_variation": "Plausible nearby numerical or symbolic variation.",
            "partial_result": "Stopped at a partial intermediate result.",
            "swap_operands": "Swapped numerator and denominator or operand order.",
        }

        return rationales.get(error_type, "Plausible distractor.")
