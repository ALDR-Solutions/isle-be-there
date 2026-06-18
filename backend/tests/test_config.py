from app.core.config import (
    AppSettings,
    DEFAULT_CORS_ORIGINS,
    DEFAULT_PRODUCTION_CORS_ORIGINS,
)


def test_cors_allow_origins_prefers_explicit_config():
    settings = AppSettings(
        _env_file=None,
        CORS_ALLOW_ORIGINS=" https://foo.example/ , https://bar.example ",
    )

    assert settings.cors_allow_origins == [
        "https://foo.example",
        "https://bar.example",
    ]


def test_cors_allow_origins_falls_back_to_local_and_production_defaults():
    settings = AppSettings(
        _env_file=None,
        FRONTEND_URL="http://localhost:5173",
        FRONTEND_BASE_URL="http://localhost:5173",
    )

    assert settings.cors_allow_origins == [
        *DEFAULT_CORS_ORIGINS,
        *DEFAULT_PRODUCTION_CORS_ORIGINS,
    ]


def test_cors_allow_origins_includes_configured_frontend_urls_in_fallback():
    settings = AppSettings(
        _env_file=None,
        FRONTEND_URL="https://preview.islebthere.com/",
        FRONTEND_BASE_URL="https://staging.islebthere.com/",
    )

    assert settings.cors_allow_origins == [
        *DEFAULT_CORS_ORIGINS,
        *DEFAULT_PRODUCTION_CORS_ORIGINS,
        "https://preview.islebthere.com",
        "https://staging.islebthere.com",
    ]
