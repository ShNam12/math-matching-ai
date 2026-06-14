import json

import pytest

from modules.question_classification import (
    ClassificationParseError,
    parse_classification_candidate,
    strip_markdown_json_fence,
)


def valid_output() -> dict:
    return {
        "chapter_code": (
            "GT1_C1_Differential_Calculus_One_Variable"
        ),
        "topic_code": "GT1_C1_05_Function_Limits",
        "problem_type_code": (
            "GT1_C1_05_T02_Algebraic_Transformation_Limit"
        ),
        "skills": [
            "function_limit",
            "algebraic_transformation",
        ],
        "difficulty": "medium",
        "confidence": 0.88,
        "reason": "Cần biến đổi đại số để tính giới hạn.",
    }


def test_parse_clean_json() -> None:
    candidate = parse_classification_candidate(
        json.dumps(valid_output(), ensure_ascii=False)
    )

    assert candidate.confidence == 0.88
    assert candidate.difficulty == "medium"


def test_parse_json_markdown_fence() -> None:
    raw_text = (
        "```json\n"
        + json.dumps(valid_output(), ensure_ascii=False)
        + "\n```"
    )

    candidate = parse_classification_candidate(raw_text)

    assert candidate.topic_code == (
        "GT1_C1_05_Function_Limits"
    )


def test_parse_plain_markdown_fence() -> None:
    raw_text = (
        "```\n"
        + json.dumps(valid_output(), ensure_ascii=False)
        + "\n```"
    )

    candidate = parse_classification_candidate(raw_text)

    assert candidate.problem_type_code.endswith(
        "Algebraic_Transformation_Limit"
    )


def test_parser_rejects_empty_output() -> None:
    with pytest.raises(
        ClassificationParseError,
        match="must not be empty",
    ):
        parse_classification_candidate("   ")


def test_parser_rejects_invalid_json() -> None:
    with pytest.raises(
        ClassificationParseError,
        match="not valid JSON",
    ):
        parse_classification_candidate("{invalid-json}")


def test_parser_rejects_json_array() -> None:
    with pytest.raises(
        ClassificationParseError,
        match="must be a JSON object",
    ):
        parse_classification_candidate("[]")


def test_parser_rejects_missing_required_field() -> None:
    data = valid_output()
    data.pop("topic_code")

    with pytest.raises(
        ClassificationParseError,
        match="required schema",
    ):
        parse_classification_candidate(
            json.dumps(data, ensure_ascii=False)
        )


def test_parser_rejects_extra_field() -> None:
    data = valid_output()
    data["invented_field"] = "not allowed"

    with pytest.raises(
        ClassificationParseError,
        match="required schema",
    ):
        parse_classification_candidate(
            json.dumps(data, ensure_ascii=False)
        )


def test_parser_rejects_invalid_difficulty() -> None:
    data = valid_output()
    data["difficulty"] = "very_hard"

    with pytest.raises(ClassificationParseError):
        parse_classification_candidate(
            json.dumps(data, ensure_ascii=False)
        )


def test_parser_rejects_invalid_confidence() -> None:
    data = valid_output()
    data["confidence"] = 1.5

    with pytest.raises(ClassificationParseError):
        parse_classification_candidate(
            json.dumps(data, ensure_ascii=False)
        )


def test_strip_fence_rejects_unclosed_fence() -> None:
    with pytest.raises(
        ClassificationParseError,
        match="invalid Markdown fence",
    ):
        strip_markdown_json_fence(
            '```json\n{"confidence": 0.9}'
        )


def test_parser_preserves_vietnamese_reason() -> None:
    candidate = parse_classification_candidate(
        json.dumps(valid_output(), ensure_ascii=False)
    )

    assert candidate.reason == (
        "Cần biến đổi đại số để tính giới hạn."
    )