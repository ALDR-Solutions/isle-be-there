from __future__ import annotations

from typing import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.security import decode_token
from app.infrastructure.database.session import get_db
from app.modules.bookings.models import Booking
from app.modules.businesses.models import Business
from app.modules.listings.models import Listing
from app.modules.reviews.models import Review
from app.modules.users.models import User

security = HTTPBearer()


def _get_user_from_token(
    credentials: HTTPAuthorizationCredentials,
    db: Session,
) -> User:
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
        )

    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    return _get_user_from_token(credentials, db)


def get_user_role(user: User) -> str:
    if user.user_type == "admin":
        return "admin"
    if user.user_type == "business":
        return "business"
    if user.user_type == "employee":
        return "employee"
    return "user"


def require_roles(*roles: str) -> Callable[[User], User]:
    allowed = {role for role in roles if role}

    def _dependency(user: User = Depends(get_current_user)) -> User:
        role = get_user_role(user)
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this resource",
            )
        return user

    return _dependency


def require_booking_owner(
    booking_id: int,
    user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
) -> Booking:
    booking = db.exec(select(Booking).where(Booking.id == booking_id)).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if not user.is_super_admin and str(booking.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return booking


def require_review_owner(
    review_id: int,
    user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
) -> Review:
    review = db.exec(select(Review).where(Review.id == review_id)).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if not user.is_super_admin and str(review.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return review


def require_business_owner(
    business_id: str,
    user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
) -> Business:
    business = db.exec(select(Business).where(Business.id == business_id)).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if not user.is_super_admin and str(business.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return business


def require_listing_owner(
    listing_id: str,
    user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
) -> Listing:
    listing = db.exec(select(Listing).where(Listing.id == listing_id)).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if user.is_super_admin:
        return listing

    if not listing.business_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    business = db.exec(select(Business).where(Business.id == listing.business_id)).first()
    if not business or str(business.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return listing


__all__ = [
    "get_current_user",
    "get_user_role",
    "require_roles",
    "require_booking_owner",
    "require_review_owner",
    "require_business_owner",
    "require_listing_owner",
]
