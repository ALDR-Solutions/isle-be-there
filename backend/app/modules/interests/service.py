from uuid import UUID

from sqlmodel import Session, select

from .models import BusinessTypeInterest, Interests, UserInterest


def get_all_interests(db: Session):
    return db.exec(select(Interests)).all()


def get_interests_by_business_type(db: Session, business_type_id: UUID):
    return db.exec(
        select(Interests)
        .join(BusinessTypeInterest, BusinessTypeInterest.interest_id == Interests.id)
        .where(BusinessTypeInterest.business_type_id == business_type_id)
        .order_by(Interests.name)
    ).all()


def get_user_interests(db: Session, user_id: str):
    return db.exec(
        select(Interests)
        .join(UserInterest, UserInterest.interest_id == Interests.id)
        .where(UserInterest.user_id == user_id)
    ).all()


def update_user_interests(db: Session, user_id, interest_ids):
    existing = db.exec(select(UserInterest).where(UserInterest.user_id == user_id)).all()
    for user_interest in existing:
        db.delete(user_interest)

    valid_interest_ids = {
        interest.id
        for interest in db.exec(select(Interests).where(Interests.__table__.c.id.in_(interest_ids))).all()
    }
    for interest_id in interest_ids:
        if interest_id in valid_interest_ids:
            db.add(UserInterest(user_id=user_id, interest_id=interest_id))

    db.commit()
