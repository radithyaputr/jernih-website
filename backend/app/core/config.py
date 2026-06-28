from pydantic_settings import BaseSettings
from typing import Optional
import warnings


class Settings(BaseSettings):
    app_name: str = "JERNIH OS API"
    app_version: str = "1.0.0"
    debug: bool = True

    # AI API Keys
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Database
    database_url: str = "postgresql://localhost:5432/jernih"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"

    # Security
    secret_key: str = "jernih-secret-key-change-in-production"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://jernih.app",
    ]

    model_config = {
        "env_file": (".env", "../.env", "../frontend/.env.local", "../.env.local"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()

# Warn only in debug mode
if settings.debug:
    if settings.secret_key == "jernih-secret-key-change-in-production":
        warnings.warn(
            "SECURITY: Using default secret_key. Set SECRET_KEY env variable for production.",
            RuntimeWarning,
            stacklevel=2,
        )
    if not settings.gemini_api_key:
        warnings.warn(
            "GEMINI_API_KEY not set. AI features will use rule-based fallback.",
            RuntimeWarning,
            stacklevel=2,
        )
