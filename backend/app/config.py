"""Application configuration loaded from environment variables (pydantic-settings).

All variables map to the contract in `.env.example`. Sensible local defaults are
provided so the app can boot, run tests, and `py_compile` without a real `.env`.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Placeholder API-key fragments from `.env.example`. If the configured key matches
# one of these (or is empty), we treat it as "no real key" and use the StubProvider.
_PLACEHOLDER_KEY_MARKERS = (
    "sk-ant-your-",
    "your-anthropic-api-key",
    "change-me",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---------------------------------------------------------------
    app_env: str = "local"
    secret_key: str = "change-me-please-generate-a-long-random-string"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # --- Database ----------------------------------------------------------
    database_url: str = (
        "postgresql+psycopg://myuno:change-me-postgres-password@localhost:5432/myuno_capital"
    )
    # Postgres schema the app's tables live in. Use a dedicated schema (e.g.
    # "myuno_capital") when sharing a database instance with other products;
    # "public" keeps the default behaviour for standalone deployments.
    db_schema: str = "public"

    # --- Redis / Celery ----------------------------------------------------
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # --- S3 / MinIO --------------------------------------------------------
    s3_endpoint: str = "http://localhost:9000"
    s3_bucket: str = "myuno-artifacts"
    s3_access_key: str = "myuno-minio"
    s3_secret_key: str = "change-me-minio-password"
    s3_region: str = "us-east-1"

    # --- LLM ---------------------------------------------------------------
    anthropic_api_key: str = "sk-ant-your-anthropic-api-key-here"
    default_llm_model: str = "claude-opus-4-8"
    llm_fallback_model: str = "claude-haiku-4-5"

    # --- Auth (JWT) --------------------------------------------------------
    jwt_secret: str = "change-me-please-generate-a-long-random-jwt-secret"
    jwt_expire_minutes: int = 60
    jwt_algorithm: str = "HS256"
    # Refresh-token lifetime (days). Not in .env.example; sensible default.
    jwt_refresh_expire_days: int = 30

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        """Normalize managed-host DB URLs to the psycopg async/sync driver.

        Platforms like Render, Railway, and Heroku inject ``DATABASE_URL`` as
        ``postgres://...`` (or ``postgresql://...``). SQLAlchemy + psycopg3
        expects the explicit ``postgresql+psycopg://`` scheme, so rewrite it
        while leaving an already-qualified URL untouched.
        """
        if not isinstance(value, str):
            return value
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value[len("postgres://") :]
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value[len("postgresql://") :]
        return value

    # --- Derived helpers ---------------------------------------------------
    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def has_real_anthropic_key(self) -> bool:
        """True only when a non-placeholder Anthropic key is configured."""
        key = (self.anthropic_api_key or "").strip()
        if not key:
            return False
        lowered = key.lower()
        if any(marker in lowered for marker in _PLACEHOLDER_KEY_MARKERS):
            return False
        # A real Anthropic key starts with `sk-ant-` and is reasonably long.
        return key.startswith("sk-ant-") and len(key) > 24


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
