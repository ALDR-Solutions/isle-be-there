from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, desc, select
from typing import Optional, Dict, Any

from app.api.dependencies.permissions import require_review_owner, require_roles
from app.database.session import get_db
from app.models.listing import Listing
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.services.review_service import (
    validate_can_review, 
    create_review_with_classification,
    get_reviews_for_listing as svc_get_reviews
)

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


def _serialize_review(review: Review) -> dict:
    data = review.model_dump()
    data["comment"] = review.comment
    if review.auto_labels:
        data["auto_labels"] = review.auto_labels
    if review.detected_language:
        data["detected_language"] = review.detected_language
    return data


@router.get("", response_model=list[dict])
def get_reviews(
    listing_id: UUID | None = Query(default=None),
    filter_label: str | None = Query(default=None, description="Filter by label (e.g., 'service', 'clean')"),
    db: Session = Depends(get_db),
):
    if listing_id:
        reviews = svc_get_reviews(db, listing_id, filter_label)
    else:
        query = select(Review).order_by(desc(Review.created_at))
        if filter_label:
            query = query.where(Review.auto_labels != None)
        reviews = db.exec(query).all()
    
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
    # Validate listing exists
    listing = db.exec(select(Listing).where(Listing.id == payload.listing_id)).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Validate user can review (completed booking + not already reviewed)
    can_review, message = validate_can_review(db, current_user.id, payload.listing_id)
    if not can_review:
        raise HTTPException(status_code=403, detail=message)
    
    # Create review with ML classification
    review = create_review_with_classification(
        db=db,
        user_id=current_user.id,
        listing_id=payload.listing_id,
        rating=payload.rating,
        comment=payload.comment,
        listing=listing
    )
    
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
