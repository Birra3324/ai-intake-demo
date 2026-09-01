"""Environment-driven settings. Keys never live in source."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Intake Automation Platform"
    app_env: str = "development"
    log_level: str = "INFO"

    api_key: str = ""

    database_url: str = "sqlite:///./data/intake.db"

    ai_provider: Literal["ollama", "openai"] = "ollama"
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    ai_timeout_seconds: float = 45.0
    ai_max_retries: int = 3

    slack_webhook_url: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_to: str = ""

    high_value_score: int = 80
    sales_queue_score: int = 50

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def is_test(self) -> bool:
        return self.app_env.lower() in {"test", "testing"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings() -> Settings:
    """Clear the settings cache (used by tests)."""
    get_settings.cache_clear()
    return get_settings()
