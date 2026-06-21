from scripts.evaluate_mcq_quality import (
    METRIC_KEYS,
    evaluate_samples,
)
from modules.taxonomy import load_validated_taxonomy


def choice(key: str, text: str, is_correct: bool = False) -> dict[str, object]:
    return {
        "key": key,
        "text": text,
        "is_correct": is_correct,
    }


def valid_sample(**overrides) -> dict[str, object]:
    sample = {
        "id": "sample-1",
        "source_group": "generated_symbolic",
        "question_type": "multiple_choice",
        "statement": "Tinh dinh thuc 2x2.",
        "choices": [
            choice("A", "-2", True),
            choice("B", "2"),
            choice("C", "10"),
            choice("D", "-10"),
        ],
        "correct_choice": "A",
        "expected_answer": "-2",
        "expected_problem_type_code": "GT1_C2_02_T04_Newton_Leibniz",
        "expected_difficulty": "easy",
        "solver_code": "DET_2X2",
        "params": {"a11": 1, "a12": 2, "a21": 3, "a22": 4},
    }
    sample.update(overrides)

    return sample


def test_evaluator_returns_zero_rates_for_empty_dataset() -> None:
    report = evaluate_samples([])

    assert report["total"] == 0
    assert set(report["metrics"]) == set(METRIC_KEYS)
    assert all(value == 0.0 for value in report["metrics"].values())
    assert report["samples"] == []


def test_evaluator_computes_structure_and_blocking_rates() -> None:
    invalid = valid_sample(
        id="sample-2",
        choices=[
            choice("A", "-2", True),
            choice("B", "2"),
            choice("C", "10"),
        ],
    )

    report = evaluate_samples([valid_sample(), invalid], taxonomy_index=None)

    assert report["metrics"]["valid_structure_rate"] == 0.5
    assert report["metrics"]["single_correct_rate"] == 1.0
    assert report["metrics"]["blocking_issue_rate"] == 0.5
    assert report["metrics"]["can_save_rate"] == 0.5
    assert "mcq_invalid_choice_count" in report["samples"][1]["blocking_issues"]
    assert "mcq_invalid_choice_key" in report["samples"][1]["blocking_issues"]


def test_evaluator_computes_symbolic_correct_rate() -> None:
    wrong_symbolic = valid_sample(
        id="sample-2",
        choices=[
            choice("A", "2", True),
            choice("B", "-2"),
            choice("C", "10"),
            choice("D", "-10"),
        ],
        correct_choice="A",
        expected_answer="2",
    )

    report = evaluate_samples([valid_sample(), wrong_symbolic], taxonomy_index=None)

    assert report["counts"]["symbolic_evaluable"] == 2
    assert report["counts"]["symbolic_correct"] == 1
    assert report["metrics"]["symbolic_correct_rate"] == 0.5
    assert "symbolic_correct_answer_mismatch" in report["samples"][1]["blocking_issues"]


def test_evaluator_computes_distractor_and_duplicate_rates() -> None:
    duplicate_choice = valid_sample(
        id="sample-2",
        statement="Tinh dao ham cua x^2.",
        choices=[
            choice("A", "-2", True),
            choice("B", "-2"),
            choice("C", "10"),
            choice("D", "-10"),
        ],
        solver_code=None,
    )
    duplicate_statement = valid_sample(id="sample-3")

    report = evaluate_samples(
        [valid_sample(), duplicate_choice, duplicate_statement],
        taxonomy_index=None,
    )

    assert report["metrics"]["distractor_distinct_rate"] == 2 / 3
    assert report["metrics"]["semantic_duplicate_rate"] == 2 / 3
    assert "mcq_duplicate_choice_content" in report["samples"][1]["blocking_issues"]
    assert "mcq_distractor_equals_correct_answer" in report["samples"][1]["blocking_issues"]


def test_evaluator_computes_taxonomy_and_warning_rates() -> None:
    _, taxonomy_index = load_validated_taxonomy()
    no_solver = valid_sample(id="sample-2", solver_code=None)
    invalid_taxonomy = valid_sample(
        id="sample-3",
        expected_problem_type_code="missing-code",
        solver_code=None,
    )

    report = evaluate_samples(
        [valid_sample(), no_solver, invalid_taxonomy],
        taxonomy_index=taxonomy_index,
    )

    assert report["metrics"]["taxonomy_valid_rate"] == 2 / 3
    assert report["metrics"]["warning_rate"] == 2 / 3
    assert "solver_not_available" in report["samples"][1]["warnings"]
    assert "invalid_expected_problem_type_code" in report["samples"][2]["blocking_issues"]
