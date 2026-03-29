from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.security import decode_token
from app.infrastructure.database import get_db
from app.modules.users.schemas import (
    RefreshTokenRequest,
    ResetPassword,
    TokenResponse,
    UserCreate,
    UserResponse,
)

from .service import (
    authenticate_user,
    build_token_response,
    disable_user_account,
    refresh_user_token,
    register_user,
    reset_authenticated_user_password,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def _require_subject(token: str) -> str:
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user ID")
    return user_id


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user_data)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    return build_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    return refresh_user_token(db, request)


@router.post("/logout")
def logout():
    return {"detail": "logged out"}


@router.post("/reset-password")
def reset_password(
    data: ResetPassword,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    reset_authenticated_user_password(db, _require_subject(token), data)
    return {"detail": "password updated"}


@router.get("/me", response_model=UserResponse)
def get_me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    from app.modules.users.service import get_user_by_id

    user = get_user_by_id(db, _require_subject(token))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/me", status_code=200)
def disable_account(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = _require_subject(token)
    disable_user_account(db, user_id)
    return {"detail": "Account disabled", "disabled_at": datetime.utcnow()}
