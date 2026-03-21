"""
Application configuration.
"""
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    APP_NAME: str = "Isle Be There API"
    ENV: str = "development"
    model_config = {"env_file": ".env", "extra": "ignore"}


settings = AppSettings()

__all__ = ["settings", "AppSettings"]
