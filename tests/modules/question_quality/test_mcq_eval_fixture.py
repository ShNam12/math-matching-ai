import json
from collections import Counter
from pathlib import Path

from modules.neuro_symbolic import SolverRegistry


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "calculus_1_mcq_eval.json"
)
EXPECTED_GROUPS = {
    "generated_symbolic",
    "ai_generated",
    "converted_free_response",
    "ingested_document",
}
EXPECTED_CHOICE_KEYS = {"A", "B", "C", "D"}


def load_fixture() -> list[dict[str, object]]:
    with FIXTURE_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def test_mcq_eval_fixture_loads_and_has_expected_groups() -> None:
    samples = load_fixture()
    group_counts = Counter(str(sample.get("source_group")) for sample in samples)

    assert len(samples) == 80
    assert set(group_counts) == EXPECTED_GROUPS
    assert all(count == 20 for count in group_counts.values())


def test_mcq_eval_fixture_samples_have_required_contract() -> None:
    samples = load_fixture()
    seen_ids: set[str] = set()

    for sample in samples:
        sample_id = str(sample.get("id") or "")
        choices = sample.get("choices")

        assert sample_id
        assert sample_id not in seen_ids
        seen_ids.add(sample_id)
        assert str(sample.get("statement") or "").strip()
        assert sample.get("question_type") == "multiple_choice"
        assert sample.get("expected_problem_type_code")
        assert sample.get("expected_difficulty") in {"easy", "medium", "hard"}
        assert isinstance(choices, list)
        assert len(choices) == 4

        choice_keys = {str(choice.get("key")) for choice in choices}
        correct_choices = [
            choice for choice in choices if choice.get("is_correct") is True
        ]

        assert choice_keys == EXPECTED_CHOICE_KEYS
        assert len(correct_choices) == 1
        assert sample.get("correct_choice") in choice_keys
        assert correct_choices[0].get("key") == sample.get("correct_choice")
        assert correct_choices[0].get("text") == sample.get("expected_answer")
        assert all(str(choice.get("text") or "").strip() for choice in choices)


def test_mcq_eval_fixture_solver_codes_exist_when_present() -> None:
    registry = SolverRegistry()
    samples = load_fixture()

    for sample in samples:
        solver_code = sample.get("solver_code")

        if solver_code is None:
            continue

        solver = registry.get_solver(str(solver_code))

        assert solver.code == solver_code
        assert isinstance(sample.get("params"), dict)
