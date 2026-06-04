"""Application package for the Isle Be There backend."""

__all__ = ["app", "main"]


def __getattr__(name: str):
    if name in {"app", "main"}:
        from .main import app

        return app
    raise AttributeError(f"module 'app' has no attribute {name!r}")
