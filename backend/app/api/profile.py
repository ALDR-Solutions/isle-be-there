"""
Profile API - User profile management
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional
from app.supabase_client import supabase, execute_with_retry
from app.core.security import decode_token

router = APIRouter(prefix="/api/profile", tags=["Profile"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user_id(token: str) -> str:
    """Extract user ID from token."""
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None


class ProfileUpdate(BaseModel):
    """Profile update schema."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    avatar_url: Optional[str] = None


class ProfileResponse(BaseModel):
    """Profile response schema."""
    id: UUID
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    avatar_url: Optional[str] = None
    interests_handled: bool = False


@router.get("", response_model=ProfileResponse)
def get_profile(token: str = Depends(oauth2_scheme)):
    """Get current user's profile."""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    response = execute_with_retry(
        lambda: supabase.table('profiles').select('*').eq('user_id', user_id).execute(),
        "get_profile"
    )
    
    if not response.data:
        # Create profile if doesn't exist
        new_profile = {
            "user_id": user_id,
            "interests_handled": False
        }
        response = execute_with_retry(
            lambda: supabase.table('profiles').insert(new_profile).execute(),
            "create_profile"
        )
        if response.error:
            raise HTTPException(status_code=500, detail=str(response.error))
        return ProfileResponse(id=response.data[0]['id'], user_id=user_id)
    
    profile = response.data[0]
    return ProfileResponse(
        id=profile['id'],
        user_id=profile['user_id'],
        first_name=profile.get('first_name'),
        last_name=profile.get('last_name'),
        phone=profile.get('phone'),
        birth_date=profile.get('birth_date'),
        avatar_url=profile.get('avatar_url'),
        interests_handled=profile.get('interests_handled', False)
    )


@router.put("", response_model=ProfileResponse)
def update_profile(
    profile_data: ProfileUpdate,
    token: str = Depends(oauth2_scheme)
):
    """Update current user's profile."""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get existing profile
    response = execute_with_retry(
        lambda: supabase.table('profiles').select('*').eq('user_id', user_id).execute(),
        "get_profile_update"
    )
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile_id = response.data[0]['id']
    
    # Build update data
    update_data = {k: v for k, v in profile_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if update_data:
        response = execute_with_retry(
            lambda: supabase.table('profiles').update(update_data).eq('id', profile_id).execute(),
            "update_profile"
        )
        if response.error:
            raise HTTPException(status_code=500, detail=str(response.error))
    
    return get_profile(token)


@router.put("/avatar", response_model=ProfileResponse)
def update_avatar(
    avatar_url: str,
    token: str = Depends(oauth2_scheme)
):
    """Update user's avatar URL."""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get existing profile
    response = execute_with_retry(
        lambda: supabase.table('profiles').select('*').eq('user_id', user_id).execute(),
        "get_profile_avatar"
    )
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile_id = response.data[0]['id']
    
    response = execute_with_retry(
        lambda: supabase.table('profiles').update({"avatar_url": avatar_url}).eq('id', profile_id).execute(),
        "update_avatar"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    return get_profile(token)
