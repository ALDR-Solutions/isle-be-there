from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, desc, select

from app.api.dependencies.permissions import require_review_owner, require_roles
from app.database.session import get_db
from app.models.listing import Listing
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


def _serialize_review(review: Review) -> dict:
    data = review.model_dump()
    data["comment"] = review.comment
    return data


@router.get("", response_model=list[dict])
def get_reviews(
    listing_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(Review)
    if listing_id:
        query = query.where(Review.listing_id == listing_id)

    reviews = db.exec(query.order_by(desc(Review.created_at))).all()
    return [_serialize_review(review) for review in reviews]


@router.get("/{review_id}", response_model=dict)
def get_review(review_id: UUID, db: Session = Depends(get_db)):
    review = db.exec(select(Review).where(Review.id == review_id)).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return _serialize_review(review)


@router.post("", response_model=dict, status_code=201)
def create_review(
    payload: ReviewCreate,
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    listing = db.exec(select(Listing.id).where(Listing.id == payload.listing_id)).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    existing = db.exec(
        select(Review)
        .where(Review.listing_id == payload.listing_id)
        .where(Review.user_id == current_user.id)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You already reviewed this listing")

    review = Review(
        listing_id=payload.listing_id,
        user_id=current_user.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return _serialize_review(review)


@router.put("/{review_id}", response_model=dict)
def update_review(
    review_id: UUID,
    payload: ReviewUpdate,
    review: Review = Depends(require_review_owner),
    db: Session = Depends(get_db),
):
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review, key, value)

    review.updated_at = datetime.utcnow()
    db.add(review)
    db.commit()
    db.refresh(review)
    return _serialize_review(review)


@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id: UUID,
    review: Review = Depends(require_review_owner),
    db: Session = Depends(get_db),
):
    db.delete(review)
    db.commit()
    return None
