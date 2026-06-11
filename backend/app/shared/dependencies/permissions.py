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
from app.modules.services.models import Service
from app.modules.users.models import User
from app.shared.domain import (
    ensure_booking_owner,
    ensure_business_owner,
    ensure_listing_owner,
    ensure_listing_service_manager,
    ensure_review_owner,
    ensure_service_access,
    get_booking_or_404,
    get_business_or_404,
    get_listing_or_404,
    get_review_or_404,
    get_service_or_404,
    get_user_by_id,
)

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

def get_user_from_token(
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

    user = get_user_by_id(db, user_id)
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
    return get_user_from_token(credentials, db)


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_security),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    return get_user_from_token(credentials, db)


def get_user_role(user: User) -> str:
    if user.user_type == "admin":
        return "admin"
    if user.user_type == "business":
        return "business"
    if user.user_type == "employee":
        return "employee"
    if user.user_type == "regular":
        return "regular"
    return "user"


def require_roles(*roles: str) -> Callable[[User], User]:
    allowed = {role for role in roles if role}

    def dependency(user: User = Depends(get_current_user)) -> User:
        role = get_user_role(user)
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this resource",
            )
        return user

    return dependency


def require_booking_owner(
    booking_id: UUID,
    user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
) -> Booking:
    booking = get_booking_or_404(db, booking_id)
    return ensure_booking_owner(user, booking)


def require_booking_listing_manager(
    booking_id: UUID,
    user: User = Depends(require_roles("business", "employee", "admin")),
    db: Session = Depends(get_db),
) -> Booking:
    booking = get_booking_or_404(db, booking_id)
    service = get_service_or_404(db, booking.service_id)
    get_listing_service_manager_or_403(db, user, service.listing_id)
    return booking


def require_review_owner(
    review_id: UUID,
    user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
) -> Review:
    review = get_review_or_404(db, review_id)
    return ensure_review_owner(user, review)


def require_business_owner(
    business_id: str,
    user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
) -> Business:
    business = get_business_or_404(db, business_id)
    return ensure_business_owner(user, business)


def require_listing_owner(
    listing_id: str,
    user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
) -> Listing:
    listing = get_listing_or_404(db, listing_id)
    return ensure_listing_owner(db, user, listing)


def require_service_access(
    service_id: UUID,
    user: User = Depends(require_roles("business", "employee", "admin")),
    db: Session = Depends(get_db),
) -> Service:
    service = get_service_or_404(db, service_id)
    return ensure_service_access(db, user, service)


def get_listing_service_manager_or_403(
    db: Session,
    user: User,
    listing_id: UUID | str,
) -> Listing:
    listing = get_listing_or_404(db, listing_id)
    return ensure_listing_service_manager(db, user, listing)


def require_listing_service_manager(
    listing_id: UUID | str,
    user: User = Depends(require_roles("business", "employee", "admin")),
    db: Session = Depends(get_db),
) -> Listing:
    return get_listing_service_manager_or_403(db, user, listing_id)


__all__ = [
    "get_current_user",
    "get_optional_current_user",
    "get_user_role",
    "require_roles",
    "require_booking_owner",
    "require_booking_listing_manager",
    "require_review_owner",
    "require_business_owner",
    "require_listing_owner",
    "require_service_access",
    "get_listing_service_manager_or_403",
    "require_listing_service_manager",
]
