from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    embedding_model: str = "gemini-embedding-2"
    embedding_dimension: int = 768

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_question_collection: str = "question_embeddings"
    qdrant_formula_collection: str = "formula_embeddings"

    r2_endpoint_url: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str
    r2_public_base_url: str | None = None

    max_upload_size_mb: int = 40

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
