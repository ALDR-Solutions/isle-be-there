"""Business logic for business replies to reviews."""

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, desc, select

from app.models.listing import Listing
from app.models.review import Review, BusinessReply
from app.models.user import User


def create_business_reply(
    db: Session, review_id: UUID, business_id: UUID, user_id: UUID, description: str
) -> dict:
    review = db.exec(select(Review).where(Review.id == review_id)).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    listing = db.exec(select(Listing).where(Listing.id == review.listing_id)).first()
    if not listing or str(listing.business_id) != str(business_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to reply to this review"
        )

    existing = db.exec(
        select(BusinessReply).where(BusinessReply.review_id == review_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=409, detail="Reply already exists for this review"
        )

    reply = BusinessReply(
        review_id=review_id,
        business_id=business_id,
        user_id=user_id,
        description=description,
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)

    return {
        "id": reply.id,
        "review_id": reply.review_id,
        "business_id": reply.business_id,
        "user_id": reply.user_id,
        "description": reply.description,
        "created_at": reply.created_at,
        "updated_at": reply.updated_at,
    }


def get_business_reply(db: Session, review_id: UUID) -> dict | None:
    result = db.exec(
        select(BusinessReply, User.username)
        .join(User, BusinessReply.user_id == User.id)
        .where(BusinessReply.review_id == review_id)
    ).first()

    if not result:
        return None

    reply, username = result
    return {
        "id": reply.id,
        "review_id": reply.review_id,
        "business_id": reply.business_id,
        "user_id": reply.user_id,
        "user_name": username,
        "description": reply.description,
        "created_at": reply.created_at,
        "updated_at": reply.updated_at,
    }


def update_business_reply(
    db: Session,
    review_id: UUID,
    user_id: UUID,
    description: str,
    is_admin: bool = False,
) -> dict:
    reply = db.exec(
        select(BusinessReply).where(BusinessReply.review_id == review_id)
    ).first()

    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    if not is_admin and str(reply.user_id) != str(user_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to update this reply"
        )

    reply.description = description
    reply.updated_at = datetime.utcnow()
    db.add(reply)
    db.commit()
    db.refresh(reply)

    return {
        "id": reply.id,
        "review_id": reply.review_id,
        "business_id": reply.business_id,
        "user_id": reply.user_id,
        "description": reply.description,
        "created_at": reply.created_at,
        "updated_at": reply.updated_at,
    }


def delete_business_reply(
    db: Session, review_id: UUID, user_id: UUID, is_admin: bool = False
) -> None:
    reply = db.exec(
        select(BusinessReply).where(BusinessReply.review_id == review_id)
    ).first()

    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    if not is_admin and str(reply.user_id) != str(user_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this reply"
        )

    db.delete(reply)
    db.commit()
