import json

from pydantic import ValidationError

from modules.question_classification.schemas import (
    ClassificationCandidate,
)


class ClassificationParseError(ValueError):
    pass


def strip_markdown_json_fence(raw_text: str) -> str:
    text = raw_text.strip()

    if not text:
        raise ClassificationParseError(
            "Classification output must not be empty"
        )

    if not text.startswith("```"):
        return text

    lines = text.splitlines()

    if len(lines) < 3 or lines[-1].strip() != "```":
        raise ClassificationParseError(
            "Classification output contains an invalid Markdown fence"
        )

    opening_fence = lines[0].strip().lower()

    if opening_fence not in {"```", "```json"}:
        raise ClassificationParseError(
            "Classification output uses an unsupported Markdown fence"
        )

    return "\n".join(lines[1:-1]).strip()


def parse_classification_candidate(
    raw_text: str,
) -> ClassificationCandidate:
    cleaned_text = strip_markdown_json_fence(raw_text)

    try:
        raw_data = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ClassificationParseError(
            "Classification output is not valid JSON"
        ) from exc

    if not isinstance(raw_data, dict):
        raise ClassificationParseError(
            "Classification output must be a JSON object"
        )

    try:
        return ClassificationCandidate.model_validate(raw_data)
    except ValidationError as exc:
        raise ClassificationParseError(
            "Classification output does not match the required schema"
        ) from exc