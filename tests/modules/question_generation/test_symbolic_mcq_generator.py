import asyncio

from modules.neuro_symbolic import SolverExecutor
from modules.question_generation.symbolic_mcq_generator import SymbolicMCQGenerator


def generate(**kwargs):
    return asyncio.run(SymbolicMCQGenerator(seed=8).generate(**kwargs))


def solver_params(candidate):
    return candidate.choices[0].metadata["solver_params"]


def test_generates_one_mcq_from_solver() -> None:
    candidates = generate(
        solver_code="INT_XN_EXP",
        generation_count=1,
        difficulty="medium",
        subject="calculus",
        chapter="integration",
        skills=["integration_by_parts"],
    )

    candidate = candidates[0]

    assert candidate.question_type == "multiple_choice"
    assert candidate.generation_method == "symbolic"
    assert candidate.solver_code == "INT_XN_EXP"
    assert candidate.difficulty == "medium"
    assert candidate.subject == "calculus"
    assert candidate.chapter == "integration"
    assert candidate.skills == ["integration_by_parts"]
    assert candidate.symbolic_answer == candidate.answer
    assert candidate.validation_report.can_save is True


def test_generates_multiple_mcqs_with_distinct_params() -> None:
    candidates = generate(
        solver_code="INT_XN_EXP",
        generation_count=3,
        seed=20,
    )

    param_keys = {
        tuple(sorted(params.items()))
        for params in [solver_params(candidate) for candidate in candidates]
    }

    assert len(candidates) == 3
    assert len(param_keys) == 3


def test_each_mcq_has_four_choices_and_one_correct_choice() -> None:
    candidate = generate(solver_code="INT_XN_EXP", generation_count=1)[0]
    correct_choices = [choice for choice in candidate.choices if choice.is_correct]

    assert [choice.key for choice in candidate.choices] == ["A", "B", "C", "D"]
    assert len(candidate.choices) == 4
    assert len(correct_choices) == 1
    assert candidate.correct_choice == correct_choices[0].key


def test_correct_answer_matches_solver_output() -> None:
    candidate = generate(solver_code="INT_XN_EXP", generation_count=1)[0]
    params = solver_params(candidate)
    solver_result = SolverExecutor().execute(candidate.solver_code or "", params)
    correct_choice = next(choice for choice in candidate.choices if choice.is_correct)

    assert solver_result.success is True
    assert solver_result.output is not None
    assert candidate.answer == solver_result.output.answer
    assert correct_choice.text == solver_result.output.answer


def test_distractors_do_not_duplicate_correct_answer() -> None:
    candidate = generate(solver_code="INT_XN_EXP", generation_count=1)[0]
    correct_choice = next(choice for choice in candidate.choices if choice.is_correct)
    distractors = [
        choice
        for choice in candidate.choices
        if choice.key != candidate.correct_choice
    ]

    assert all(choice.text != correct_choice.text for choice in distractors)
    assert all(choice.latex != correct_choice.latex for choice in distractors)
    assert all(choice.distractor_type for choice in distractors)


def test_quality_report_can_save_valid_symbolic_mcq() -> None:
    candidate = generate(solver_code="INT_XN_EXP", generation_count=1)[0]

    assert candidate.validation_report.can_save is True
    assert not candidate.validation_report.blocking_issues
    assert any(
        check.code == "symbolic_correct_answer_verified"
        and check.passed is True
        for check in candidate.validation_report.symbolic_checks
    )
