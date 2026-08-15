"""Centralised application settings.

Loaded once at startup from environment / .env file.
All governance-specific defaults live here so there is a single source of truth.
"""

from __future__ import annotations

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Immutable application configuration derived from env vars."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ─────────────────────────────────────────
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 9100
    app_title: str = "LexCorp"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── PostgreSQL ──────────────────────────────────
    postgres_host: str = "localhost"
    postgres_port: int = 9432
    postgres_db: str = "lexcorp"
    postgres_user: str = "cso"
    postgres_password: SecretStr = SecretStr("cso_secret_change_me")

    @property
    def database_url(self) -> str:
        pwd = self.postgres_password.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{pwd}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync URL for Alembic migrations."""
        pwd = self.postgres_password.get_secret_value()
        return (
            f"postgresql://{self.postgres_user}:{pwd}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ── Redis ───────────────────────────────────────
    redis_host: str = "localhost"
    redis_port: int = 9379
    redis_password: SecretStr = SecretStr("redis_secret_change_me")

    @property
    def redis_url(self) -> str:
        pwd = self.redis_password.get_secret_value()
        return f"redis://:{pwd}@{self.redis_host}:{self.redis_port}/0"

    @property
    def celery_broker_url(self) -> str:
        return self.redis_url

    @property
    def celery_result_backend(self) -> str:
        pwd = self.redis_password.get_secret_value()
        return f"redis://:{pwd}@{self.redis_host}:{self.redis_port}/1"

    # ── Ollama (self-hosted LLM) ────────────────────
    ollama_base_url: str = "http://localhost:9434"
    ollama_chat_model: str = "qwen2.5:7b"

    # ── Auth (PASETO v4.local) ──────────────────────
    paseto_secret_key: SecretStr = SecretStr("replace-with-a-strong-32-byte-secret-key!!")
    access_token_ttl_minutes: int = 30
    refresh_token_ttl_days: int = 14

    # ── OTEL ────────────────────────────────────────
    otel_exporter_otlp_endpoint: str = "http://localhost:9317"
    otel_service_name: str = "lexcorp-api"

    # ── Security / CORS ─────────────────────────────
    enable_log_masking: bool = True
    cors_allow_origins: str = "http://localhost:9000,http://localhost:9100"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]

    # ── Governance defaults ─────────────────────────
    poa_expiry_warning_days: int = 30
    filing_deadline_warning_days: int = 14
    meeting_reminder_hours: int = 48
    analytics_cache_ttl_seconds: int = 900

    # ── Rate-limiting ───────────────────────────────
    rate_limit_per_minute: int = Field(default=120)


def get_settings() -> Settings:
    """Factory (cacheable at the DI-container level)."""
    return Settings()
