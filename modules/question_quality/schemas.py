from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class QualityIssue:
    code: str
    message: str
    severity: str
    field: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "field": self.field,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "QualityIssue":
        return cls(
            code=str(payload.get("code") or ""),
            message=str(payload.get("message") or ""),
            severity=str(payload.get("severity") or ""),
            field=(
                str(payload["field"])
                if payload.get("field") is not None
                else None
            ),
        )


@dataclass(frozen=True)
class SymbolicCheckResult:
    code: str
    message: str
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.passed, bool):
            raise ValueError("symbolic check passed must be a boolean")

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "passed": self.passed,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SymbolicCheckResult":
        details = payload.get("details")

        return cls(
            code=str(payload.get("code") or ""),
            message=str(payload.get("message") or ""),
            passed=payload.get("passed") is True,
            details=details if isinstance(details, dict) else {},
        )


@dataclass(frozen=True)
class SemanticDuplicateHit:
    question_id: str
    document_id: str
    score: float
    statement: str


@dataclass(frozen=True)
class QualityRuleResult:
    """A presentation-friendly outcome for one candidate quality rule.

    This is derived from the existing warnings/blocking issues.  It does not
    participate in the decision of whether a question may be saved.
    """

    rule_id: str
    title: str
    category: str
    status: Literal["pass", "warn", "fail", "skipped"]
    issues: list[QualityIssue] = field(default_factory=list)
    check_codes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class QuestionQualityReport:
    warnings: list[QualityIssue] = field(default_factory=list)
    blocking_issues: list[QualityIssue] = field(default_factory=list)
    semantic_duplicates: list[SemanticDuplicateHit] = field(default_factory=list)
    symbolic_checks: list[SymbolicCheckResult] = field(default_factory=list)
    rule_results: list[QualityRuleResult] = field(default_factory=list)

    @property
    def quality_warnings(self) -> list[str]:
        return [
            issue.code
            for issue in [*self.blocking_issues, *self.warnings]
        ]

    @property
    def can_save(self) -> bool:
        return not self.blocking_issues


@dataclass(frozen=True)
class QuestionValidationReport:
    warnings: list[QualityIssue] = field(default_factory=list)
    blocking_issues: list[QualityIssue] = field(default_factory=list)
    symbolic_checks: list[SymbolicCheckResult] = field(default_factory=list)

    @property
    def can_save(self) -> bool:
        return not self.blocking_issues

    @property
    def quality_warnings(self) -> list[str]:
        return [
            issue.code
            for issue in [*self.blocking_issues, *self.warnings]
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "can_save": self.can_save,
            "warnings": [issue.to_dict() for issue in self.warnings],
            "blocking_issues": [
                issue.to_dict()
                for issue in self.blocking_issues
            ],
            "symbolic_checks": [
                check.to_dict()
                for check in self.symbolic_checks
            ],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "QuestionValidationReport":
        if not payload:
            return cls()

        warnings = payload.get("warnings")
        blocking_issues = payload.get("blocking_issues")
        symbolic_checks = payload.get("symbolic_checks")

        return cls(
            warnings=[
                QualityIssue.from_dict(issue)
                for issue in warnings
                if isinstance(issue, dict)
            ] if isinstance(warnings, list) else [],
            blocking_issues=[
                QualityIssue.from_dict(issue)
                for issue in blocking_issues
                if isinstance(issue, dict)
            ] if isinstance(blocking_issues, list) else [],
            symbolic_checks=[
                SymbolicCheckResult.from_dict(check)
                for check in symbolic_checks
                if isinstance(check, dict)
            ] if isinstance(symbolic_checks, list) else [],
        )
    
@dataclass(frozen=True)
class TaxonomyQualityReport:
    question_id: str
    warnings: list[QualityIssue] = field(default_factory=list)
    blocking_issues: list[QualityIssue] = field(default_factory=list)

    @property
    def can_accept(self) -> bool:
        return not self.blocking_issues

    @property
    def issue_count(self) -> int:
        return len(self.warnings) + len(self.blocking_issues)
