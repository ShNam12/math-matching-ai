from modules.question_classification import (
    ClassificationEvalItem,
    ClassificationEvalPrediction,
    evaluate_classification_predictions,
)


def make_item(
    item_id: str,
    *,
    chapter_code: str = "chapter_1",
    topic_code: str = "topic_1",
    problem_type_code: str = "problem_type_1",
    difficulty: str = "easy",
) -> ClassificationEvalItem:
    return ClassificationEvalItem(
        id=item_id,
        statement="Tính đạo hàm.",
        expected_chapter_code=chapter_code,
        expected_topic_code=topic_code,
        expected_problem_type_code=problem_type_code,
        expected_difficulty=difficulty,
    )


def make_prediction(
    item_id: str,
    *,
    chapter_code: str | None = "chapter_1",
    topic_code: str | None = "topic_1",
    problem_type_code: str | None = "problem_type_1",
    difficulty: str | None = "easy",
    confidence: float | None = 0.9,
    is_valid: bool = True,
) -> ClassificationEvalPrediction:
    return ClassificationEvalPrediction(
        item_id=item_id,
        chapter_code=chapter_code,
        topic_code=topic_code,
        problem_type_code=problem_type_code,
        difficulty=difficulty,
        confidence=confidence,
        is_valid=is_valid,
    )


def test_evaluate_accuracy_for_all_levels() -> None:
    items = [
        make_item("q1"),
        make_item("q2"),
    ]

    predictions = [
        make_prediction("q1"),
        make_prediction(
            "q2",
            chapter_code="chapter_1",
            topic_code="wrong_topic",
            problem_type_code="wrong_problem_type",
            difficulty="medium",
        ),
    ]

    report = evaluate_classification_predictions(
        items=items,
        predictions=predictions,
    )

    assert report.total == 2
    assert report.chapter_accuracy == 1.0
    assert report.topic_accuracy == 0.5
    assert report.problem_type_accuracy == 0.5
    assert report.difficulty_accuracy == 0.5


def test_invalid_code_rate_counts_invalid_predictions() -> None:
    items = [
        make_item("q1"),
        make_item("q2"),
    ]

    predictions = [
        make_prediction("q1"),
        make_prediction("q2", is_valid=False),
    ]

    report = evaluate_classification_predictions(
        items=items,
        predictions=predictions,
    )

    assert report.invalid_code_rate == 0.5
    assert report.failed_count == 1


def test_low_confidence_rate() -> None:
    items = [
        make_item("q1"),
        make_item("q2"),
        make_item("q3"),
    ]

    predictions = [
        make_prediction("q1", confidence=0.95),
        make_prediction("q2", confidence=0.6),
        make_prediction("q3", confidence=None),
    ]

    report = evaluate_classification_predictions(
        items=items,
        predictions=predictions,
        low_confidence_threshold=0.75,
    )

    assert report.low_confidence_rate == 2 / 3


def test_empty_dataset_does_not_crash() -> None:
    report = evaluate_classification_predictions(
        items=[],
        predictions=[],
    )

    assert report.total == 0
    assert report.chapter_accuracy == 0.0
    assert report.topic_accuracy == 0.0
    assert report.problem_type_accuracy == 0.0
    assert report.difficulty_accuracy == 0.0
    assert report.low_confidence_rate == 0.0
    assert report.invalid_code_rate == 0.0
    assert report.failed_count == 0


def test_missing_prediction_counts_as_failed() -> None:
    items = [
        make_item("q1"),
        make_item("q2"),
    ]

    predictions = [
        make_prediction("q1"),
    ]

    report = evaluate_classification_predictions(
        items=items,
        predictions=predictions,
    )

    assert report.failed_count == 1
    assert report.invalid_code_rate == 0.5