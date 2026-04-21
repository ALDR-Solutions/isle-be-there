"""
Application configuration.
"""
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    APP_NAME: str = "Isle Be There API"
    ENV: str = "development"
    model_config = {"env_file": ".env", "extra": "ignore"}
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 10
    FORGET_PWD_SECRET_KEY: str
    MAIL_FROM: str = "noreply@islebthere.com"
    FRONTEND_URL: str = "http://localhost:5173"
    RESEND_API_KEY: str

settings = AppSettings()

__all__ = ["settings", "AppSettings"]
