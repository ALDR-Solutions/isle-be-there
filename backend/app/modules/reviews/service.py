import json
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from .models import Review
from .schemas import ReviewCreate


def get_reviews_for_listing(db: Session, listing_id: UUID) -> list[Review]:
    """Get all reviews for a listing."""
    reviews = db.exec(select(Review).where(Review.listing_id == listing_id)).all()
    return reviews


def create_review(db: Session, user_id: UUID, review_request: ReviewCreate) -> dict:
    """Create a new review."""
    # Check if user already reviewed this listing
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
        classification_labels=json.dumps(["(none)", "(none)", "(none)"]),
    )

    try:
        db.add(review)
        db.commit()
        db.refresh(review)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="You already reviewed this listing")

    # Parse classification labels for response
    labels = json.loads(
        review.classification_labels or '["(none)", "(none)", "(none)"]'
    )

    return {
        "id": review.id,
        "listing_id": review.listing_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "comment": review.comment,
        "classification_labels": review.classification_labels,
        "main_label": labels[0] if len(labels) > 0 else "(none)",
        "second_label": labels[1] if len(labels) > 1 else "(none)",
        "third_label": labels[2] if len(labels) > 2 else "(none)",
        "created_at": review.created_at,
        "detail": "Review submitted successfully",
    }


def delete_review(db: Session, review: Review) -> None:
    """Delete a review."""
    db.delete(review)
    db.commit()
