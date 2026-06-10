from modules.question_quality.schemas import (
    QualityIssue,
    QuestionQualityReport,
    SemanticDuplicateHit,
)


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