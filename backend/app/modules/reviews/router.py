from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlmodel import Session, select

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_roles

from .models import Review
from .schemas import ReviewCreate, ReviewResponse, ReviewSubmitResponse
from .service import create_review, delete_review, list_reviews

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get(
    "/{listing_id}/",
    response_model=list[ReviewResponse],
    responses={
        200: {
            "description": "Reviews for Sunset Eats (listing_id: ff62dcdf-5ce0-42af-a5fd-4785b586636c, rating: 1-5)"},
        400: {"description": "Listing is not active"},
        404: {"description": "Listing not found"},
    },
)
def get_reviews_for_listing_route(
    listing_id: UUID,
    db: Session = Depends(get_db),
):
    """Get all reviews for a specific listing."""
    reviews = list_reviews(db, listing_id)
    return reviews


@router.post(
    "/submit",
    response_model=ReviewSubmitResponse,
    status_code=201,
    responses={
        201: {
            "description": "Review submitted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "listing_id": "ff62dcdf-5ce0-42af-a5fd-4785b586636c",
                        "user_id": "f9826077-3237-406b-9857-847564313890",
                        "rating": 4,
                        "comment": "Great food and atmosphere!",
                        "classification_labels": None,
                        "created_at": "2026-05-19T10:30:00Z",
                        "detail": "Review submitted successfully",
                    }
                }
            },
        },
        400: {"description": "Listing is not active"},
        401: {"description": "Not authorized"},
        404: {"description": "Listing not found"},
        409: {"description": "You already reviewed this listing"},
    },
)
def submit_review_route(
    listing_id: UUID = Form(...),
    rating: int = Form(..., ge=1, le=5),
    comment: str | None = Form(default=None),
    current_user: User = Depends(require_roles("regular", "admin")),
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


@router.put(
    "/{review_id}",
    response_model=dict,
    responses={
        200: {"description": "Review updated"},
        401: {"description": "Not authorized to update this review"},
        404: {"description": "Review not found"},
        422: {"description": "Validation error"},
    },
)
def update_review_route(
    review_id: UUID,
    rating: int | None = Form(default=None, ge=1, le=5),
    comment: str | None = Form(default=None),
    current_user: User = Depends(require_roles("regular", "admin")),
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

    return {"detail": "Review updated"}


@router.delete(
    "/{review_id}",
    status_code=204,
    responses={
        204: {"description": "Review deleted"},
        401: {"description": "Not authorized to delete this review"},
        404: {"description": "Review not found"},
    },
)
def delete_review_route(
    review_id: UUID,
    current_user: User = Depends(require_roles("regular", "admin")),
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

    return {"detail": "Review deleted"}
