from apps.api.v1.endpoints.generation import (
    _to_candidate_response,
    _to_generated_candidate,
    _to_generation_constraints,
)
from apps.api.v1.models.generation import (
    GeneratedQuestionCandidateItem,
    GenerationConstraintsRequest,
)
from modules.question_generation import GeneratedQuestionCandidate, MultipleChoiceOption
from modules.question_quality import QuestionValidationReport


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


def test_to_candidate_response_maps_mcq_fields() -> None:
    candidate = GeneratedQuestionCandidate(
        statement="Tinh $1+1$.",
        solution="$1+1=2$.",
        answer="2",
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["addition"],
        formulas=[],
        quality_warnings=[],
        question_type="multiple_choice",
        choices=[
            MultipleChoiceOption(key="A", text="1"),
            MultipleChoiceOption(key="B", text="2", is_correct=True),
            MultipleChoiceOption(key="C", text="3"),
            MultipleChoiceOption(key="D", text="4"),
        ],
        correct_choice="B",
        symbolic_answer="2",
        generation_method="ai_symbolic",
        solver_code="ADD_INT",
        validation_report=QuestionValidationReport(),
    )

    response = _to_candidate_response(candidate)

    assert response.question_type == "multiple_choice"
    assert response.choices[1].key == "B"
    assert response.choices[1].is_correct is True
    assert response.correct_choice == "B"
    assert response.symbolic_answer == "2"
    assert response.generation_method == "ai_symbolic"
    assert response.solver_code == "ADD_INT"
    assert response.validation_report.can_save is True


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


def test_to_generated_candidate_maps_mcq_fields() -> None:
    item = GeneratedQuestionCandidateItem(
        statement="Tinh $1+1$.",
        solution="$1+1=2$.",
        answer="2",
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["addition"],
        formulas=[],
        quality_warnings=[],
        question_type="multiple_choice",
        choices=[
            {"key": "A", "text": "1"},
            {"key": "B", "text": "2", "is_correct": True},
            {"key": "C", "text": "3"},
            {"key": "D", "text": "4"},
        ],
        correct_choice="B",
        symbolic_answer="2",
        generation_method="ai_symbolic",
        solver_code="ADD_INT",
        validation_report={
            "can_save": True,
            "warnings": [],
            "blocking_issues": [],
            "symbolic_checks": [],
        },
    )

    candidate = _to_generated_candidate(item)

    assert candidate.question_type == "multiple_choice"
    assert candidate.choices[1].key == "B"
    assert candidate.choices[1].is_correct is True
    assert candidate.correct_choice == "B"
    assert candidate.symbolic_answer == "2"
    assert candidate.generation_method == "ai_symbolic"
    assert candidate.solver_code == "ADD_INT"
    assert candidate.validation_report.can_save is True
