"""
Interests API - User interests management
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from uuid import UUID
from typing import List
from app.supabase_client import supabase, execute_with_retry
from app.core.security import decode_token

router = APIRouter(prefix="/api/interests", tags=["Interests"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user_id(token: str) -> str:
    """Extract user ID from token."""
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None


class InterestResponse(BaseModel):
    """Interest response schema."""
    id: UUID
    name: str
    category: str


class UserInterestUpdate(BaseModel):
    """Update user's interests."""
    interest_ids: List[str]


@router.get("", response_model=List[InterestResponse])
def get_all_interests():
    """Get all available interests."""
    response = execute_with_retry(
        lambda: supabase.table('interests').select('*').order('category').order('name').execute(),
        "get_all_interests"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    return [
        InterestResponse(
            id=interest['id'],
            name=interest['name'],
            category=interest['category']
        )
        for interest in response.data
    ]


@router.get("/user", response_model=List[dict])
def get_user_interests(token: str = Depends(oauth2_scheme)):
    """Get current user's selected interests."""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get user's interests
    response = execute_with_retry(
        lambda: supabase.table('user_interests').select('interest_id').eq('user_id', user_id).execute(),
        "get_user_interests"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    if not response.data:
        return []
    
    interest_ids = [item['interest_id'] for item in response.data]
    
    # Get interest details
    interests_response = execute_with_retry(
        lambda: supabase.table('interests').select('*').in_('id', interest_ids).execute(),
        "get_user_interests_details"
    )
    
    return interests_response.data


@router.put("/user", response_model=List[dict])
def update_user_interests(
    interest_data: UserInterestUpdate,
    token: str = Depends(oauth2_scheme)
):
    """Update current user's interests."""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Delete existing user interests
    execute_with_retry(
        lambda: supabase.table('user_interests').delete().eq('user_id', user_id).execute(),
        "delete_user_interests"
    )
    
    # Insert new user interests
    if interest_data.interest_ids:
        new_interests = [
            {"user_id": user_id, "interest_id": interest_id}
            for interest_id in interest_data.interest_ids
        ]
        
        response = execute_with_retry(
            lambda: supabase.table('user_interests').insert(new_interests).execute(),
            "insert_user_interests"
        )
        
        if response.error:
            raise HTTPException(status_code=500, detail=str(response.error))
    
    # Update profile to mark interests as handled
    profile_response = execute_with_retry(
        lambda: supabase.table('profiles').select('id').eq('user_id', user_id).execute(),
        "get_profile_interests"
    )
    
    if profile_response.data:
        execute_with_retry(
            lambda: supabase.table('profiles').update({"interests_handled": True}).eq('user_id', user_id).execute(),
            "update_profile_interests"
        )
    
    return get_user_interests(token)


@router.get("/categories", response_model=List[str])
def get_interest_categories():
    """Get all unique interest categories."""
    response = execute_with_retry(
        lambda: supabase.table('interests').select('category').execute(),
        "get_interest_categories"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    categories = list(set(item['category'] for item in response.data))
    return sorted(categories)
