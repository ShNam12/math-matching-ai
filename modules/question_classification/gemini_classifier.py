from typing import Protocol

from google import genai
from google.genai import types

from core.config.settings import settings
from modules.question_classification.json_parser import (
    ClassificationParseError,
    parse_classification_candidate,
)
from modules.question_classification.schemas import (
    ClassificationCandidate,
)


class ClassificationModelError(RuntimeError):
    pass


class TextGenerationClient(Protocol):
    def generate_text(self, prompt: str) -> str:
        ...


class GeminiClassificationClient:
    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
        )
        self.model = settings.gemini_model

    def generate_text(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError(
                "Classification prompt must not be empty"
            )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            raise ClassificationModelError(
                f"Gemini classification request failed: {exc}"
            ) from exc

        text = getattr(response, "text", None)

        if not text or not text.strip():
            raise ClassificationModelError(
                "Gemini returned empty classification output"
            )

        return text.strip()


class GeminiQuestionClassifier:
    def __init__(
        self,
        *,
        model_client: TextGenerationClient | None = None,
        max_parse_retries: int = 1,
    ) -> None:
        if max_parse_retries < 0:
            raise ValueError(
                "max_parse_retries must not be negative"
            )

        self.model_client = (
            model_client or GeminiClassificationClient()
        )
        self.max_parse_retries = max_parse_retries

    def classify(
        self,
        prompt: str,
    ) -> ClassificationCandidate:
        if not prompt.strip():
            raise ValueError(
                "Classification prompt must not be empty"
            )

        attempts = self.max_parse_retries + 1
        last_error: ClassificationParseError | None = None

        for _ in range(attempts):
            raw_output = self.model_client.generate_text(prompt)

            try:
                return parse_classification_candidate(
                    raw_output
                )
            except ClassificationParseError as exc:
                last_error = exc

        raise ClassificationParseError(
            "Gemini returned invalid classification output "
            f"after {attempts} attempt(s): {last_error}"
        ) from last_error