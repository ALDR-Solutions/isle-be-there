from sqlmodel import Session, select
from app.models.user_interest import UserInterest
from app.models.interests import Interests

def get_all_interests(db: Session):
    return db.exec(select(Interests)).all()

def get_user_interests(db: Session, user_id: str):
    return db.exec(
        select(Interests)
        .join(UserInterest, UserInterest.interest_id == Interests.id)
        .where(UserInterest.user_id == user_id)
    ).all()