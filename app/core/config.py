"""
Centralised application settings.

Values can be overridden via environment variables or a `.env` file in the
project root.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment / .env."""

    # ── App metadata ──────────────────────────────────────────────────────
    PROJECT_NAME: str = "AI Resume Generator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # ── MongoDB ───────────────────────────────────────────────────────────
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "ai_resume_db"

    # ── AI / NVIDIA ───────────────────────────────────────────────────────
    NVIDIA_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
