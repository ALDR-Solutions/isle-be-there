"""
Application configuration.
"""
from typing import Optional

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    APP_NAME: str = "Isle Be There API"
    ENV: str = "development"
    # Stripe Configuration
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    FRONTEND_BASE_URL: str = "http://localhost:5173"
    model_config = {"env_file": ".env", "extra": "ignore"}


settings = AppSettings()

__all__ = ["settings", "AppSettings"]
