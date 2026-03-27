from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from app.database.session import get_db
from app.services.interests_services import get_all_interests, get_user_interests
from app.schemas.interests import InterestResponse
from app.models.user_interest import UserInterest
from app.models.interests import Interests
from app.models.user import User
from app.api.dependencies.permissions import get_current_user

router = APIRouter(prefix="/api/interests", tags=["Interests"])


class UserInterestsUpdate(BaseModel):
    interest_ids: List[UUID]


@router.get("", response_model=list[InterestResponse])
def get_interests(db: Session = Depends(get_db)):
    """Get all available interests."""
    return get_all_interests(db)


@router.get("/user", response_model=list[InterestResponse])
def get_user_interests_route(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_interests(db, user.id)


@router.put("/user")
def update_user_interests(
    data: UserInterestsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user.id

    existing = db.exec(select(UserInterest).where(UserInterest.user_id == user_id)).all()
    for ui in existing:
        db.delete(ui)

    for interest_id in data.interest_ids:
        interest = db.exec(select(Interests).where(Interests.id == interest_id)).first()
        if interest:
            db.add(UserInterest(user_id=user_id, interest_id=interest_id))

    db.commit()
    return {"detail": "Interests updated"}
