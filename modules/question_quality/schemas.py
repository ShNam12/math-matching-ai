from dataclasses import dataclass, field


@dataclass(frozen=True)
class QualityIssue:
    code: str
    message: str
    severity: str
    field: str | None = None


@dataclass(frozen=True)
class SemanticDuplicateHit:
    question_id: str
    document_id: str
    score: float
    statement: str


@dataclass(frozen=True)
class QuestionQualityReport:
    warnings: list[QualityIssue] = field(default_factory=list)
    blocking_issues: list[QualityIssue] = field(default_factory=list)
    semantic_duplicates: list[SemanticDuplicateHit] = field(default_factory=list)

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