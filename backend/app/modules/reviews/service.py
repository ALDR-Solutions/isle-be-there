from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, desc, select

from app.modules.listings.models import Listing

from .models import Review
from .schemas import ReviewCreate, ReviewUpdate

import json
from .keyword_classifier import BUSINESS_TYPE_UUIDS, check_flags, classify_with_keywords
from .review_classifier import classify_review as ml_classify_review


def serialize_review(review: Review, include_classification: bool = False) -> dict:
    data = review.model_dump()
    data["comment"] = review.comment
    if include_classification and review.classification_labels:
        try:
            data["classification_labels"] = json.loads(review.classification_labels)
        except:
            data["classification_labels"] = review.classification_labels
    return data


def list_reviews(db: Session, listing_id=None):
    query = select(Review).where(Review.is_visible == True)
    if listing_id:
        query = query.where(Review.listing_id == listing_id)

    reviews = db.exec(query.order_by(desc(Review.created_at))).all()
    return [
        {
            "id": r.id,
            "listing_id": r.listing_id,
            "user_id": r.user_id,
            "rating": r.rating,
            "comment": r.comment,
            "is_visible": r.is_visible,
            "classification_labels": r.classification_labels,
            "created_at": r.created_at,
        }
        for r in reviews
    ]


def get_review(db: Session, review_id: int) -> dict:
    review = db.exec(select(Review).where(Review.id == review_id).where(Review.is_visible == True)).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return serialize_review(review)


def create_review(db: Session, user_id, review_request: ReviewCreate) -> dict:
    listing = db.exec(select(Listing.id).where(Listing.id == review_request.listing_id)).first()
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
    db.add(review)
    db.commit()
    db.refresh(review)
    return serialize_review(review)


def submit_review(db: Session, user_id, review_request, business_type_uuid: str, hotel_name: str = None) -> dict:
    """
    Submit a review with automatic classification.
    
    1. Validates listing exists
    2. Checks user hasn't already reviewed
    3. Classifies the review text (keyword or ML)
    4. Saves review with classification fields
    5. Returns review with classification data
    """
    # Validate listing
    listing = db.exec(select(Listing.id).where(Listing.id == review_request.listing_id)).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Check existing review
    existing = db.exec(
        select(Review)
        .where(Review.listing_id == review_request.listing_id)
        .where(Review.user_id == user_id)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You already reviewed this listing")

    # Classify the review text
    text = review_request.comment or ""
    
    # Check flags (applies to ALL business types)
    flag_result = check_flags(text)
    is_flagged = flag_result["is_flagged"]
    flag_reason = flag_result["reason"]
    
    # Route to appropriate classifier
    events_uuid = BUSINESS_TYPE_UUIDS["events"]
    tours_uuid = BUSINESS_TYPE_UUIDS["tours"]
    services_uuid = BUSINESS_TYPE_UUIDS["services"]
    
    if business_type_uuid in [events_uuid, tours_uuid, services_uuid]:
        # Keyword-based classification
        classification_result = classify_with_keywords(text, business_type_uuid)
        main_label = classification_result.get("main_label", "")
        second_label = classification_result.get("second_label", "")
        third_label = classification_result.get("third_label", "")
        business_type = classification_result.get("business_type", "")
        classification_labels = json.dumps([main_label, second_label, third_label])
    else:
        # ML classification for Hotel/Restaurant
        try:
            ml_result = ml_classify_review(
                text=text,
                business_type_uuid=business_type_uuid,
                hotel_name=hotel_name,
                verbose=False
            )
            main_label = ml_result.get('main_label') or ""
            second_label = ml_result.get('second_label') or ""
            third_label = ml_result.get('third_label') or ""
            business_type = ml_result.get('business_type', 'Hotel')
            classification_labels = json.dumps([main_label, second_label, third_label])
        except Exception:
            main_label = second_label = third_label = ""
            business_type = "Hotel" if business_type_uuid == BUSINESS_TYPE_UUIDS.get("hotel") else "Restaurant"
            classification_labels = json.dumps([])

    # Create review with classification
    review = Review(
        listing_id=review_request.listing_id,
        user_id=user_id,
        rating=review_request.rating,
        comment=review_request.comment,
        classification_labels=classification_labels,
        is_flagged=is_flagged,
        is_visible=True,
        flag_reason=flag_reason,
        classified_at=datetime.utcnow(),
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    # Return with classification data
    result = serialize_review(review)
    result["business_type"] = business_type
    result["hotel_name"] = hotel_name
    result["main_label"] = main_label
    result["second_label"] = second_label
    result["third_label"] = third_label
    result["detail"] = "Review submitted and classified"
    
    return result


def update_review(db: Session, review: Review, review_request: ReviewUpdate) -> dict:
    update_data = review_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review, key, value)

    review.updated_at = datetime.utcnow()
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"detail": "Review updated"}


def delete_review(db: Session, review: Review) -> None:
    db.delete(review)
    db.commit()


def toggle_review_visibility(db: Session, review: Review, is_visible: bool) -> dict:
    """
    Toggle review visibility (admin only).
    
    Args:
        db: Database session
        review: Review object to update
        is_visible: New visibility value
        
    Returns:
        Updated review dict
    """
    review.is_visible = is_visible
    review.updated_at = datetime.utcnow()
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"detail": "Review visibility updated"}
