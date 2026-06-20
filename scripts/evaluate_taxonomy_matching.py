import argparse
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from core.config.settings import settings
from modules.question_classification import (
    ClassificationEvalItem,
    GeminiQuestionClassifier,
    QuestionClassificationService,
    evaluate_classification_predictions,
    failed_prediction,
    prediction_from_result,
)


def load_eval_items(path: Path) -> list[ClassificationEvalItem]:
    raw_items = json.loads(path.read_text(encoding="utf-8"))

    return [
        ClassificationEvalItem(
            id=item["id"],
            statement=item["statement"],
            solution=item.get("solution"),
            answer=item.get("answer"),
            formulas=item.get("formulas") or [],
            expected_chapter_code=item["expected_chapter_code"],
            expected_topic_code=item["expected_topic_code"],
            expected_problem_type_code=item["expected_problem_type_code"],
            expected_difficulty=item["expected_difficulty"],
        )
        for item in raw_items
    ]


def make_question(item: ClassificationEvalItem):
    return SimpleNamespace(
        id=item.id,
        statement=item.statement,
        solution=item.solution,
        answer=item.answer,
        formulas=item.formulas or [],
    )


async def run_evaluation(dataset_path: Path) -> None:
    items = load_eval_items(dataset_path)

    service = QuestionClassificationService(
        classifier=GeminiQuestionClassifier(),
    )

    predictions = []

    for index, item in enumerate(items, start=1):
        print(f"[{index}/{len(items)}] Classifying {item.id}...")

        try:
            result = await asyncio.to_thread(
                service.classify_question,
                make_question(item),
            )

            print(f"  Expected chapter: {item.expected_chapter_code}")
            print(f"  Predicted chapter: {result.chapter_code}")
            print(f"  Expected topic: {item.expected_topic_code}")
            print(f"  Predicted topic: {result.topic_code}")
            print(f"  Expected problem type: {item.expected_problem_type_code}")
            print(f"  Predicted problem type: {result.problem_type_code}")
            print(f"  Expected difficulty: {item.expected_difficulty}")
            print(f"  Predicted difficulty: {result.difficulty}")
            print(f"  Confidence: {result.confidence}")
            print(f"  Reason: {result.reason}")
            predictions.append(
                prediction_from_result(
                    item_id=item.id,
                    result=result,
                )
            )
        except Exception as exc:
            predictions.append(
                failed_prediction(
                    item_id=item.id,
                    error=str(exc),
                )
            )

    report = evaluate_classification_predictions(
        items=items,
        predictions=predictions,
        low_confidence_threshold=0.75,
    )

    print()
    print("=== Taxonomy Matching Evaluation ===")
    print(f"Dataset: {dataset_path}")
    print(f"Model: {settings.gemini_model}")
    print(f"Total: {report.total}")
    print(f"Chapter accuracy: {report.chapter_accuracy:.2%}")
    print(f"Topic accuracy: {report.topic_accuracy:.2%}")
    print(f"Problem type accuracy: {report.problem_type_accuracy:.2%}")
    print(f"Difficulty accuracy: {report.difficulty_accuracy:.2%}")
    print(f"Low confidence rate: {report.low_confidence_rate:.2%}")
    print(f"Invalid code rate: {report.invalid_code_rate:.2%}")
    print(f"Failed count: {report.failed_count}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        default="tests/fixtures/calculus_1_classification_eval.json",
    )
    args = parser.parse_args()

    asyncio.run(run_evaluation(Path(args.dataset)))


if __name__ == "__main__":
    main()