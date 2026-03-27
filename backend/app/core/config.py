"""
Application configuration.
"""
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    APP_NAME: str = "Isle Be There API"
    ENV: str = "development"
    model_config = {"env_file": ".env", "extra": "ignore"}
    MAIL_USERNAME: str = "islebethere@outlook.com"
    MAIL_PASSWORD: str = "ooklmkyskqlpdgid"
    MAIL_FROM: str = "islebethere@outlook.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp-mail.outlook.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    FRONTEND_URL: str = "http://localhost:5173"


settings = AppSettings()

__all__ = ["settings", "AppSettings"]
