from modules.question_quality.schemas import (
    QualityIssue,
    QuestionQualityReport,
    QuestionValidationReport,
    SemanticDuplicateHit,
    SymbolicCheckResult,
)
import pytest


def test_quality_report_can_save_when_no_blocking_issues() -> None:
    report = QuestionQualityReport(
        warnings=[
            QualityIssue(
                code="missing_solution",
                message="Generated question does not include a solution",
                severity="warning",
                field="solution",
            )
        ],
        blocking_issues=[],
    )

    assert report.can_save is True
    assert report.quality_warnings == ["missing_solution"]


def test_quality_report_cannot_save_when_has_blocking_issue() -> None:
    report = QuestionQualityReport(
        warnings=[
            QualityIssue(
                code="missing_answer",
                message="Generated question does not include an answer",
                severity="warning",
                field="answer",
            )
        ],
        blocking_issues=[
            QualityIssue(
                code="exact_duplicate_statement",
                message="Generated statement duplicates an existing question",
                severity="error",
                field="statement",
            )
        ],
    )

    assert report.can_save is False
    assert report.quality_warnings == [
        "exact_duplicate_statement",
        "missing_answer",
    ]


def test_semantic_duplicate_hit_stores_search_result_metadata() -> None:
    hit = SemanticDuplicateHit(
        question_id="question-id",
        document_id="document-id",
        score=0.95,
        statement="Tinh $x+1$.",
    )

    assert hit.question_id == "question-id"
    assert hit.document_id == "document-id"
    assert hit.score == 0.95
    assert hit.statement == "Tinh $x+1$."


def test_validation_report_cannot_save_with_blocking_issue() -> None:
    report = QuestionValidationReport(
        warnings=[
            QualityIssue(
                code="solver_not_available",
                message="No solver is available",
                severity="warning",
                field="solver_code",
            )
        ],
        blocking_issues=[
            QualityIssue(
                code="mcq_missing_choices",
                message="Multiple choice question must include choices",
                severity="error",
                field="choices",
            )
        ],
    )

    assert report.can_save is False
    assert report.quality_warnings == [
        "mcq_missing_choices",
        "solver_not_available",
    ]
    assert report.to_dict()["can_save"] is False


def test_validation_report_round_trips_symbolic_checks() -> None:
    report = QuestionValidationReport(
        symbolic_checks=[
            SymbolicCheckResult(
                code="symbolic_correct_answer_verified",
                message="Correct answer matches solver result",
                passed=True,
                details={"solver_code": "ADD_INT"},
            )
        ]
    )

    restored = QuestionValidationReport.from_dict(report.to_dict())

    assert restored.can_save is True
    assert len(restored.symbolic_checks) == 1
    assert restored.symbolic_checks[0].passed is True
    assert restored.symbolic_checks[0].details["solver_code"] == "ADD_INT"


def test_symbolic_check_result_requires_boolean_passed() -> None:
    with pytest.raises(ValueError, match="boolean"):
        SymbolicCheckResult(
            code="symbolic_parse_failed",
            message="Could not parse expression",
            passed="no",
        )
