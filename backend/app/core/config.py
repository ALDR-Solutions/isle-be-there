"""
Application configuration.
"""
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    APP_NAME: str = "Isle Be There API"
    ENV: str = "development"
    HF_TOKEN: str = ""  # HuggingFace token - set via environment variable in production
    MODEL_PATH: str = "models/"  # Path to store trained models
    EMBEDDING_MODEL: str = "paraphrase-MiniLM-L3-v2"  # Smaller model for reduced memory footprint (~100MB vs ~200MB)
    
    model_config = {"env_file": ".env", "extra": "ignore"}


settings = AppSettings()

__all__ = ["settings", "AppSettings"]
