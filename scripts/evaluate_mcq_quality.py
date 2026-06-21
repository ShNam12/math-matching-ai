from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from modules.neuro_symbolic.symbolic_validator import SymbolicMCQValidator
from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    MultipleChoiceOption,
)
from modules.taxonomy import load_validated_taxonomy
from modules.taxonomy.validator import TaxonomyIndex


DEFAULT_DATASET_PATH = Path("tests/fixtures/calculus_1_mcq_eval.json")
EXPECTED_CHOICE_KEYS = {"A", "B", "C", "D"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
METRIC_KEYS = (
    "valid_structure_rate",
    "single_correct_rate",
    "distractor_distinct_rate",
    "symbolic_correct_rate",
    "taxonomy_valid_rate",
    "semantic_duplicate_rate",
    "can_save_rate",
    "warning_rate",
    "blocking_issue_rate",
)


def load_mcq_eval_samples(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_dataset(path: Path = DEFAULT_DATASET_PATH) -> dict[str, Any]:
    _, taxonomy_index = load_validated_taxonomy()

    return evaluate_samples(
        load_mcq_eval_samples(path),
        taxonomy_index=taxonomy_index,
    )


def evaluate_samples(
    samples: list[dict[str, Any]],
    *,
    taxonomy_index: TaxonomyIndex | None = None,
    symbolic_validator: SymbolicMCQValidator | None = None,
) -> dict[str, Any]:
    validator = symbolic_validator or SymbolicMCQValidator()
    total = len(samples)
    duplicate_statement_ids = _duplicate_statement_ids(samples)
    group_counts = Counter(str(sample.get("source_group") or "unknown") for sample in samples)
    sample_reports: list[dict[str, Any]] = []
    counters = Counter()

    for sample in samples:
        report = _evaluate_sample(
            sample,
            duplicate_statement_ids=duplicate_statement_ids,
            taxonomy_index=taxonomy_index,
            symbolic_validator=validator,
        )
        sample_reports.append(report)

        if report["valid_structure"]:
            counters["valid_structure"] += 1
        if report["single_correct"]:
            counters["single_correct"] += 1
        if report["distractor_distinct"]:
            counters["distractor_distinct"] += 1
        if report["taxonomy_valid"]:
            counters["taxonomy_valid"] += 1
        if report["semantic_duplicate"]:
            counters["semantic_duplicate"] += 1
        if report["can_save"]:
            counters["can_save"] += 1
        if report["warnings"]:
            counters["warning"] += 1
        if report["blocking_issues"]:
            counters["blocking_issue"] += 1

        if report["symbolic_evaluable"]:
            counters["symbolic_evaluable"] += 1
            if report["symbolic_correct"]:
                counters["symbolic_correct"] += 1

    metrics = {
        "valid_structure_rate": _rate(counters["valid_structure"], total),
        "single_correct_rate": _rate(counters["single_correct"], total),
        "distractor_distinct_rate": _rate(counters["distractor_distinct"], total),
        "symbolic_correct_rate": _rate(
            counters["symbolic_correct"],
            counters["symbolic_evaluable"],
        ),
        "taxonomy_valid_rate": _rate(counters["taxonomy_valid"], total),
        "semantic_duplicate_rate": _rate(counters["semantic_duplicate"], total),
        "can_save_rate": _rate(counters["can_save"], total),
        "warning_rate": _rate(counters["warning"], total),
        "blocking_issue_rate": _rate(counters["blocking_issue"], total),
    }

    return {
        "total": total,
        "group_counts": dict(sorted(group_counts.items())),
        "counts": {
            "valid_structure": counters["valid_structure"],
            "single_correct": counters["single_correct"],
            "distractor_distinct": counters["distractor_distinct"],
            "symbolic_evaluable": counters["symbolic_evaluable"],
            "symbolic_correct": counters["symbolic_correct"],
            "taxonomy_valid": counters["taxonomy_valid"],
            "semantic_duplicate": counters["semantic_duplicate"],
            "can_save": counters["can_save"],
            "warning": counters["warning"],
            "blocking_issue": counters["blocking_issue"],
        },
        "metrics": metrics,
        "samples": sample_reports,
    }


def _evaluate_sample(
    sample: dict[str, Any],
    *,
    duplicate_statement_ids: set[str],
    taxonomy_index: TaxonomyIndex | None,
    symbolic_validator: SymbolicMCQValidator,
) -> dict[str, Any]:
    sample_id = str(sample.get("id") or "")
    warnings: list[str] = []
    blocking_issues: list[str] = []
    structure_issues = _validate_structure(sample)
    distractor_issues = _validate_distractors(sample)
    taxonomy_issues = _validate_taxonomy(sample, taxonomy_index)
    symbolic_evaluable = sample.get("solver_code") is not None
    symbolic_correct = False

    blocking_issues.extend(structure_issues)
    blocking_issues.extend(distractor_issues)
    blocking_issues.extend(taxonomy_issues)

    symbolic_checks: list[dict[str, Any]] = []

    if symbolic_evaluable:
        symbolic_report = symbolic_validator.validate_candidate(
            _candidate_from_sample(sample),
            params=sample.get("params") if isinstance(sample.get("params"), dict) else {},
        )
        warnings.extend(issue.code for issue in symbolic_report.warnings)
        blocking_issues.extend(issue.code for issue in symbolic_report.blocking_issues)
        symbolic_checks = [check.to_dict() for check in symbolic_report.symbolic_checks]
        symbolic_correct = any(
            check.code == "symbolic_correct_answer_verified" and check.passed
            for check in symbolic_report.symbolic_checks
        )
    elif sample.get("question_type") == "multiple_choice":
        warnings.append("solver_not_available")

    semantic_duplicate = sample_id in duplicate_statement_ids

    return {
        "id": sample_id,
        "source_group": sample.get("source_group"),
        "valid_structure": not structure_issues,
        "single_correct": _has_single_correct_choice(sample),
        "distractor_distinct": not distractor_issues,
        "symbolic_evaluable": symbolic_evaluable,
        "symbolic_correct": symbolic_correct,
        "taxonomy_valid": not taxonomy_issues,
        "semantic_duplicate": semantic_duplicate,
        "can_save": not blocking_issues,
        "warnings": sorted(set(warnings)),
        "blocking_issues": sorted(set(blocking_issues)),
        "symbolic_checks": symbolic_checks,
    }


def _validate_structure(sample: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    choices = _choices(sample)

    if not str(sample.get("statement") or "").strip():
        issues.append("empty_statement")

    if sample.get("question_type") != "multiple_choice":
        issues.append("invalid_question_type")

    if len(choices) != 4:
        issues.append("mcq_invalid_choice_count")

    choice_keys = [_choice_key(choice) for choice in choices]

    if set(choice_keys) != EXPECTED_CHOICE_KEYS:
        issues.append("mcq_invalid_choice_key")

    if len(choice_keys) != len(set(choice_keys)):
        issues.append("mcq_duplicate_choice_key")

    if any(not str(choice.get("text") or "").strip() for choice in choices):
        issues.append("mcq_empty_choice_text")

    correct_choice = sample.get("correct_choice")

    if not correct_choice:
        issues.append("mcq_missing_correct_choice")
    elif str(correct_choice) not in choice_keys:
        issues.append("mcq_correct_choice_not_found")

    if not _has_single_correct_choice(sample):
        issues.append("mcq_single_correct_invalid")

    return issues


def _validate_distractors(sample: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    choices = _choices(sample)
    normalized_by_key = {
        _choice_key(choice): _normalize_choice_content(choice)
        for choice in choices
    }
    normalized_values = [
        value for value in normalized_by_key.values() if value
    ]

    if len(normalized_values) != len(set(normalized_values)):
        issues.append("mcq_duplicate_choice_content")

    correct_choice = str(sample.get("correct_choice") or "")
    correct_value = normalized_by_key.get(correct_choice)

    if correct_value:
        for key, value in normalized_by_key.items():
            if key != correct_choice and value == correct_value:
                issues.append("mcq_distractor_equals_correct_answer")
                break

    return issues


def _validate_taxonomy(
    sample: dict[str, Any],
    taxonomy_index: TaxonomyIndex | None,
) -> list[str]:
    issues: list[str] = []
    problem_type_code = str(sample.get("expected_problem_type_code") or "")

    if not problem_type_code:
        issues.append("missing_expected_problem_type_code")
    elif taxonomy_index is not None and problem_type_code not in taxonomy_index.problem_types:
        issues.append("invalid_expected_problem_type_code")

    if sample.get("expected_difficulty") not in VALID_DIFFICULTIES:
        issues.append("invalid_expected_difficulty")

    return issues


def _candidate_from_sample(sample: dict[str, Any]) -> GeneratedQuestionCandidate:
    return GeneratedQuestionCandidate(
        statement=str(sample.get("statement") or ""),
        solution=None,
        answer=(
            str(sample["expected_answer"])
            if sample.get("expected_answer") is not None
            else None
        ),
        subject="calculus",
        chapter=None,
        difficulty=(
            str(sample["expected_difficulty"])
            if sample.get("expected_difficulty") is not None
            else None
        ),
        skills=[],
        formulas=[],
        quality_warnings=[],
        question_type=str(sample.get("question_type") or "multiple_choice"),
        choices=[
            MultipleChoiceOption.from_dict(choice)
            for choice in _choices(sample)
        ],
        correct_choice=(
            str(sample["correct_choice"])
            if sample.get("correct_choice") is not None
            else None
        ),
        symbolic_answer=(
            str(sample["expected_answer"])
            if sample.get("expected_answer") is not None
            else None
        ),
        generation_method=str(sample.get("source_group") or ""),
        solver_code=(
            str(sample["solver_code"])
            if sample.get("solver_code") is not None
            else None
        ),
    )


def _duplicate_statement_ids(samples: list[dict[str, Any]]) -> set[str]:
    normalized_to_ids: dict[str, list[str]] = {}

    for sample in samples:
        normalized = _normalize_text(str(sample.get("statement") or ""))

        if not normalized:
            continue

        normalized_to_ids.setdefault(normalized, []).append(str(sample.get("id") or ""))

    return {
        sample_id
        for ids in normalized_to_ids.values()
        if len(ids) > 1
        for sample_id in ids
    }


def _has_single_correct_choice(sample: dict[str, Any]) -> bool:
    correct_choice = str(sample.get("correct_choice") or "")
    correct_flags = [
        choice for choice in _choices(sample) if choice.get("is_correct") is True
    ]

    return (
        len(correct_flags) == 1
        and _choice_key(correct_flags[0]) == correct_choice
    )


def _choices(sample: dict[str, Any]) -> list[dict[str, Any]]:
    choices = sample.get("choices")

    return [
        choice for choice in choices if isinstance(choice, dict)
    ] if isinstance(choices, list) else []


def _choice_key(choice: dict[str, Any]) -> str:
    return str(choice.get("key") or "").strip().upper()


def _normalize_choice_content(choice: dict[str, Any]) -> str:
    return _normalize_text(str(choice.get("latex") or choice.get("text") or ""))


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0

    return numerator / denominator


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = evaluate_dataset(Path(args.dataset))

    print(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2 if args.pretty else None,
        )
    )


if __name__ == "__main__":
    main()
