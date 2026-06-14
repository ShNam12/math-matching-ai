import json
from types import SimpleNamespace

import pytest

from modules.question_classification import (
    ClassificationModelError,
    ClassificationParseError,
    GeminiClassificationClient,
    GeminiQuestionClassifier,
)


def valid_output() -> str:
    return json.dumps({
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
        "reason": "Cần biến đổi đại số.",
    }, ensure_ascii=False)


class FakeTextGenerationClient:
    def __init__(
        self,
        outputs: list[str] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.outputs = list(outputs or [])
        self.error = error
        self.prompts: list[str] = []

    def generate_text(self, prompt: str) -> str:
        self.prompts.append(prompt)

        if self.error is not None:
            raise self.error

        return self.outputs.pop(0)


class FakeModels:
    def __init__(
        self,
        response_text: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response_text = response_text
        self.error = error
        self.calls = []

    def generate_content(
        self,
        *,
        model: str,
        contents: str,
        config=None,
    ):
        self.calls.append({
            "model": model,
            "contents": contents,
            "config": config,
        })

        if self.error is not None:
            raise self.error

        return SimpleNamespace(text=self.response_text)


class FakeGeminiClient:
    def __init__(
        self,
        response_text: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self.models = FakeModels(response_text, error)


def make_gemini_client(
    response_text: str | None = None,
    error: Exception | None = None,
) -> GeminiClassificationClient:
    client = GeminiClassificationClient.__new__(
        GeminiClassificationClient
    )
    client.client = FakeGeminiClient(
        response_text=response_text,
        error=error,
    )
    client.model = "fake-gemini-model"
    return client


def test_classifier_returns_parsed_candidate() -> None:
    fake_client = FakeTextGenerationClient(
        outputs=[valid_output()]
    )
    classifier = GeminiQuestionClassifier(
        model_client=fake_client,
    )

    result = classifier.classify("classification prompt")

    assert result.confidence == 0.88
    assert result.difficulty == "medium"
    assert fake_client.prompts == ["classification prompt"]


def test_classifier_retries_once_after_invalid_json() -> None:
    fake_client = FakeTextGenerationClient(
        outputs=[
            "{invalid-json}",
            valid_output(),
        ]
    )
    classifier = GeminiQuestionClassifier(
        model_client=fake_client,
        max_parse_retries=1,
    )

    result = classifier.classify("prompt")

    assert result.confidence == 0.88
    assert len(fake_client.prompts) == 2


def test_classifier_does_not_retry_after_success() -> None:
    fake_client = FakeTextGenerationClient(
        outputs=[
            valid_output(),
            valid_output(),
        ]
    )
    classifier = GeminiQuestionClassifier(
        model_client=fake_client,
        max_parse_retries=1,
    )

    classifier.classify("prompt")

    assert len(fake_client.prompts) == 1


def test_classifier_stops_after_retry_limit() -> None:
    fake_client = FakeTextGenerationClient(
        outputs=[
            "{invalid-first}",
            "{invalid-second}",
        ]
    )
    classifier = GeminiQuestionClassifier(
        model_client=fake_client,
        max_parse_retries=1,
    )

    with pytest.raises(
        ClassificationParseError,
        match="after 2 attempt",
    ):
        classifier.classify("prompt")

    assert len(fake_client.prompts) == 2


def test_classifier_can_disable_retry() -> None:
    fake_client = FakeTextGenerationClient(
        outputs=["{invalid-json}"]
    )
    classifier = GeminiQuestionClassifier(
        model_client=fake_client,
        max_parse_retries=0,
    )

    with pytest.raises(
        ClassificationParseError,
        match="after 1 attempt",
    ):
        classifier.classify("prompt")

    assert len(fake_client.prompts) == 1


def test_classifier_rejects_empty_prompt() -> None:
    fake_client = FakeTextGenerationClient(
        outputs=[valid_output()]
    )
    classifier = GeminiQuestionClassifier(
        model_client=fake_client,
    )

    with pytest.raises(ValueError, match="must not be empty"):
        classifier.classify("   ")

    assert fake_client.prompts == []


def test_classifier_rejects_negative_retry_count() -> None:
    with pytest.raises(
        ValueError,
        match="must not be negative",
    ):
        GeminiQuestionClassifier(
            model_client=FakeTextGenerationClient(),
            max_parse_retries=-1,
        )


def test_model_error_is_not_retried() -> None:
    fake_client = FakeTextGenerationClient(
        error=ClassificationModelError(
            "Gemini request failed"
        )
    )
    classifier = GeminiQuestionClassifier(
        model_client=fake_client,
        max_parse_retries=1,
    )

    with pytest.raises(
        ClassificationModelError,
        match="Gemini request failed",
    ):
        classifier.classify("prompt")

    assert len(fake_client.prompts) == 1


def test_gemini_client_returns_stripped_text() -> None:
    client = make_gemini_client(
        response_text=f"  {valid_output()}  "
    )

    result = client.generate_text("prompt")

    assert result == valid_output()

    call = client.client.models.calls[0]
    assert call["model"] == "fake-gemini-model"
    assert call["contents"] == "prompt"
    assert call["config"] is not None


def test_gemini_client_rejects_empty_prompt() -> None:
    client = make_gemini_client(valid_output())

    with pytest.raises(ValueError, match="must not be empty"):
        client.generate_text("   ")


def test_gemini_client_rejects_empty_response() -> None:
    client = make_gemini_client("   ")

    with pytest.raises(
        ClassificationModelError,
        match="empty classification output",
    ):
        client.generate_text("prompt")


def test_gemini_client_wraps_api_error() -> None:
    client = make_gemini_client(
        error=RuntimeError("network unavailable")
    )

    with pytest.raises(
        ClassificationModelError,
        match="classification request failed",
    ):
        client.generate_text("prompt")