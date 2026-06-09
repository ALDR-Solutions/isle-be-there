"""Unified review classification orchestration."""

from __future__ import annotations

import json
import logging

from .classifiers.keyword_classifier import (
    classify_with_keywords,
    get_classification_approach,
)
from .classifiers.ml_classifier import classify_review as ml_classify_review

logger = logging.getLogger(__name__)


def _normalize_labels(classification_result: dict) -> dict:
    main_label = classification_result.get("main_label") or "(none)"
    second_label = classification_result.get("second_label") or "(none)"
    third_label = classification_result.get("third_label") or "(none)"

    return {
        "main_label": main_label,
        "second_label": second_label,
        "third_label": third_label,
        "classification_labels": json.dumps([main_label, second_label, third_label]),
    }


def _keyword_result(text: str, business_type_uuid: str, classification_method: str) -> dict:
    normalized = _normalize_labels(classify_with_keywords(text, business_type_uuid))
    normalized.update(
        {
            "detected_lang": None,
            "translated_text": None,
            "classification_method": classification_method,
        }
    )
    return normalized


def classify_review_text(
    text: str,
    business_type_name: str,
    business_type_uuid: str,
    *,
    hotel_name: str | None = None,
    verbose: bool = False,
) -> dict:
    if get_classification_approach(business_type_name) != "ml":
        return _keyword_result(text, business_type_uuid, "keyword")

    try:
        ml_result = ml_classify_review(
            text=text,
            business_type_uuid=business_type_uuid,
            hotel_name=hotel_name,
            verbose=verbose,
        )
    except Exception:
        logger.exception("ML classification failed; falling back to keyword classifier")
        return _keyword_result(text, business_type_uuid, "ml_fallback")

    if ml_result.get("main_label") is None:
        return _keyword_result(text, business_type_uuid, "ml_fallback")

    normalized = _normalize_labels(ml_result)
    normalized.update(
        {
            "detected_lang": ml_result.get("detected_language", "en"),
            "translated_text": ml_result.get("translated_text"),
            "classification_method": "ml",
        }
    )
    return normalized
