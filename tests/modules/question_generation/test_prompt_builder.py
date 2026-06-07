from types import SimpleNamespace

from modules.question_generation.prompt_builder import (
    build_question_generation_prompt,
)
from modules.question_generation.schemas import GenerationConstraints


def make_source_question():
    return SimpleNamespace(
        marker="Bai",
        marker_number="28",
        statement="Tinh $(1+i\\sqrt{3})^{9}$.",
        solution="Doi sang dang luong giac.",
        answer="$512i$",
        subject="complex",
        chapter="complex-number",
        difficulty="medium",
        skills=["complex-power"],
    )


def test_build_question_generation_prompt_contains_required_json_contract() -> None:
    source_question = make_source_question()

    prompt = build_question_generation_prompt(
        source_question=source_question,
        generation_count=2,
        constraints=GenerationConstraints(),
    )

    assert "Generate 2 new mathematics questions" in prompt
    assert "Return valid JSON only" in prompt
    assert "Do not wrap JSON in markdown fences" in prompt
    assert '"items"' in prompt
    assert '"statement"' in prompt
    assert '"solution"' in prompt
    assert '"answer"' in prompt
    assert '"difficulty"' in prompt
    assert '"skills"' in prompt


def test_build_question_generation_prompt_contains_source_question() -> None:
    source_question = make_source_question()

    prompt = build_question_generation_prompt(
        source_question=source_question,
        generation_count=1,
        constraints=GenerationConstraints(),
    )

    assert "Marker: Bai 28" in prompt
    assert "Tinh $(1+i\\sqrt{3})^{9}$." in prompt
    assert "Doi sang dang luong giac." in prompt
    assert "$512i$" in prompt


def test_build_question_generation_prompt_uses_source_metadata_by_default() -> None:
    source_question = make_source_question()

    prompt = build_question_generation_prompt(
        source_question=source_question,
        generation_count=1,
        constraints=GenerationConstraints(),
    )

    assert "- subject: complex" in prompt
    assert "- chapter: complex-number" in prompt
    assert "- difficulty: medium" in prompt
    assert "- skills: complex-power" in prompt


def test_build_question_generation_prompt_constraints_override_source_metadata() -> None:
    source_question = make_source_question()

    prompt = build_question_generation_prompt(
        source_question=source_question,
        generation_count=3,
        constraints=GenerationConstraints(
            subject="algebra",
            chapter="quadratic",
            difficulty="hard",
            skills=["quadratic-equation", "discriminant"],
            preserve_formula_style=False,
            avoid_duplicate=False,
        ),
    )

    assert "- subject: algebra" in prompt
    assert "- chapter: quadratic" in prompt
    assert "- difficulty: hard" in prompt
    assert "- skills: quadratic-equation, discriminant" in prompt
    assert "- preserve_formula_style: False" in prompt
    assert "- avoid_duplicate: False" in prompt