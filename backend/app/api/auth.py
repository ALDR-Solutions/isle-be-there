from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from starlette.responses import RedirectResponse
from app.supabase_client import supabase, execute_with_retry
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_business: bool = False
class UserResponse(BaseModel):
    id: UUID
    email: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_business: bool | None = False
    is_super_admin: bool | None = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
class RefreshTokenRequest(BaseModel):
    refresh_token: str
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate):
    # use Supabase Auth to create user (password hashed internally)
    try:
        signup_payload = {
            "email": user_data.email,
            "password": user_data.password,
            "options": {"data": {
                "username": user_data.username,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "is_business": user_data.is_business,
            }}
        }
        res = supabase.auth.sign_up(signup_payload)
    except Exception as e:
        # Supabase returns errors for duplicates etc.
        raise HTTPException(status_code=400, detail=str(e))

    user = res.user
    if not user:
        raise HTTPException(status_code=400, detail="Failed to create user")

    # build response object from returned user
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.user_metadata.get("username"),
        first_name=user.user_metadata.get("first_name"),
        last_name=user.user_metadata.get("last_name"),
        is_business=user.user_metadata.get("is_business"),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password,
        })
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = res.user
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
# refresh token logic remains same; user table query used for validation
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest):
    payload = decode_token(request.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    response = supabase.table('users').select('*').eq('id', user_id).execute()
    user = response.data[0] if response.data else None
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

# OAuth2/social login helpers
@router.get("/login/google")
def oauth_google():
    # redirect to Supabase oauth endpoint
    res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {"redirect_to": "http://localhost:8000/api/auth/oauth_callback"}
    })
    return RedirectResponse(res.url)

@router.get("/oauth_callback")
def oauth_callback(code: str = None):
    if not code:
        raise HTTPException(status_code=400, detail="Code not provided")
    resp = supabase.auth.exchange_code_for_session({"auth_code": code})
    if not resp.session or not resp.user:
        raise HTTPException(status_code=400, detail="OAuth exchange failed")
    # return tokens to client
    return {
        "access_token": create_access_token(data={"sub": resp.user.id}),
        "refresh_token": create_refresh_token(data={"sub": resp.user.id}),
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login"))):
    # simply call supabase sign_out if needed; tokens are client-side
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    return {"detail": "logged out"}

# password reset and confirmation routes
class ResetRequest(BaseModel):
    email: EmailStr

@router.post("/forgot-password")
def forgot_password(req: ResetRequest):
    try:
        supabase.auth.reset_password_for_email(req.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"detail": "reset email sent"}

class ResetPassword(BaseModel):
    password: str

@router.post("/reset-password")
def reset_password(data: ResetPassword, token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login"))):
    try:
        supabase.auth.update_user({"password": data.password})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"detail": "password updated"}

@router.get("/confirm")
def confirm(token_hash: str, type: str = "email"):
    try:
        supabase.auth.verify_otp({"token_hash": token_hash, "type": type})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"detail": "confirmed"}
@router.get("/me", response_model=UserResponse)
def get_me(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login"))):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    
    # Try to get user from profiles table (our custom table)
    response = execute_with_retry(
        lambda: supabase.table('profiles').select('*').eq('user_id', user_id).execute(),
        "get_user_profile"
    )
    
    if not response.data:
        # No profile yet - return basic info from token
        return UserResponse(
            id=user_id,
            email=payload.get("email"),
            username=payload.get("username"),
        )
    
    profile = response.data[0]
    return UserResponse(
        id=profile.get('user_id'),
        email=profile.get('email'),
        username=profile.get('username'),
        first_name=profile.get('first_name'),
        last_name=profile.get('last_name'),
        is_business=profile.get('is_business', False),
        is_super_admin=False,
        created_at=profile.get('created_at'),
        updated_at=profile.get('updated_at'),
    )