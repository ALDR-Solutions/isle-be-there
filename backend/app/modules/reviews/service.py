from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, desc, select

from app.modules.listings.models import Listing, Statuses
from app.modules.businesses.models import BusinessType
from app.modules.users.models import User

from .classification import classify_review_text
from .profanity import censor_text
from app.shared.sanitization import sanitize_html

from .models import Review, BusinessReply
from .schemas import ReviewCreate, ReviewUpdate

import json


def list_reviews(db: Session, listing_id: UUID) -> list[dict]:
    from app.modules.users.models import User

    listing_status = db.exec(
        select(Listing.status).where(Listing.id == listing_id)
    ).first()

    if listing_status is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing_status != Statuses.active:
        raise HTTPException(status_code=400, detail="Listing is not active")

    reviews_list = db.exec(
        select(Review)
        .where(Review.listing_id == listing_id)
        .order_by(desc(Review.created_at))
    ).all()

    reviews = []
    for r in reviews_list:
        user = db.exec(select(User).where(User.id == r.user_id)).first()
        username = user.username if user else None

        reply = get_business_reply(db, r.id)

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
                "business_reply": reply,
            }
        )
    return reviews


def submit_review(db: Session, user_id: UUID, review_request: ReviewCreate) -> dict:
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

    text = sanitize_html(review_request.comment) or ""
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


def update_review(db: Session, review: Review, review_request: ReviewUpdate) -> dict:
    if review_request.rating is not None:
        review.rating = review_request.rating
    if review_request.comment is not None:
        review.comment = sanitize_html(review_request.comment)
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


def create_business_reply(
    db: Session, review_id: UUID, business_id: UUID, user_id: UUID, description: str
) -> dict:
    review = db.exec(select(Review).where(Review.id == review_id)).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    from app.modules.listings.models import Listing

    listing = db.exec(select(Listing).where(Listing.id == review.listing_id)).first()
    if not listing or str(listing.business_id) != str(business_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to reply to this review"
        )

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
        user_id=user_id,
        description=sanitize_html(description),
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)

    return {
        "id": reply.id,
        "review_id": reply.review_id,
        "business_id": reply.business_id,
        "user_id": reply.user_id,
        "description": reply.description,
        "created_at": reply.created_at,
        "updated_at": reply.updated_at,
    }


def get_business_reply(db: Session, review_id: UUID) -> dict | None:
    result = db.exec(
        select(BusinessReply, User.username)
        .join(User, BusinessReply.user_id == User.id)
        .where(BusinessReply.review_id == review_id)
    ).first()

    if not result:
        return None

    reply, username = result
    return {
        "id": reply.id,
        "review_id": reply.review_id,
        "business_id": reply.business_id,
        "user_id": reply.user_id,
        "user_name": username,
        "description": reply.description,
        "created_at": reply.created_at,
        "updated_at": reply.updated_at,
    }


def update_business_reply(
    db: Session,
    review_id: UUID,
    user_id: UUID,
    description: str,
    is_admin: bool = False,
) -> dict:
    reply = db.exec(
        select(BusinessReply).where(BusinessReply.review_id == review_id)
    ).first()

    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    if not is_admin and str(reply.user_id) != str(user_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to update this reply"
        )

    reply.description = sanitize_html(description)
    reply.updated_at = datetime.utcnow()
    db.add(reply)
    db.commit()
    db.refresh(reply)

    return {
        "id": reply.id,
        "review_id": reply.review_id,
        "business_id": reply.business_id,
        "user_id": reply.user_id,
        "description": reply.description,
        "created_at": reply.created_at,
        "updated_at": reply.updated_at,
    }


def delete_business_reply(
    db: Session, review_id: UUID, user_id: UUID, is_admin: bool = False
) -> None:
    reply = db.exec(
        select(BusinessReply).where(BusinessReply.review_id == review_id)
    ).first()

    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    if not is_admin and str(reply.user_id) != str(user_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this reply"
        )

    db.delete(reply)
    db.commit()


def delete_review(db: Session, review: Review) -> None:
    db.delete(review)
    db.commit()
