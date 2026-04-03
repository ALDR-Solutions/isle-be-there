from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.shared.dependencies.permissions import get_current_user

from .models import User
from .schemas import UserResponse, UserUpdate
from .service import get_profile, mark_interests_handled, update_profile

router = APIRouter(prefix="/api/profile", tags=["Profile"])


def _serialize_profile(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        avatar_url=user.avatar_url,
        phone=user.phone,
        birth_date=user.birth_date,
        interests_handled=bool(user.interests_handled),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("", response_model=dict, status_code=200)
def update_profile_endpoint(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = update_profile(db, current_user.id, data)
    return {"detail": "Profile updated", "profile": _serialize_profile(user)}


@router.get("", response_model=UserResponse, status_code=200)
def get_profile_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _serialize_profile(get_profile(db, current_user.id))


@router.patch("/interests-handled", response_model=dict, status_code=200)
def set_interests_handled(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    mark_interests_handled(db, current_user.id)
    return {"detail": "Updated"}
