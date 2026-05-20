from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, desc, select

from app.modules.listings.models import Listing, Statuses
from .models import Review
from .schemas import ReviewCreate, ReviewUpdate


def list_reviews(db: Session, listing_id: UUID) -> list[dict]:
    listing_status = db.exec(
        select(Listing.status).where(Listing.id == listing_id)
    ).first()

    if listing_status is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing_status != Statuses.active:
        raise HTTPException(status_code=400, detail="Listing is not active")

    reviews = db.exec(
        select(Review)
        .where(Review.listing_id == listing_id)
        .order_by(desc(Review.created_at))
    ).all()

    return [
        {
            "id": r.id,
            "listing_id": r.listing_id,
            "user_id": r.user_id,
            "rating": r.rating,
            "comment": r.comment,
            "classification_labels": r.classification_labels,
            "created_at": r.created_at,
        }
        for r in reviews
    ]


def create_review(db: Session, user_id: UUID, review_request: ReviewCreate) -> dict:
    listing_status = db.exec(
        select(Listing.status).where(Listing.id == review_request.listing_id)
    ).first()

    if listing_status is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing_status != Statuses.active:
        raise HTTPException(status_code=400, detail="Listing is not active")

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

    return {
        "id": review.id,
        "listing_id": review.listing_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "comment": review.comment,
        "classification_labels": review.classification_labels,
        "created_at": review.created_at,
        "detail": "Review submitted successfully",
    }


def delete_review(db: Session, review: Review) -> None:
    db.delete(review)
    db.commit()
