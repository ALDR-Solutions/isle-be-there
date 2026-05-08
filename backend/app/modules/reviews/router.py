from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query
from sqlmodel import Session, select

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_review_owner, require_roles

from .models import Review, BusinessReply
from .schemas import (
    ReviewCreate,
    ReviewUpdate,
    ReviewSubmitResponse,
    BusinessReplyResponse,
)
from .service import (
    delete_review,
    get_review,
    list_reviews,
    submit_review,
    update_review,
    get_reply,
    create_reply,
    update_reply,
    delete_reply,
    can_user_reply_to_review,
)

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get("", response_model=list[dict])
def get_reviews(
    listing_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_reviews(db, listing_id)


@router.post("/submit", response_model=ReviewSubmitResponse, status_code=201)
def submit_review_route(
    listing_id: UUID = Form(...),
    rating: int = Form(..., ge=1, le=5),
    comment: str | None = Form(default=None),
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    review_create_payload = ReviewCreate(
        listing_id=listing_id,
        rating=rating,
        comment=comment,
    )

    return submit_review(
        db=db,
        user_id=current_user.id,
        review_request=review_create_payload,
    )


@router.put("/{review_id}", response_model=dict)
def update_review_route(
    review_id: UUID,
    rating: int | None = Form(default=None, ge=1, le=5),
    comment: str | None = Form(default=None),
    review: Review = Depends(require_review_owner),
    db: Session = Depends(get_db),
):
    review_update_payload = ReviewUpdate(rating=rating, comment=comment)
    return update_review(db, review, review_update_payload)


@router.delete("/{review_id}", status_code=204)
def delete_review_route(
    review_id: UUID,
    review: Review = Depends(require_review_owner),
    db: Session = Depends(get_db),
):
    delete_review(db, review)
    return None


@router.get("/{review_id}/reply", response_model=BusinessReplyResponse | None)
def get_review_reply(
    review_id: UUID,
    db: Session = Depends(get_db),
):
    return get_reply(db, review_id)


@router.post(
    "/{review_id}/reply", response_model=BusinessReplyResponse, status_code=201
)
def create_review_reply(
    review_id: UUID,
    description: str = Form(...),
    current_user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    if not can_user_reply_to_review(db, str(current_user.id), review_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to reply to this review"
        )

    return create_reply(
        db=db,
        review_id=review_id,
        business_id=str(current_user.id),
        user_id=str(current_user.id),
        description=description,
    )


@router.put("/{review_id}/reply", response_model=BusinessReplyResponse)
def update_review_reply(
    review_id: UUID,
    description: str = Form(...),
    current_user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    if not can_user_reply_to_review(db, str(current_user.id), review_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to reply to this review"
        )

    reply = db.exec(
        select(BusinessReply).where(BusinessReply.review_id == review_id)
    ).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    return update_reply(db, reply, description)


@router.delete("/{review_id}/reply", status_code=204)
def delete_review_reply(
    review_id: UUID,
    current_user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    if not can_user_reply_to_review(db, str(current_user.id), review_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this reply"
        )

    reply = db.exec(
        select(BusinessReply).where(BusinessReply.review_id == review_id)
    ).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    delete_reply(db, reply)
    return None
