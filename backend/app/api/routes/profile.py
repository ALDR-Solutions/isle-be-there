from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/api/profile", tags=["Profile"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class ProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None

@router.put("", status_code=200)
def update_profile(
    data: ProfileUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.exec(select(User).where(User.id == payload["sub"])).first()
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

    user.updated_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"detail": "Profile updated"}
