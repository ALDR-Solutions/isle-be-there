"""Application-wide configuration and runtime validation helpers."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILES = (str(ROOT_DIR / ".env"), str(ROOT_DIR / "backend" / ".env"))
LOCAL_ENVIRONMENTS = {"development", "dev", "local", "test"}
DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
)
DEFAULT_PRODUCTION_CORS_ORIGINS = (
    "https://islebthere.com",
    "https://www.islebthere.com",
)
DEFAULT_ALLOWED_IMAGE_MIME_TYPES = (
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
)


def _normalize_origin(value: str) -> str:
    return value.strip().rstrip("/")


def _dedupe_origins(origins: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()

    for origin in origins:
        normalized = _normalize_origin(origin)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)

    return deduped


class AppSettings(BaseSettings):
    APP_NAME: str = "Isle Be There API"
    ENV: str = "development"
    TESTING: bool = False
    ENABLE_BACKGROUND_JOBS: bool = True
    DATABASE_URL: str | None = None
    SQL_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 0
    DB_POOL_TIMEOUT: int = 30

    STRIPE_SECRET_KEY: str | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None

    FRONTEND_BASE_URL: str = "http://localhost:5173"
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ALLOW_ORIGINS: str = ""

    JWT_SECRET_KEY: str | None = None
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 10
    FORGET_PWD_SECRET_KEY: str | None = None

    MAIL_FROM: str = "noreply@islebthere.com"
    RESEND_API_KEY: str | None = None

    SUPABASE_URL: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    SUPABASE_KEY: str | None = None
    SUPABASE_STORAGE_BUCKET: str = "uploads"
    MAX_UPLOAD_FILE_SIZE_MB: int = 10
    ALLOWED_IMAGE_MIME_TYPES: str = ",".join(DEFAULT_ALLOWED_IMAGE_MIME_TYPES)

    model_config = SettingsConfigDict(env_file=ENV_FILES, extra="ignore")

    @property
    def is_local_env(self) -> bool:
        return self.ENV.strip().lower() in LOCAL_ENVIRONMENTS

    @property
    def should_start_background_jobs(self) -> bool:
        return self.ENABLE_BACKGROUND_JOBS and not self.TESTING

    @property
    def cors_allow_origins(self) -> list[str]:
        configured = self.CORS_ALLOW_ORIGINS.strip()
        if configured:
            return _dedupe_origins([
                origin.strip()
                for origin in configured.split(",")
                if origin.strip()
            ])
        return _dedupe_origins([
            *DEFAULT_CORS_ORIGINS,
            *DEFAULT_PRODUCTION_CORS_ORIGINS,
            self.FRONTEND_URL,
            self.FRONTEND_BASE_URL,
        ])

    @property
    def resolved_frontend_url(self) -> str:
        return self.FRONTEND_URL.rstrip("/") or self.FRONTEND_BASE_URL.rstrip("/")

    @property
    def allowed_image_mime_types(self) -> set[str]:
        configured = self.ALLOWED_IMAGE_MIME_TYPES.strip()
        if not configured:
            return set(DEFAULT_ALLOWED_IMAGE_MIME_TYPES)
        return {
            value.strip().lower()
            for value in configured.split(",")
            if value.strip()
        }

    @property
    def max_upload_file_size_bytes(self) -> int:
        return self.MAX_UPLOAD_FILE_SIZE_MB * 1024 * 1024

    @property
    def supabase_storage_bucket(self) -> str:
        return self.SUPABASE_STORAGE_BUCKET.strip() or "uploads"

    def get_jwt_secret_key(self) -> str:
        if self.JWT_SECRET_KEY:
            return self.JWT_SECRET_KEY
        if self.is_local_env:
            return "local-dev-jwt-secret-change-me"
        raise RuntimeError(
            "JWT_SECRET_KEY is required when ENV is not a local/test environment."
        )

    def get_password_reset_secret_key(self) -> str:
        if self.FORGET_PWD_SECRET_KEY:
            return self.FORGET_PWD_SECRET_KEY
        if self.is_local_env:
            return f"{self.get_jwt_secret_key()}-password-reset"
        raise RuntimeError(
            "FORGET_PWD_SECRET_KEY is required when ENV is not a local/test environment."
        )

    def require_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        raise RuntimeError("DATABASE_URL is required to initialize the database engine.")

    def require_stripe_secret_key(self) -> str:
        if self.STRIPE_SECRET_KEY:
            return self.STRIPE_SECRET_KEY
        raise RuntimeError("STRIPE_SECRET_KEY is required for Stripe operations.")

    def require_stripe_webhook_secret(self) -> str:
        if self.STRIPE_WEBHOOK_SECRET:
            return self.STRIPE_WEBHOOK_SECRET
        raise RuntimeError("STRIPE_WEBHOOK_SECRET is required for Stripe webhooks.")

    def require_resend_api_key(self) -> str:
        if self.RESEND_API_KEY:
            return self.RESEND_API_KEY
        raise RuntimeError("RESEND_API_KEY is required for email delivery.")

    def require_supabase_url(self) -> str:
        if self.SUPABASE_URL:
            return self.SUPABASE_URL.rstrip("/")
        raise RuntimeError("SUPABASE_URL is required for storage operations.")

    def require_supabase_service_role_key(self) -> str:
        if self.SUPABASE_SERVICE_ROLE_KEY:
            return self.SUPABASE_SERVICE_ROLE_KEY
        if self.SUPABASE_KEY:
            return self.SUPABASE_KEY
        raise RuntimeError(
            "SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY is required for storage operations."
        )

    def validate_runtime(self) -> None:
        self.get_jwt_secret_key()
        self.get_password_reset_secret_key()


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


settings = get_settings()

__all__ = ["AppSettings", "get_settings", "settings", "ROOT_DIR", "ENV_FILES"]
