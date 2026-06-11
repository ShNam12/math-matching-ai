from typing import Protocol

from google import genai
from google.genai import types

from core.config.settings import settings


class QuestionGenerator(Protocol):
    def generate_text(self, prompt: str) -> str:
        ...


class GeminiQuestionGenerator:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def generate_text(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Generation prompt must not be empty")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        text = getattr(response, "text", None)

        if not text or not text.strip():
            raise ValueError("Gemini returned empty generation output")

        return text.strip()