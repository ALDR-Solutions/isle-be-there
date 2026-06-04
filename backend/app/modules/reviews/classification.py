"""Unified review classification facade with lazy ML loading."""

from __future__ import annotations

from .keyword_classifier import BUSINESS_TYPE_UUIDS, check_flags, classify_with_keywords

KEYWORD_BUSINESS_TYPE_UUIDS = {
    BUSINESS_TYPE_UUIDS["events"],
    BUSINESS_TYPE_UUIDS["tours"],
    BUSINESS_TYPE_UUIDS["services"],
}


def check_review_flags(text: str) -> dict:
    return check_flags(text)


def is_keyword_business_type(business_type_uuid: str) -> bool:
    return business_type_uuid in KEYWORD_BUSINESS_TYPE_UUIDS


def fallback_business_type_name(business_type_uuid: str) -> str:
    if business_type_uuid == BUSINESS_TYPE_UUIDS["hotel"]:
        return "Hotel"
    return "Restaurant"


def classify_review_text(
    text: str,
    business_type_uuid: str,
    hotel_name: str | None = None,
    *,
    verbose: bool = False,
) -> dict:
    if is_keyword_business_type(business_type_uuid):
        return classify_with_keywords(text, business_type_uuid)

    from .ml_adapter import classify_review as ml_classify_review

    result = ml_classify_review(
        text=text,
        business_type_uuid=business_type_uuid,
        hotel_name=hotel_name,
        verbose=verbose,
    )

    normalized = dict(result)
    if normalized.get("business_type") == "Hotel":
        normalized["business_type_id"] = BUSINESS_TYPE_UUIDS["hotel"]
    elif normalized.get("business_type") == "Restaurant":
        normalized["business_type_id"] = BUSINESS_TYPE_UUIDS["restaurant"]
    else:
        normalized["business_type_id"] = business_type_uuid
    return normalized
