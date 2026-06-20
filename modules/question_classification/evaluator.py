from dataclasses import dataclass
from typing import Iterable

from modules.question_classification.schemas import (
    QuestionClassificationResult,
)


@dataclass(frozen=True)
class ClassificationEvalItem:
    id: str
    statement: str
    expected_chapter_code: str
    expected_topic_code: str
    expected_problem_type_code: str
    expected_difficulty: str
    solution: str | None = None
    answer: str | None = None
    formulas: list[dict[str, str]] | None = None


@dataclass(frozen=True)
class ClassificationEvalPrediction:
    item_id: str
    chapter_code: str | None
    topic_code: str | None
    problem_type_code: str | None
    difficulty: str | None
    confidence: float | None
    is_valid: bool = True
    error: str | None = None


@dataclass(frozen=True)
class ClassificationEvalReport:
    total: int
    chapter_accuracy: float
    topic_accuracy: float
    problem_type_accuracy: float
    difficulty_accuracy: float
    low_confidence_rate: float
    invalid_code_rate: float
    failed_count: int


def prediction_from_result(
    *,
    item_id: str,
    result: QuestionClassificationResult,
) -> ClassificationEvalPrediction:
    return ClassificationEvalPrediction(
        item_id=item_id,
        chapter_code=result.chapter_code,
        topic_code=result.topic_code,
        problem_type_code=result.problem_type_code,
        difficulty=result.difficulty,
        confidence=result.confidence,
        is_valid=True,
        error=None,
    )


def failed_prediction(
    *,
    item_id: str,
    error: str,
) -> ClassificationEvalPrediction:
    return ClassificationEvalPrediction(
        item_id=item_id,
        chapter_code=None,
        topic_code=None,
        problem_type_code=None,
        difficulty=None,
        confidence=None,
        is_valid=False,
        error=error,
    )


def evaluate_classification_predictions(
    *,
    items: Iterable[ClassificationEvalItem],
    predictions: Iterable[ClassificationEvalPrediction],
    low_confidence_threshold: float = 0.75,
) -> ClassificationEvalReport:
    item_list = list(items)
    prediction_by_id = {
        prediction.item_id: prediction
        for prediction in predictions
    }

    total = len(item_list)

    if total == 0:
        return ClassificationEvalReport(
            total=0,
            chapter_accuracy=0.0,
            topic_accuracy=0.0,
            problem_type_accuracy=0.0,
            difficulty_accuracy=0.0,
            low_confidence_rate=0.0,
            invalid_code_rate=0.0,
            failed_count=0,
        )

    chapter_correct = 0
    topic_correct = 0
    problem_type_correct = 0
    difficulty_correct = 0
    low_confidence_count = 0
    invalid_count = 0
    failed_count = 0

    for item in item_list:
        prediction = prediction_by_id.get(item.id)

        if prediction is None:
            failed_count += 1
            invalid_count += 1
            continue

        if not prediction.is_valid:
            failed_count += 1
            invalid_count += 1
            continue

        if prediction.chapter_code == item.expected_chapter_code:
            chapter_correct += 1

        if prediction.topic_code == item.expected_topic_code:
            topic_correct += 1

        if prediction.problem_type_code == item.expected_problem_type_code:
            problem_type_correct += 1

        if prediction.difficulty == item.expected_difficulty:
            difficulty_correct += 1

        if (
            prediction.confidence is None
            or prediction.confidence < low_confidence_threshold
        ):
            low_confidence_count += 1

    return ClassificationEvalReport(
        total=total,
        chapter_accuracy=chapter_correct / total,
        topic_accuracy=topic_correct / total,
        problem_type_accuracy=problem_type_correct / total,
        difficulty_accuracy=difficulty_correct / total,
        low_confidence_rate=low_confidence_count / total,
        invalid_code_rate=invalid_count / total,
        failed_count=failed_count,
    )