from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, desc, select

from app.modules.listings.models import Listing
from app.modules.businesses.models import Business, BusinessType, BusinessEmployees

from .models import Review, BusinessReply
from .schemas import ReviewCreate, ReviewUpdate

import json
from .classifiers.keyword_classifier import (
    BUSINESS_TYPE_UUIDS,
    classify_with_keywords,
    get_classification_approach,
)
from .classifiers.ml_classifier import classify_review as ml_classify_review
from .profanity import censor_text


def serialize_review(review: Review, include_classification: bool = False) -> dict:
    data = review.model_dump()
    data["comment"] = review.comment
    data["classification_labels"] = review.classification_labels
    data["censored_comment"] = review.censored_comment
    data["detected_language"] = review.detected_language
    if include_classification and review.classification_labels:
        try:
            data["classification_labels"] = json.loads(review.classification_labels)
        except:
            pass
    return data


def list_reviews(db: Session, listing_id=None):
    query = select(Review)
    if listing_id:
        query = query.where(Review.listing_id == listing_id)

    reviews = db.exec(query.order_by(desc(Review.created_at))).all()
    return [
        {
            "id": str(r.id),
            "listing_id": str(r.listing_id),
            "user_id": str(r.user_id),
            "rating": r.rating,
            "comment": r.comment,
            "censored_comment": r.censored_comment,
            "detected_language": r.detected_language,
            "classification_labels": r.classification_labels,
            "created_at": r.created_at,
        }
        for r in reviews
    ]


def get_review(db: Session, review_id: UUID) -> dict:
    review = db.exec(select(Review).where(Review.id == review_id)).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return serialize_review(review)


def create_review(db: Session, user_id, review_request: ReviewCreate) -> dict:
    listing = db.exec(
        select(Listing.id).where(Listing.id == review_request.listing_id)
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    existing = db.exec(
        select(Review)
        .where(Review.listing_id == review_request.listing_id)
        .where(Review.user_id == user_id)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You already reviewed this listing")

    review = Review(
        listing_id=review_request.listing_id,
        user_id=user_id,
        rating=review_request.rating,
        comment=review_request.comment,
    )
    try:
        db.add(review)
        db.commit()
        db.refresh(review)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="You already reviewed this listing")

    return serialize_review(review)


def classify_review_text(text: str, business_type_uuid: str) -> dict:
    result = classify_with_keywords(text, business_type_uuid)
    return {
        "main_label": result.get("main_label", ""),
        "second_label": result.get("second_label", ""),
        "third_label": result.get("third_label", ""),
        "business_type": result.get("business_type", ""),
        "classification_labels": json.dumps(
            [
                result.get("main_label", ""),
                result.get("second_label", ""),
                result.get("third_label", ""),
            ]
        ),
        "detected_lang": None,
        "translated_text": None,
    }


def submit_review(db: Session, user_id, review_request) -> dict:
    listing = db.exec(
        select(Listing).where(Listing.id == review_request.listing_id)
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    existing = db.exec(
        select(Review)
        .where(Review.listing_id == review_request.listing_id)
        .where(Review.user_id == user_id)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You already reviewed this listing")

    business_type = db.exec(
        select(BusinessType).where(BusinessType.id == listing.business_type)
    ).first()
    if not business_type:
        raise HTTPException(status_code=400, detail="Listing has no business type")

    business_type_name = business_type.name
    business_type_uuid = str(listing.business_type)

    text = review_request.comment or ""
    original_comment = text

    if text and len(text) > 5000:
        raise HTTPException(
            status_code=400, detail="Comment exceeds maximum length of 5000 characters"
        )

    censored_comment = censor_text(text) if text else None

    if get_classification_approach(business_type_name) == "ml":
        try:
            ml_result = ml_classify_review(
                text=text, business_type_uuid=business_type_uuid, verbose=False
            )
            if ml_result.get("main_label") is None:
                classification_result = classify_with_keywords(text, business_type_uuid)
                main_label = classification_result.get("main_label") or "(none)"
                second_label = classification_result.get("second_label") or "(none)"
                third_label = classification_result.get("third_label") or "(none)"
                classification_labels = json.dumps(
                    [main_label, second_label, third_label]
                )
                detected_lang = None
                translated_text = None
            else:
                main_label = ml_result.get("main_label") or "(none)"
                second_label = ml_result.get("second_label") or "(none)"
                third_label = ml_result.get("third_label") or "(none)"
                classification_labels = json.dumps(
                    [main_label, second_label, third_label]
                )
                detected_lang = ml_result.get("detected_language", "en")
                translated_text = ml_result.get("translated_text")
        except Exception:
            classification_result = classify_with_keywords(text, business_type_uuid)
            main_label = classification_result.get("main_label") or "(none)"
            second_label = classification_result.get("second_label") or "(none)"
            third_label = classification_result.get("third_label") or "(none)"
            classification_labels = json.dumps([main_label, second_label, third_label])
            detected_lang = None
            translated_text = None
    else:
        classification_result = classify_with_keywords(text, business_type_uuid)
        main_label = classification_result.get("main_label") or "(none)"
        second_label = classification_result.get("second_label") or "(none)"
        third_label = classification_result.get("third_label") or "(none)"
        classification_labels = json.dumps([main_label, second_label, third_label])
        detected_lang = None
        translated_text = None

    review = Review(
        listing_id=review_request.listing_id,
        user_id=user_id,
        rating=review_request.rating,
        comment=original_comment,
        classification_labels=classification_labels,
        censored_comment=censored_comment,
        classified_at=datetime.utcnow(),
        detected_language=detected_lang,
        translated_comment=translated_text if translated_text else None,
    )

    try:
        db.add(review)
        db.commit()
        db.refresh(review)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="You already reviewed this listing")

    result = serialize_review(review)
    result["detail"] = "Review submitted and classified"

    return result


def update_review(db: Session, review: Review, review_request: ReviewUpdate) -> dict:
    update_data = review_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review, key, value)

    if review.comment:
        review.censored_comment = censor_text(review.comment)

    review.updated_at = datetime.utcnow()
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"detail": "Review updated"}


def delete_review(db: Session, review: Review) -> None:
    db.delete(review)
    db.commit()


def can_user_reply_to_review(db: Session, user_id: str, review_id: UUID) -> bool:
    review_obj = db.exec(select(Review).where(Review.id == review_id)).first()
    if not review_obj:
        return False

    listing = db.exec(
        select(Listing).where(Listing.id == review_obj.listing_id)
    ).first()
    if not listing or not listing.business_id:
        return False

    business = db.exec(
        select(Business).where(Business.id == listing.business_id)
    ).first()
    if not business:
        return False

    if str(business.user_id) == str(user_id):
        return True

    employee = db.exec(
        select(BusinessEmployees)
        .where(BusinessEmployees.employee_id == user_id)
        .where(BusinessEmployees.business_id == listing.business_id)
    ).first()
    return employee is not None


def get_reply(db: Session, review_id: UUID) -> dict | None:
    reply = db.exec(
        select(BusinessReply).where(BusinessReply.review_id == review_id)
    ).first()
    if not reply:
        return None
    return {
        "id": reply.id,
        "review_id": str(reply.review_id),
        "business_id": str(reply.business_id) if reply.business_id else None,
        "description": reply.description,
        "created_at": reply.created_at,
    }


def create_reply(
    db: Session, review_id: UUID, business_id: str, user_id: str, description: str
) -> dict:
    review_obj = db.exec(select(Review).where(Review.id == review_id)).first()
    if not review_obj:
        raise HTTPException(status_code=404, detail="Review not found")

    existing = db.exec(
        select(BusinessReply).where(BusinessReply.review_id == review_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=409, detail="Reply already exists for this review"
        )

    reply = BusinessReply(
        review_id=review_id,
        business_id=business_id,
        description=description,
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)

    return {
        "id": reply.id,
        "review_id": str(reply.review_id),
        "business_id": str(reply.business_id) if reply.business_id else None,
        "description": reply.description,
        "created_at": reply.created_at,
    }


def update_reply(db: Session, reply: BusinessReply, description: str) -> dict:
    reply.description = description
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return {
        "id": reply.id,
        "review_id": str(reply.review_id),
        "business_id": str(reply.business_id) if reply.business_id else None,
        "description": reply.description,
        "created_at": reply.created_at,
    }


def delete_reply(db: Session, reply: BusinessReply) -> None:
    db.delete(reply)
    db.commit()
