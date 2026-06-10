from apps.api.v1.models.generation import (
    GeneratedQuestionCandidateItem,
    QuestionGenerationQualityRequest,
    QuestionGenerationQualityResponse,
    QualityIssueItem,
    SemanticDuplicateItem,
)


def test_generation_quality_request_accepts_candidate() -> None:
    request = QuestionGenerationQualityRequest(
        source_question_id="source-id",
        requested_difficulty="medium",
        candidate=GeneratedQuestionCandidateItem(
            statement="Tinh $x+1$.",
            solution=None,
            answer="$x+1$",
            subject="math",
            chapter="algebra",
            difficulty="medium",
            skills=["simplify"],
            formulas=[],
            quality_warnings=[],
        ),
    )

    assert request.source_question_id == "source-id"
    assert request.requested_difficulty == "medium"
    assert request.candidate.statement == "Tinh $x+1$."


def test_generation_quality_response_contains_report_details() -> None:
    response = QuestionGenerationQualityResponse(
        can_save=False,
        quality_warnings=["exact_duplicate_statement"],
        warnings=[],
        blocking_issues=[
            QualityIssueItem(
                code="exact_duplicate_statement",
                message="Generated statement duplicates an existing question",
                severity="error",
                field="statement",
            )
        ],
        semantic_duplicates=[
            SemanticDuplicateItem(
                question_id="question-id",
                document_id="document-id",
                score=0.95,
                statement="Tinh $x+1$.",
            )
        ],
    )

    assert response.can_save is False
    assert response.quality_warnings == ["exact_duplicate_statement"]
    assert response.blocking_issues[0].field == "statement"
    assert response.semantic_duplicates[0].score == 0.95