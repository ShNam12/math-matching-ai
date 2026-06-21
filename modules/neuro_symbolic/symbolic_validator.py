from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from modules.question_quality.schemas import (
    QualityIssue,
    QuestionValidationReport,
    SymbolicCheckResult,
)
from modules.neuro_symbolic.solver_executor import SolverExecutor

if TYPE_CHECKING:
    from modules.question_generation.schemas import (
        GeneratedQuestionCandidate,
        MultipleChoiceOption,
    )


TRANSFORMATIONS = (
    *standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)


@dataclass(frozen=True)
class ParsedChoice:
    choice: MultipleChoiceOption
    expression: sp.Expr | None
    raw_value: str


class SymbolicMCQValidator:
    def __init__(
        self,
        executor: SolverExecutor | None = None,
    ) -> None:
        self.executor = executor or SolverExecutor()

    def validate_candidate(
        self,
        candidate: GeneratedQuestionCandidate,
        *,
        params: dict[str, Any] | None = None,
    ) -> QuestionValidationReport:
        if candidate.question_type != "multiple_choice":
            return QuestionValidationReport()

        warnings: list[QualityIssue] = []
        blocking_issues: list[QualityIssue] = []
        symbolic_checks: list[SymbolicCheckResult] = []

        if not candidate.solver_code:
            warnings.append(
                QualityIssue(
                    code="solver_not_available",
                    message="No solver_code is available for symbolic validation",
                    severity="warning",
                    field="solver_code",
                )
            )
            symbolic_checks.append(
                SymbolicCheckResult(
                    code="solver_not_available",
                    message="No solver_code is available for symbolic validation",
                    passed=False,
                    details={},
                )
            )
            return QuestionValidationReport(
                warnings=warnings,
                blocking_issues=blocking_issues,
                symbolic_checks=symbolic_checks,
            )

        solver_result = self.executor.execute(candidate.solver_code, params or {})

        if not solver_result.success or solver_result.output is None:
            warnings.append(
                QualityIssue(
                    code="solver_not_available",
                    message=solver_result.error or "Solver execution failed",
                    severity="warning",
                    field="solver_code",
                )
            )
            symbolic_checks.append(
                SymbolicCheckResult(
                    code="solver_not_available",
                    message=solver_result.error or "Solver execution failed",
                    passed=False,
                    details={"solver_code": solver_result.solver_code},
                )
            )
            return QuestionValidationReport(
                warnings=warnings,
                blocking_issues=blocking_issues,
                symbolic_checks=symbolic_checks,
            )

        solver_expression = self._parse_expression(solver_result.output.answer)

        if solver_expression is None:
            warnings.append(
                QualityIssue(
                    code="symbolic_parse_failed",
                    message="Could not parse solver answer for symbolic validation",
                    severity="warning",
                    field="answer",
                )
            )
            symbolic_checks.append(
                SymbolicCheckResult(
                    code="symbolic_parse_failed",
                    message="Could not parse solver answer for symbolic validation",
                    passed=False,
                    details={"solver_answer": solver_result.output.answer},
                )
            )
            return QuestionValidationReport(
                warnings=warnings,
                blocking_issues=blocking_issues,
                symbolic_checks=symbolic_checks,
            )

        correct_choice = self._find_correct_choice(candidate)

        if correct_choice is None:
            warnings.append(
                QualityIssue(
                    code="symbolic_parse_failed",
                    message="Could not identify a correct choice for symbolic validation",
                    severity="warning",
                    field="correct_choice",
                )
            )
            symbolic_checks.append(
                SymbolicCheckResult(
                    code="symbolic_parse_failed",
                    message="Could not identify a correct choice for symbolic validation",
                    passed=False,
                    details={"correct_choice": candidate.correct_choice},
                )
            )
            return QuestionValidationReport(
                warnings=warnings,
                blocking_issues=blocking_issues,
                symbolic_checks=symbolic_checks,
            )

        parsed_correct = self._parse_choice(correct_choice)

        if parsed_correct.expression is None:
            warnings.append(
                QualityIssue(
                    code="symbolic_parse_failed",
                    message="Could not parse correct choice for symbolic validation",
                    severity="warning",
                    field="choices",
                )
            )
            symbolic_checks.append(
                SymbolicCheckResult(
                    code="symbolic_parse_failed",
                    message="Could not parse correct choice for symbolic validation",
                    passed=False,
                    details={
                        "choice_key": correct_choice.key,
                        "choice_value": parsed_correct.raw_value,
                    },
                )
            )
            return QuestionValidationReport(
                warnings=warnings,
                blocking_issues=blocking_issues,
                symbolic_checks=symbolic_checks,
            )

        if self._equivalent(parsed_correct.expression, solver_expression):
            symbolic_checks.append(
                SymbolicCheckResult(
                    code="symbolic_correct_answer_verified",
                    message="Correct choice matches solver result",
                    passed=True,
                    details={
                        "choice_key": correct_choice.key,
                        "solver_answer": solver_result.output.answer,
                    },
                )
            )
        else:
            blocking_issues.append(
                QualityIssue(
                    code="symbolic_correct_answer_mismatch",
                    message="Correct choice does not match solver result",
                    severity="error",
                    field="correct_choice",
                )
            )
            symbolic_checks.append(
                SymbolicCheckResult(
                    code="symbolic_correct_answer_mismatch",
                    message="Correct choice does not match solver result",
                    passed=False,
                    details={
                        "choice_key": correct_choice.key,
                        "choice_value": parsed_correct.raw_value,
                        "solver_answer": solver_result.output.answer,
                    },
                )
            )

        parsed_distractors = [
            self._parse_choice(choice)
            for choice in candidate.choices
            if choice.key != correct_choice.key
        ]

        self._validate_distractors_against_solver(
            parsed_distractors=parsed_distractors,
            solver_expression=solver_expression,
            warnings=warnings,
            blocking_issues=blocking_issues,
            symbolic_checks=symbolic_checks,
        )
        self._validate_duplicate_distractors(
            parsed_distractors=parsed_distractors,
            warnings=warnings,
            blocking_issues=blocking_issues,
            symbolic_checks=symbolic_checks,
        )

        return QuestionValidationReport(
            warnings=warnings,
            blocking_issues=blocking_issues,
            symbolic_checks=symbolic_checks,
        )

    def _find_correct_choice(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> MultipleChoiceOption | None:
        if candidate.correct_choice:
            for choice in candidate.choices:
                if choice.key == candidate.correct_choice:
                    return choice

        flagged = [
            choice
            for choice in candidate.choices
            if choice.is_correct
        ]

        if len(flagged) == 1:
            return flagged[0]

        return None

    def _parse_choice(self, choice: MultipleChoiceOption) -> ParsedChoice:
        raw_value = choice.latex or choice.text

        return ParsedChoice(
            choice=choice,
            expression=self._parse_expression(raw_value),
            raw_value=raw_value,
        )

    def _parse_expression(self, value: Any) -> sp.Expr | None:
        text = str(value).strip()

        if not text:
            return None

        text = text.strip("$")

        try:
            return parse_expr(
                text,
                transformations=TRANSFORMATIONS,
                evaluate=True,
            )
        except Exception:
            try:
                return sp.sympify(text)
            except Exception:
                return None

    def _equivalent(self, left: sp.Expr, right: sp.Expr) -> bool:
        try:
            return sp.simplify(left - right) == 0
        except Exception:
            return sp.simplify(left) == sp.simplify(right)

    def _validate_distractors_against_solver(
        self,
        *,
        parsed_distractors: list[ParsedChoice],
        solver_expression: sp.Expr,
        warnings: list[QualityIssue],
        blocking_issues: list[QualityIssue],
        symbolic_checks: list[SymbolicCheckResult],
    ) -> None:
        for parsed in parsed_distractors:
            if parsed.expression is None:
                self._append_parse_warning(
                    parsed=parsed,
                    warnings=warnings,
                    symbolic_checks=symbolic_checks,
                )
                continue

            if self._equivalent(parsed.expression, solver_expression):
                blocking_issues.append(
                    QualityIssue(
                        code="symbolic_distractor_equals_correct",
                        message="Distractor is symbolically equal to the correct answer",
                        severity="error",
                        field="choices",
                    )
                )
                symbolic_checks.append(
                    SymbolicCheckResult(
                        code="symbolic_distractor_equals_correct",
                        message="Distractor is symbolically equal to the correct answer",
                        passed=False,
                        details={
                            "choice_key": parsed.choice.key,
                            "choice_value": parsed.raw_value,
                        },
                    )
                )

    def _validate_duplicate_distractors(
        self,
        *,
        parsed_distractors: list[ParsedChoice],
        warnings: list[QualityIssue],
        blocking_issues: list[QualityIssue],
        symbolic_checks: list[SymbolicCheckResult],
    ) -> None:
        seen: list[ParsedChoice] = []

        for parsed in parsed_distractors:
            if parsed.expression is None:
                self._append_parse_warning(
                    parsed=parsed,
                    warnings=warnings,
                    symbolic_checks=symbolic_checks,
                )
                continue

            for previous in seen:
                if previous.expression is not None and self._equivalent(
                    parsed.expression,
                    previous.expression,
                ):
                    blocking_issues.append(
                        QualityIssue(
                            code="symbolic_distractor_duplicate",
                            message="Two distractors are symbolically equivalent",
                            severity="error",
                            field="choices",
                        )
                    )
                    symbolic_checks.append(
                        SymbolicCheckResult(
                            code="symbolic_distractor_duplicate",
                            message="Two distractors are symbolically equivalent",
                            passed=False,
                            details={
                                "choice_key": parsed.choice.key,
                                "duplicate_choice_key": previous.choice.key,
                            },
                        )
                    )
                    break

            seen.append(parsed)

    def _append_parse_warning(
        self,
        *,
        parsed: ParsedChoice,
        warnings: list[QualityIssue],
        symbolic_checks: list[SymbolicCheckResult],
    ) -> None:
        details = {
            "choice_key": parsed.choice.key,
            "choice_value": parsed.raw_value,
        }

        if any(
            check.code == "symbolic_parse_failed"
            and check.details == details
            for check in symbolic_checks
        ):
            return

        warnings.append(
            QualityIssue(
                code="symbolic_parse_failed",
                message="Could not parse choice for symbolic validation",
                severity="warning",
                field="choices",
            )
        )
        symbolic_checks.append(
            SymbolicCheckResult(
                code="symbolic_parse_failed",
                message="Could not parse choice for symbolic validation",
                passed=False,
                details=details,
            )
        )
