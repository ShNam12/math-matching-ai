from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    GenerationConstraints,
    QuestionGenerationPreview,
)


def test_generation_constraints_default_values() -> None:
    constraints = GenerationConstraints()

    assert constraints.subject is None
    assert constraints.chapter is None
    assert constraints.difficulty is None
    assert constraints.skills == []
    assert constraints.preserve_formula_style is True
    assert constraints.avoid_duplicate is True


def test_generation_constraints_skills_are_not_shared() -> None:
    first = GenerationConstraints()
    second = GenerationConstraints()

    assert first.skills is not second.skills


def test_generated_question_candidate_stores_generation_payload() -> None:
    candidate = GeneratedQuestionCandidate(
        statement="Tinh $x^2$.",
        solution="Binh phuong x.",
        answer="$x^2$",
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["power"],
        formulas=[
            {
                "latex": "x^2",
                "normalized_latex": "x^2",
                "source": "statement",
            }
        ],
        quality_warnings=[],
    )

    assert candidate.statement == "Tinh $x^2$."
    assert candidate.solution == "Binh phuong x."
    assert candidate.answer == "$x^2$"
    assert candidate.skills == ["power"]
    assert candidate.formulas[0]["source"] == "statement"
    assert candidate.quality_warnings == []


def test_question_generation_preview_contains_candidates() -> None:
    candidate = GeneratedQuestionCandidate(
        statement="Tinh $x+1$.",
        solution=None,
        answer=None,
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
        formulas=[
            {
                "latex": "x+1",
                "normalized_latex": "x+1",
                "source": "statement",
            }
        ],
        quality_warnings=[],
    )

    preview = QuestionGenerationPreview(
        source_question_id="source-id",
        candidates=[candidate],
    )

    assert preview.source_question_id == "source-id"
    assert len(preview.candidates) == 1
    assert preview.candidates[0].statement == "Tinh $x+1$."