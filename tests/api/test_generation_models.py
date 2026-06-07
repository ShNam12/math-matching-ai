import pytest
from pydantic import ValidationError

from apps.api.v1.models.generation import (
    GeneratedQuestionCandidateItem,
    GenerationConstraintsRequest,
    QuestionGenerationPreviewRequest,
    QuestionGenerationSaveRequest,
)


def test_preview_request_defaults() -> None:
    request = QuestionGenerationPreviewRequest(
        source_question_id="source-id",
    )

    assert request.source_question_id == "source-id"
    assert request.generation_count == 3
    assert request.constraints is None


def test_preview_request_rejects_invalid_generation_count() -> None:
    with pytest.raises(ValidationError):
        QuestionGenerationPreviewRequest(
            source_question_id="source-id",
            generation_count=0,
        )

    with pytest.raises(ValidationError):
        QuestionGenerationPreviewRequest(
            source_question_id="source-id",
            generation_count=11,
        )


def test_constraints_default_skills_are_not_shared() -> None:
    first = GenerationConstraintsRequest()
    second = GenerationConstraintsRequest()

    assert first.skills == []
    assert second.skills == []
    assert first.skills is not second.skills


def test_save_request_accepts_candidate_payload() -> None:
    request = QuestionGenerationSaveRequest(
        source_question_id="source-id",
        candidate=GeneratedQuestionCandidateItem(
            statement="Tinh $x+1$.",
            solution=None,
            answer=None,
            subject="algebra",
            chapter="expression",
            difficulty="easy",
            skills=["simplify"],
            formulas=[
                {
                    "latex": "x+1",
                    "normalized_latex": "x+1",
                    "source": "statement",
                }
            ],
            quality_warnings=[],
        ),
    )

    assert request.source_question_id == "source-id"
    assert request.candidate.statement == "Tinh $x+1$."
    assert request.candidate.formulas[0].normalized_latex == "x+1"