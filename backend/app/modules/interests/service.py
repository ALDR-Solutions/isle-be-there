from uuid import UUID

from sqlmodel import Session, select

from .models import BusinessTypeInterest, Interests, ListingInterest, UserInterest
from ..listings.models import Listing, Statuses
from ..services.models import Service, StatusTypes as ServiceStatusTypes


def get_all_interests(db: Session):
    return db.exec(select(Interests)).all()


def get_interests_by_business_type(db: Session, business_type_id: UUID):
    return db.exec(
        select(Interests)
        .join(BusinessTypeInterest, BusinessTypeInterest.interest_id == Interests.id)
        .where(BusinessTypeInterest.business_type_id == business_type_id)
        .order_by(Interests.name)
    ).all()


def get_interests_by_listing_country(
    db: Session, country: str, bookable_only: bool = False
):
    query = (
        select(Interests)
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

    return db.exec(query).all()


def get_user_interests(db: Session, user_id: str):
    return db.exec(
        select(Interests)
        .join(UserInterest, UserInterest.interest_id == Interests.id)
        .where(UserInterest.user_id == user_id)
    ).all()


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
