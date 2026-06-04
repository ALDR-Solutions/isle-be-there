from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .models import (
    BusinessTypeInterest,
    Interests,
    ListingInterest,
    UserInterest,
)
from .schemas import (
    InterestCategoryResponse,
    InterestResponse,
    ItineraryInterestsResponse,
)
from ..listings.models import Listing, Statuses
from ..services.models import Service, StatusTypes as ServiceStatusTypes


def serialize_interest(interest: Interests) -> InterestResponse:
    return InterestResponse(
        id=interest.id,
        name=interest.name,
        category=interest.category_rel.name if interest.category_rel else "",
        category_id=interest.category_id,
        created_at=interest.created_at,
    )


def serialize_interest_category(interest: Interests) -> InterestCategoryResponse | None:
    if not interest.category_rel:
        return None

    return InterestCategoryResponse(
        name=interest.category_rel.name,
        description=interest.category_rel.description,
    )


def get_all_interests(db: Session):
    rows = db.exec(
        select(Interests)
        .options(selectinload(Interests.category_rel))
        .order_by(Interests.name)
    ).all()
    return [serialize_interest(row) for row in rows]


def get_interests_by_business_type(db: Session, business_type_id: UUID):
    rows = db.exec(
        select(Interests)
        .options(selectinload(Interests.category_rel))
        .join(BusinessTypeInterest, BusinessTypeInterest.interest_id == Interests.id)
        .where(BusinessTypeInterest.business_type_id == business_type_id)
        .order_by(Interests.name)
    ).all()
    return [serialize_interest(row) for row in rows]


def get_interests_by_listing_country(
    db: Session, country: str, bookable_only: bool = False
) -> ItineraryInterestsResponse:
    query = (
        select(Interests)
        .options(selectinload(Interests.category_rel))
        .join(ListingInterest, ListingInterest.interest_id == Interests.id)
        .join(Listing, Listing.id == ListingInterest.listing_id)
        .where(Listing.address["country"].astext.ilike(f"%{country}%"))
        .where(Listing.status == Statuses.active)
        .distinct()
        .order_by(Interests.name)
    )

    if bookable_only:
        query = query.join(Service, Service.listing_id == Listing.id).where(
            Service.status == ServiceStatusTypes.active
        )

    rows = db.exec(query).all()
    interests = [serialize_interest(row) for row in rows]
    categories_by_name: dict[str, InterestCategoryResponse] = {}

    for row in rows:
        category = serialize_interest_category(row)
        if category is None:
            continue
        categories_by_name.setdefault(category.name, category)

    categories = sorted(categories_by_name.values(), key=lambda category: category.name)
    return ItineraryInterestsResponse(categories=categories, interests=interests)


def get_user_interests(db: Session, user_id: str):
    rows = db.exec(
        select(Interests)
        .options(selectinload(Interests.category_rel))
        .join(UserInterest, UserInterest.interest_id == Interests.id)
        .where(UserInterest.user_id == user_id)
        .order_by(Interests.name)
    ).all()
    return [serialize_interest(row) for row in rows]


def update_user_interests(db: Session, user_id, interest_ids):
    existing = db.exec(
        select(UserInterest).where(UserInterest.user_id == user_id)
    ).all()
    for user_interest in existing:
        db.delete(user_interest)

    valid_interest_ids = {
        interest.id
        for interest in db.exec(
            select(Interests).where(Interests.__table__.c.id.in_(interest_ids))
        ).all()
    }

    for interest_id in interest_ids:
        if interest_id in valid_interest_ids:
            db.add(UserInterest(user_id=user_id, interest_id=interest_id))

    db.commit()
