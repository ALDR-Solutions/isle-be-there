from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, desc, select

from app.modules.listings.models import Listing

from .models import Review
from .schemas import ReviewCreate, ReviewUpdate


def serialize_review(review: Review) -> dict:
    data = review.model_dump()
    data["comment"] = review.comment
    return data


def list_reviews(db: Session, listing_id=None):
    query = select(Review)
    if listing_id:
        query = query.where(Review.listing_id == listing_id)

    reviews = db.exec(query.order_by(desc(Review.created_at))).all()
    return [serialize_review(review) for review in reviews]


def get_review(db: Session, review_id: int) -> dict:
    review = db.exec(select(Review).where(Review.id == review_id)).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return serialize_review(review)


def create_review(db: Session, user_id, payload: ReviewCreate) -> dict:
    listing = db.exec(select(Listing.id).where(Listing.id == payload.listing_id)).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    existing = db.exec(
        select(Review)
        .where(Review.listing_id == payload.listing_id)
        .where(Review.user_id == user_id)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You already reviewed this listing")

    review = Review(
        listing_id=payload.listing_id,
        user_id=user_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return serialize_review(review)


def update_review(db: Session, review: Review, payload: ReviewUpdate) -> dict:
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review, key, value)

    review.updated_at = datetime.utcnow()
    db.add(review)
    db.commit()
    db.refresh(review)
    return serialize_review(review)


def delete_review(db: Session, review: Review) -> None:
    db.delete(review)
    db.commit()
