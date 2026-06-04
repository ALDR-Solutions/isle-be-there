"""Business logic for reviews."""

import json
import logging
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, desc, select

from app.models.listing import Listing, Statuses
from app.models.business import Business
from app.models.business_types import BusinessType
from app.models.review import Review
from app.models.user import User
from app.modules.reviews.classifiers.keyword_classifier import (
    classify_with_keywords,
    get_classification_approach,
)
from app.modules.reviews.classifiers.ml_classifier import (
    classify_review as ml_classify_review,
    _load_models,
    _get_embedding_model_with_timeout,
)
from app.modules.reviews.profanity import censor_text

logger = logging.getLogger(__name__)


def _verify_ml_models() -> bool:
    models_data = _load_models()
    embedding_model = _get_embedding_model_with_timeout(5)
    if models_data is None or embedding_model is None:
        logger.warning(
            "ML classification models not available. "
            "Hotel/Restaurant classification will fall back to keyword classifier."
        )
        return False
    return True


ML_MODELS_VERIFIED = _verify_ml_models()


def classify_review_text(
    text: str, business_type_name: str, business_type_uuid: str
) -> dict:
    classification_method = "keyword"
    main_label = "(none)"
    second_label = "(none)"
    third_label = "(none)"
    detected_lang = None
    translated_text = None

    if get_classification_approach(business_type_name) == "ml":
        classification_method = "ml"
        if not ML_MODELS_VERIFIED:
            logger.warning("ML models not verified, falling back to keyword classifier")
            classification_method = "ml_fallback"

        try:
            ml_result = ml_classify_review(
                text=text, business_type_uuid=business_type_uuid, verbose=False
            )
            if ml_result.get("main_label") is None:
                classification_result = classify_with_keywords(text, business_type_uuid)
                main_label = classification_result.get("main_label") or "(none)"
                second_label = classification_result.get("second_label") or "(none)"
                third_label = classification_result.get("third_label") or "(none)"
                classification_method = "ml_fallback"
            else:
                main_label = ml_result.get("main_label") or "(none)"
                second_label = ml_result.get("second_label") or "(none)"
                third_label = ml_result.get("third_label") or "(none)"
                detected_lang = ml_result.get("detected_language", "en")
                translated_text = ml_result.get("translated_text")
        except Exception as e:
            logger.error("ML classification failed: %s", str(e))
            try:
                classification_result = classify_with_keywords(text, business_type_uuid)
                main_label = classification_result.get("main_label") or "(none)"
                second_label = classification_result.get("second_label") or "(none)"
                third_label = classification_result.get("third_label") or "(none)"
                classification_method = "ml_fallback"
            except Exception:
                raise HTTPException(
                    status_code=500, detail="Review could not be classified"
                )
    else:
        classification_result = classify_with_keywords(text, business_type_uuid)
        main_label = classification_result.get("main_label") or "(none)"
        second_label = classification_result.get("second_label") or "(none)"
        third_label = classification_result.get("third_label") or "(none)"

    classification_labels = json.dumps([main_label, second_label, third_label])

    return {
        "main_label": main_label,
        "second_label": second_label,
        "third_label": third_label,
        "classification_labels": classification_labels,
        "detected_lang": detected_lang,
        "translated_text": translated_text,
        "classification_method": classification_method,
    }


def list_reviews(db: Session, listing_id: UUID) -> list[dict]:
    listing = db.exec(select(Listing).where(Listing.id == listing_id)).first()

    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.status != Statuses.active:
        raise HTTPException(status_code=400, detail="Listing is not active")

    results = db.exec(
        select(Review, User.username)
        .join(User, Review.user_id == User.id)
        .where(Review.listing_id == listing_id)
        .order_by(desc(Review.created_at))
    ).all()

    reviews = []
    for r, username in results:
        labels = json.loads(r.classification_labels or '["(none)", "(none)", "(none)"]')
        classification_method = "keyword"
        if r.translated_comment:
            classification_method = "ml"
        reviews.append(
            {
                "id": r.id,
                "listing_id": r.listing_id,
                "user_id": r.user_id,
                "user_name": username,
                "rating": r.rating,
                "comment": r.comment,
                "censored_comment": r.censored_comment,
                "detected_language": r.detected_language,
                "translated_comment": r.translated_comment,
                "main_label": labels[0] if len(labels) > 0 else "(none)",
                "second_label": labels[1] if len(labels) > 1 else "(none)",
                "third_label": labels[2] if len(labels) > 2 else "(none)",
                "classification_labels": r.classification_labels,
                "classification_method": classification_method,
                "created_at": r.created_at,
            }
        )
    return reviews


def submit_review(db: Session, user_id: UUID, review_request: "ReviewCreate") -> dict:
    listing = db.exec(
        select(Listing).where(Listing.id == review_request.listing_id)
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.status != Statuses.active:
        raise HTTPException(status_code=400, detail="Listing is not active")

    business_type = db.exec(
        select(BusinessType).where(BusinessType.id == listing.business_type)
    ).first()
    if not business_type:
        raise HTTPException(status_code=400, detail="Listing has no business type")

    business_type_name = business_type.name
    business_type_uuid = str(listing.business_type)

    text = review_request.comment or ""
    original_comment = text
    censored_comment = censor_text(text) if text else None

    if text and len(text) > 5000:
        raise HTTPException(
            status_code=400, detail="Comment exceeds maximum length of 5000 characters"
        )

    classification_result = classify_review_text(
        text, business_type_name, business_type_uuid
    )

    main_label = classification_result["main_label"]
    second_label = classification_result["second_label"]
    third_label = classification_result["third_label"]
    classification_labels = classification_result["classification_labels"]
    detected_lang = classification_result["detected_lang"]
    translated_text = classification_result["translated_text"]
    classification_method = classification_result["classification_method"]

    if main_label == "(none)" and second_label == "(none)" and third_label == "(none)":
        raise HTTPException(status_code=500, detail="Review could not be classified")

    review = Review(
        listing_id=review_request.listing_id,
        user_id=user_id,
        rating=review_request.rating,
        comment=original_comment,
        classification_labels=classification_labels,
        classified_at=datetime.utcnow(),
        detected_language=detected_lang,
        translated_comment=translated_text if translated_text else None,
        censored_comment=censored_comment,
    )

    try:
        db.add(review)
        db.commit()
        db.refresh(review)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="You already reviewed this listing")

    return {
        "id": review.id,
        "listing_id": review.listing_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "comment": review.comment,
        "detected_language": detected_lang,
        "translated_comment": review.translated_comment,
        "censored_comment": review.censored_comment,
        "classification_labels": classification_labels,
        "main_label": main_label,
        "second_label": second_label,
        "third_label": third_label,
        "classification_method": classification_method,
        "created_at": review.created_at,
        "detail": "Review submitted and classified",
    }


def update_review(db: Session, review: Review, review_request: "ReviewUpdate") -> dict:
    if review_request.rating is not None:
        review.rating = review_request.rating
    if review_request.comment is not None:
        review.comment = review_request.comment
        review.censored_comment = censor_text(review_request.comment)

    classification_method = None
    if review_request.comment is not None:
        listing = db.exec(
            select(Listing).where(Listing.id == review.listing_id)
        ).first()

        if listing:
            business_type = db.exec(
                select(BusinessType).where(BusinessType.id == listing.business_type)
            ).first()

            if business_type:
                classification_result = classify_review_text(
                    review_request.comment,
                    business_type.name,
                    str(listing.business_type),
                )
                review.classification_labels = classification_result[
                    "classification_labels"
                ]
                review.detected_language = classification_result["detected_lang"]
                review.translated_comment = classification_result["translated_text"]
                review.classified_at = datetime.utcnow()
                classification_method = classification_result["classification_method"]

    review.updated_at = datetime.utcnow()
    db.add(review)
    db.commit()
    db.refresh(review)

    response = {
        "id": review.id,
        "listing_id": review.listing_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "comment": review.comment,
        "detected_language": review.detected_language,
        "translated_comment": review.translated_comment,
        "censored_comment": review.censored_comment,
        "classification_labels": review.classification_labels,
        "created_at": review.created_at,
        "detail": "Review updated",
    }

    if classification_method:
        response["classification_method"] = classification_method

    labels = json.loads(
        review.classification_labels or '["(none)", "(none)", "(none)"]'
    )
    response["main_label"] = labels[0] if len(labels) > 0 else "(none)"
    response["second_label"] = labels[1] if len(labels) > 1 else "(none)"
    response["third_label"] = labels[2] if len(labels) > 2 else "(none)"

    return response


def delete_review(db: Session, review: Review) -> None:
    db.delete(review)
    db.commit()


def get_review_by_id(db: Session, review_id: UUID) -> Review | None:
    return db.exec(select(Review).where(Review.id == review_id)).first()
