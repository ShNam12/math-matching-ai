import asyncio

from apps.api.v1.endpoints.analytics import get_analytics_summary


class FakeScalars:
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values


class FakeResult:
    def __init__(self, rows=None, scalars=None):
        self.rows = rows or []
        self.scalar_values = scalars or []

    def all(self):
        return self.rows

    def scalars(self):
        return FakeScalars(self.scalar_values)


class FakeSession:
    def __init__(self, results):
        self.results = list(results)

    async def execute(self, statement):
        assert statement is not None
        return self.results.pop(0)


def test_analytics_summary_returns_mcq_metrics() -> None:
    session = FakeSession(
        [
            FakeResult(rows=[("completed", 1)]),
            FakeResult(rows=[("completed", 4)]),
            FakeResult(rows=[("medium", 3), ("easy", 1)]),
            FakeResult(rows=[("Chapter 1", 1), ("Chapter 2", 3)]),
            FakeResult(rows=[("Topic A", 2), ("Topic B", 2)]),
            FakeResult(
                scalars=[
                    [{"latex": "x+1"}],
                    [],
                    [{"latex": "x^2"}, {"latex": "2x"}],
                ]
            ),
            FakeResult(
                rows=[
                    (
                        "multiple_choice",
                        {
                            "can_save": True,
                            "warnings": [],
                            "blocking_issues": [],
                            "symbolic_checks": [
                                {
                                    "code": "symbolic_correct_answer_verified",
                                    "passed": True,
                                }
                            ],
                        },
                        "ADD_INT",
                        "symbolic",
                        "validated",
                    ),
                    (
                        "multiple_choice",
                        {
                            "can_save": False,
                            "warnings": [],
                            "blocking_issues": [
                                {
                                    "code": (
                                        "mcq_distractor_equals_correct_answer"
                                    )
                                },
                                {
                                    "code": "symbolic_correct_answer_mismatch",
                                }
                            ],
                            "symbolic_checks": [],
                        },
                        None,
                        "ai",
                        "rejected",
                    ),
                    (
                        "multiple_choice",
                        {
                            "can_save": True,
                            "warnings": [
                                {
                                    "code": "solver_not_available",
                                }
                            ],
                            "blocking_issues": [],
                            "symbolic_checks": [
                                {
                                    "code": "solver_not_available",
                                    "passed": False,
                                }
                            ],
                        },
                        None,
                        "ai_convert",
                        "needs_review",
                    ),
                    (
                        "free_response",
                        {},
                        None,
                        None,
                        None,
                    ),
                ]
            ),
        ]
    )

    response = asyncio.run(get_analytics_summary(session=session))

    assert response.question_count == 4
    assert response.formula_count == 3
    assert response.multiple_choice_question_count == 3
    assert response.free_response_question_count == 1
    assert response.validated_mcq_count == 2
    assert response.blocking_mcq_count == 1
    assert response.symbolic_validated_question_count == 1
    assert response.correct_answer_error_count == 1
    assert response.distractor_error_count == 1
    assert response.solver_unavailable_count == 1
    assert response.needs_review_count == 1
    assert response.valid_mcq_rate == 2 / 3
    assert response.correct_answer_error_rate == 1 / 3
    assert response.distractor_error_rate == 1 / 3
    assert response.solver_unavailable_rate == 1 / 3
    assert response.needs_review_rate == 1 / 3
    assert response.question_type_counts == {
        "multiple_choice": 3,
        "free_response": 1,
    }
    assert response.topic_counts == {"Topic A": 2, "Topic B": 2}
    assert response.generation_method_counts == {
        "symbolic": 1,
        "ai": 1,
        "ai_convert": 1,
    }


def test_analytics_summary_handles_no_mcq() -> None:
    session = FakeSession(
        [
            FakeResult(rows=[]),
            FakeResult(rows=[("pending", 1)]),
            FakeResult(rows=[]),
            FakeResult(rows=[]),
            FakeResult(rows=[]),
            FakeResult(scalars=[]),
            FakeResult(rows=[("free_response", {}, None, None, None)]),
        ]
    )

    response = asyncio.run(get_analytics_summary(session=session))

    assert response.multiple_choice_question_count == 0
    assert response.free_response_question_count == 1
    assert response.distractor_error_rate == 0.0
    assert response.valid_mcq_rate == 0.0
    assert response.correct_answer_error_rate == 0.0
    assert response.solver_unavailable_rate == 0.0
    assert response.needs_review_rate == 0.0
