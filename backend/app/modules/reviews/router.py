from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlmodel import Session, select

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_roles

from .models import Review
from .schemas import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewSubmitResponse,
)
from .service import create_review, delete_review, get_reviews_for_listing

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get("/{listing_id}", response_model=list[ReviewResponse])
def get_reviews_for_listing_route(
    listing_id: UUID,
    db: Session = Depends(get_db),
):
    """Get all reviews for a specific listing."""
    reviews = get_reviews_for_listing(db, listing_id)
    return reviews


@router.post("/submit", response_model=ReviewSubmitResponse, status_code=201)
def submit_review_route(
    listing_id: UUID = Form(...),
    rating: int = Form(..., ge=1, le=5),
    comment: str | None = Form(default=None),
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    """Submit a new review for a listing."""
    review_create = ReviewCreate(
        listing_id=listing_id,
        rating=rating,
        comment=comment,
    )
    return create_review(
        db=db,
        user_id=current_user.id,
        review_request=review_create,
    )


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review_route(
    review_id: UUID,
    rating: int | None = Form(default=None, ge=1, le=5),
    comment: str | None = Form(default=None),
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    """Update an existing review (owner only)."""
    review = db.exec(select(Review).where(Review.id == review_id)).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if (
        str(review.user_id) != str(current_user.id)
        and current_user.user_type != "admin"
    ):
        raise HTTPException(
            status_code=401, detail="Not authorized to update this review"
        )

    if rating is not None:
        review.rating = rating
    if comment is not None:
        review.comment = comment

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.delete("/{review_id}", status_code=204)
def delete_review_route(
    review_id: UUID,
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    """Delete a review (owner or admin only)."""
    review = db.exec(select(Review).where(Review.id == review_id)).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if (
        str(review.user_id) != str(current_user.id)
        and current_user.user_type != "admin"
    ):
        raise HTTPException(
            status_code=401, detail="Not authorized to delete this review"
        )

    db.delete(review)
    db.commit()
    return None
