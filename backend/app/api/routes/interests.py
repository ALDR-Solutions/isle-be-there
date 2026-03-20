from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database.session import get_db
from app.services.interests_services import get_all_interests, get_user_interests
from app.schemas.interests import InterestResponse
from app.core.security import decode_token
from app.models.user_interest import UserInterest
from app.models.interests import Interests

router = APIRouter(prefix="/api/interests", tags=["Interests"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class UserInterestsUpdate(BaseModel):
    interest_ids: List[UUID]


@router.get("", response_model=list[InterestResponse])
def get_interests(db: Session = Depends(get_db)):
    """Get all available interests."""
    return get_all_interests(db)


@router.get("/user", response_model=list[InterestResponse])
def get_user_interests_route(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return get_user_interests(db, payload["sub"])


@router.put("/user")
def update_user_interests(
    data: UserInterestsUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload["sub"]

    existing = db.exec(select(UserInterest).where(UserInterest.user_id == user_id)).all()
    for ui in existing:
        db.delete(ui)

    for interest_id in data.interest_ids:
        interest = db.exec(select(Interests).where(Interests.id == interest_id)).first()
        if interest:
            db.add(UserInterest(user_id=user_id, interest_id=interest_id))

    db.commit()
    return {"detail": "Interests updated"}
