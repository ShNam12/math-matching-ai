from types import SimpleNamespace

import pytest

from modules.question_generation.gemini_generator import GeminiQuestionGenerator


class FakeModels:
    def __init__(self, response_text):
        self.response_text = response_text
        self.calls = []

    def generate_content(self, *, model: str, contents: str, config=None):
        self.calls.append(
            {
                "model": model,
                "contents": contents,
                "config": config,
            }
        )

        return SimpleNamespace(text=self.response_text)


class FakeClient:
    def __init__(self, response_text):
        self.models = FakeModels(response_text)


def make_generator(response_text="generated text"):
    generator = GeminiQuestionGenerator.__new__(GeminiQuestionGenerator)
    generator.client = FakeClient(response_text)
    generator.model = "fake-model"
    return generator


def test_generate_text_returns_stripped_response_text() -> None:
    generator = make_generator("  generated text  ")

    result = generator.generate_text("prompt")

    assert result == "generated text"
    assert generator.client.models.calls[0]["model"] == "fake-model"
    assert generator.client.models.calls[0]["contents"] == "prompt"
    assert generator.client.models.calls[0]["config"] is not None


def test_generate_text_rejects_empty_prompt() -> None:
    generator = make_generator("generated text")

    with pytest.raises(ValueError, match="must not be empty"):
        generator.generate_text("   ")


def test_generate_text_rejects_empty_response() -> None:
    generator = make_generator("   ")

    with pytest.raises(ValueError, match="empty generation output"):
        generator.generate_text("prompt")


def test_generate_text_rejects_missing_response_text() -> None:
    generator = make_generator(None)

    with pytest.raises(ValueError, match="empty generation output"):
        generator.generate_text("prompt")