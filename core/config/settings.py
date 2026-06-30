from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    cors_allow_origins: str = "http://localhost:5173"

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

    jwt_secret_key: str = "change-me-for-demo"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allow_origins.split(",")
            if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
