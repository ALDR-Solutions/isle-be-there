from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import get_current_user

from .schemas import (
    InterestResponse,
    ItineraryInterestsResponse,
    UserInterestsUpdate,
)
from .service import (
    get_all_interests,
    get_interests_by_business_type,
    get_user_interests,
    update_user_interests,
    get_interests_by_listing_country
)

router = APIRouter(prefix="/api/interests", tags=["Interests"])


@router.get("", response_model=list[InterestResponse])
def get_interests(db: Session = Depends(get_db)):
    return get_all_interests(db)


@router.get("/business-type/{business_type_id}", response_model=list[InterestResponse])
def get_business_type_interests_route(
    business_type_id: UUID,
    db: Session = Depends(get_db),
):
    return get_interests_by_business_type(db, business_type_id)

@router.get("/listing-country/{country}", response_model=ItineraryInterestsResponse)
def get_listing_country_interests_route(
    country: str,
    bookable_only: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    return get_interests_by_listing_country(db, country, bookable_only)



@router.get("/user", response_model=list[InterestResponse])
def get_user_interests_route(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_interests(db, user.id)


@router.put("/user")
def update_user_interests_route(
    data: UserInterestsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_user_interests(db, user.id, data.interest_ids)
    return {"detail": "Interests updated"}
