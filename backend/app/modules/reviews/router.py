from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlmodel import Session, select

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_roles

from .models import Review, BusinessReply
from .schemas import (
    ReviewCreate,
    ReviewResponse,
    ReviewSubmitResponse,
    ReviewUpdate,
    BusinessReplyCreate,
    BusinessReplyUpdate,
    BusinessReplyResponse,
)
from .service import (
    submit_review,
    delete_review,
    list_reviews,
    update_review,
    create_business_reply,
    get_business_reply,
    update_business_reply,
    delete_business_reply,
)

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get(
    "/{listing_id}/",
    response_model=list[ReviewResponse],
    responses={
        200: {
            "description": "Reviews for Sunset Eats (listing_id: ff62dcdf-5ce0-42af-a5fd-4785b586636c)"
        },
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
            "description": "Review submitted and classified",
            "content": {
                "application/json": {
                    "example": {
                        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "listing_id": "ff62dcdf-5ce0-42af-a5fd-4785b586636c",
                        "user_id": "f9826077-3237-406b-9857-847564313890",
                        "rating": 4,
                        "comment": "Great food and atmosphere!",
                        "detected_language": "en",
                        "classification_labels": '["food_quality", "service_quality", "ambiance"]',
                        "main_label": "food_quality",
                        "second_label": "service_quality",
                        "third_label": "ambiance",
                        "classification_method": "ml",
                        "created_at": "2026-05-19T10:30:00Z",
                        "detail": "Review submitted and classified",
                    }
                }
            },
        },
        400: {"description": "Listing is not active"},
        401: {"description": "Not authorized"},
        404: {"description": "Listing not found"},
        409: {"description": "You already reviewed this listing"},
        500: {"description": "Review could not be classified"},
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
    return submit_review(
        db=db,
        user_id=current_user.id,
        review_request=review_create,
    )


@router.put(
    "/{review_id}",
    response_model=ReviewSubmitResponse,
    responses={
        200: {
            "description": "Review updated with re-classification",
            "content": {
                "application/json": {
                    "example": {
                        "id": "d3b16653-8629-4af0-b621-7b17e8373195",
                        "listing_id": "ff62dcdf-5ce0-42af-a5fd-4785b586636c",
                        "user_id": "f9826077-3237-406b-9857-847564313890",
                        "rating": 4,
                        "comment": "Good atmosphere but bad service",
                        "detected_language": "en",
                        "classification_labels": '["ambiance", "service_quality", "(none)"]',
                        "main_label": "ambiance",
                        "second_label": "service_quality",
                        "third_label": "(none)",
                        "classification_method": "keyword",
                        "created_at": "2026-05-21T01:25:06.342237Z",
                        "detail": "Review updated",
                    }
                }
            },
        },
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
    """Update an existing review (owner only). Re-classifies if comment changes."""
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

    review_update = ReviewUpdate(rating=rating, comment=comment)
    return update_review(db, review, review_update)


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


@router.post(
    "/{review_id}/reply",
    response_model=BusinessReplyResponse,
    status_code=201,
    responses={
        201: {"description": "Business reply created"},
        401: {"description": "Not authorized"},
        403: {"description": "Not authorized to reply to this review"},
        404: {"description": "Review not found"},
        409: {"description": "Reply already exists for this review"},
    },
)
def create_reply_route(
    review_id: UUID,
    description: str = Form(..., max_length=2000),
    current_user: User = Depends(require_roles("business", "employee")),
    db: Session = Depends(get_db),
):
    """Create a business reply to a review (business/employee only)."""
    from app.modules.businesses.models import Business

    business = db.exec(
        select(Business).where(Business.user_id == current_user.id)
    ).first()
    if not business:
        raise HTTPException(
            status_code=403, detail="No business associated with this user"
        )

    reply = create_business_reply(
        db=db,
        review_id=review_id,
        business_id=business.id,
        user_id=current_user.id,
        description=description,
    )
    reply["user_name"] = current_user.username
    return reply


@router.get(
    "/{review_id}/reply",
    response_model=BusinessReplyResponse | None,
    responses={
        200: {"description": "Get business reply for a review"},
        404: {"description": "Reply not found"},
    },
)
def get_reply_route(
    review_id: UUID,
    db: Session = Depends(get_db),
):
    """Get business reply for a review."""
    return get_business_reply(db, review_id)


@router.put(
    "/{review_id}/reply",
    response_model=BusinessReplyResponse,
    responses={
        200: {"description": "Business reply updated"},
        401: {"description": "Not authorized"},
        403: {"description": "Not authorized to update this reply"},
        404: {"description": "Reply not found"},
    },
)
def update_reply_route(
    review_id: UUID,
    description: str = Form(..., max_length=2000),
    current_user: User = Depends(require_roles("business", "employee")),
    db: Session = Depends(get_db),
):
    """Update a business reply (owner or admin only)."""
    reply = update_business_reply(
        db=db,
        review_id=review_id,
        user_id=current_user.id,
        description=description,
    )
    return reply


@router.delete(
    "/{review_id}/reply",
    status_code=204,
    responses={
        204: {"description": "Business reply deleted"},
        401: {"description": "Not authorized"},
        403: {"description": "Not authorized to delete this reply"},
        404: {"description": "Reply not found"},
    },
)
def delete_reply_route(
    review_id: UUID,
    current_user: User = Depends(require_roles("business", "employee")),
    db: Session = Depends(get_db),
):
    """Delete a business reply (owner or admin only)."""
    delete_business_reply(
        db=db,
        review_id=review_id,
        user_id=current_user.id,
    )
    return {"detail": "Reply deleted"}
