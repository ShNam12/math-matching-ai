from google import genai
from google.genai import types

from core.config.settings import settings


class GeminiEmbedder:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dimension

    def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Embedding text must not be empty")

        result = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=self.dimension,
            ),
        )

        if not result.embeddings:
            raise ValueError("Gemini returned no embedding")

        vector = list(result.embeddings[0].values)

        if len(vector) != self.dimension:
            raise ValueError(
                "Unexpected embedding dimension: "
                f"expected {self.dimension}, got {len(vector)}"
            )

        return vector
    