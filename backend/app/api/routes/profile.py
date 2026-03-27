from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import Session, select
from app.api.dependencies.permissions import get_current_user
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User
from app.models.profile import Profile

router = APIRouter(prefix="/api/profile", tags=["Profile"])


class ProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    phone: str | None = None
    birth_date: datetime | None = None
    


@router.put("", status_code=200)
def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    user = db.exec(select(User).where(User.id == current_user.id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.username is not None:
        # check uniqueness
        existing = db.exec(select(User).where(User.username == data.username)).first()
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = data.username
    if data.email is not None:
        existing = db.exec(select(User).where(User.email == data.email)).first()
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = data.email
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    if data.phone is not None:
        user.phone = data.phone
    if data.birth_date is not None:
        user.birth_date = data.birth_date


    user.updated_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"detail": "Profile updated"}


@router.get("", status_code=200)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.exec(select(User).where(User.id == payload["sub"])).first()
    if not profile:
        return {"interests_handled": False}

    return {
        "user_id": str(profile.id),
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "avatar_url": profile.avatar_url,
        "phone": profile.phone,
        "birth_date": str(profile.birth_date) if profile.birth_date else None,
        "interests_handled": profile.interests_handled or False,
        "created_at": str(profile.created_at) if profile.created_at else None,
        "updated_at": str(profile.updated_at) if profile.updated_at else None,
    }


@router.patch("/interests-handled", status_code=200)
def set_interests_handled(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.exec(select(User).where(User.id == payload["sub"])).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.interests_handled = True
    db.add(profile)
    db.commit()
    return {"detail": "Updated"}

