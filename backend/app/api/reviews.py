from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.supabase_client import supabase, execute_with_retry
from app.core.security import decode_token

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
from uuid import UUID

class ReviewCreate(BaseModel):
    listing_id: UUID
    rating: int
    description: str | None = None
class ReviewUpdate(BaseModel):
    rating: int | None = None
    description: str | None = None
def get_current_user_id(token: str) -> str:
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None
@router.get("", response_model=List[dict])
def get_reviews(listing_id: UUID | None = None, skip: int = 0, limit: int = 20):
    query = supabase.table('reviews').select('*')
    
    if listing_id:
        query = query.eq('listing_id', str(listing_id))
    
    response = execute_with_retry(
        lambda: query.range(skip, skip + limit - 1).execute(),
        "get_reviews"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    return response.data
@router.get("/{review_id}", response_model=dict)
def get_review(review_id: str):
    response = execute_with_retry(
        lambda: supabase.table('reviews').select('*').eq('id', review_id).execute(),
        "get_review"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    if not response.data:
        raise HTTPException(status_code=404, detail="Review not found")
    return response.data[0]
@router.post("", response_model=dict, status_code=201)
def create_review(review_data: ReviewCreate, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check listing exists
    listing_response = execute_with_retry(
        lambda: supabase.table('listings').select('id').eq('id', review_data.listing_id).execute(),
        "check_listing_exists"
    )
    if not listing_response.data:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Validate rating
    if not 1 <= review_data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Check if user already reviewed
    existing = execute_with_retry(
        lambda: supabase.table('reviews').select('id').eq('listing_id', review_data.listing_id).eq('user_id', user_id).execute(),
        "check_existing_review"
    )
    if existing.data:
        raise HTTPException(status_code=400, detail="You have already reviewed this listing")
    
    data = review_data.model_dump()
    data['user_id'] = user_id
    
    response = execute_with_retry(
        lambda: supabase.table('reviews').insert(data).execute(),
        "create_review"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    return response.data[0]
@router.put("/{review_id}", response_model=dict)
def update_review(review_id: str, review_data: ReviewUpdate, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    response = execute_with_retry(
        lambda: supabase.table('reviews').select('*').eq('id', review_id).execute(),
        "check_review_ownership_update"
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if response.data[0]['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = {k: v for k, v in review_data.dict(exclude_unset=True).items() if v is not None}
    response = execute_with_retry(
        lambda: supabase.table('reviews').update(update_data).eq('id', review_id).execute(),
        "update_review"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    return response.data[0]
@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: str, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    response = execute_with_retry(
        lambda: supabase.table('reviews').select('user_id').eq('id', review_id).execute(),
        "check_review_ownership_delete"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    if not response.data:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if response.data[0]['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    execute_with_retry(
        lambda: supabase.table('reviews').delete().eq('id', review_id).execute(),
        "delete_review"
    )
    return None