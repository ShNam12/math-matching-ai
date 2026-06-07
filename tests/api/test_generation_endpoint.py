from apps.api.v1.endpoints.generation import (
    _to_candidate_response,
    _to_generated_candidate,
    _to_generation_constraints,
)
from apps.api.v1.models.generation import (
    GeneratedQuestionCandidateItem,
    GenerationConstraintsRequest,
)
from modules.question_generation import GeneratedQuestionCandidate


def test_to_generation_constraints_uses_defaults_when_request_is_none() -> None:
    constraints = _to_generation_constraints(None)

    assert constraints.subject is None
    assert constraints.chapter is None
    assert constraints.difficulty is None
    assert constraints.skills == []
    assert constraints.preserve_formula_style is True
    assert constraints.avoid_duplicate is True


def test_to_generation_constraints_maps_request_values() -> None:
    constraints = _to_generation_constraints(
        GenerationConstraintsRequest(
            subject="math",
            chapter="complex",
            difficulty="medium",
            skills=["complex-power"],
            preserve_formula_style=False,
            avoid_duplicate=False,
        )
    )

    assert constraints.subject == "math"
    assert constraints.chapter == "complex"
    assert constraints.difficulty == "medium"
    assert constraints.skills == ["complex-power"]
    assert constraints.preserve_formula_style is False
    assert constraints.avoid_duplicate is False


def test_to_candidate_response_maps_dataclass_to_api_model() -> None:
    candidate = GeneratedQuestionCandidate(
        statement="Tinh $x+1$.",
        solution=None,
        answer="$x+1$",
        subject="math",
        chapter="algebra",
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
    )

    response = _to_candidate_response(candidate)

    assert response.statement == "Tinh $x+1$."
    assert response.answer == "$x+1$"
    assert response.formulas[0].normalized_latex == "x+1"


def test_to_generated_candidate_maps_api_model_to_dataclass() -> None:
    item = GeneratedQuestionCandidateItem(
        statement="Tinh $x+1$.",
        solution=None,
        answer="$x+1$",
        subject="math",
        chapter="algebra",
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
    )

    candidate = _to_generated_candidate(item)

    assert candidate.statement == "Tinh $x+1$."
    assert candidate.answer == "$x+1$"
    assert candidate.formulas[0]["source"] == "statement"