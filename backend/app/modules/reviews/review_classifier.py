"""Backward-compatible wrapper around the lazy ML review adapter."""

from .ml_adapter import classify_review, detect_language, translate_if_needed, translate_to_english

__all__ = [
    "classify_review",
    "detect_language",
    "translate_if_needed",
    "translate_to_english",
]
