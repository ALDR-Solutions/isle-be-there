from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.security import decode_token
from app.infrastructure.database import get_db
from app.modules.users.schemas import (
    PasswordResetConfirm,
    RefreshTokenRequest,
    ResendVerificationRequest,
    ResetRequest,
    ResetPassword,
    TokenResponse,
    UserCreate,
    UserResponse,
)

from .service import (
    authenticate_user,
    build_token_response,
    disable_user_account,
    forget_password,
    refresh_user_token,
    register_user,
    resend_verification_email_for_user,
    reset_authenticated_user_password,
    reset_password_with_token,
    verify_email as verify_email_service,
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
    return {"detail": "Password updated"}


@router.post("/forgot-password")
def forgot_password(
    data: ResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    forget_password(db, data, background_tasks)
    return {"detail": "If an account exists for that email, a reset link has been sent."}


@router.post("/reset-password/confirm")
def confirm_reset_password(
    data: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    reset_password_with_token(db, data)
    return {"detail": "Password updated"}


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

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    verify_email_service(token, db)
    return {"detail": "Email verified successfully. You can now log in."}


@router.post("/resend-verification")
def resend_verification(
    data: ResendVerificationRequest,
    db: Session = Depends(get_db),
):
    resend_verification_email_for_user(db, data.email)
    return {"detail": "Verification email sent successfully."}

