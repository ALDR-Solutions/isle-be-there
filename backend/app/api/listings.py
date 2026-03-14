from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.supabase_client import supabase, execute_with_retry

router = APIRouter(prefix="/api/listings", tags=["Listings"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
from uuid import UUID

class ListingBase(BaseModel):
    business_id: UUID
    title: str
    description: str | None = None
    address: dict | None = None          # stored as jsonb
    latitude: float | None = None
    longitude: float | None = None
    base_price: float | None = None      # numeric
    business_type: UUID | None = None
    image_urls: list | None = None       # array of text
    status: str | None = None
    phone_number: str | None = None
    email_address: str | None = None
    location: str | None = None          # user-defined, keep as string
    embedding: str | None = None         # user-defined, keep as string
class ListingCreate(ListingBase):
    pass
class ListingUpdate(BaseModel):
    business_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    address: dict | None = None
    latitude: float | None = None
    longitude: float | None = None
    base_price: float | None = None
    business_type: UUID | None = None
    image_urls: list | None = None
    status: str | None = None
    phone_number: str | None = None
    email_address: str | None = None
    location: str | None = None
    embedding: str | None = None
    is_active: bool | None = None
class ListingResponse(ListingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    business_id: UUID
    
    class Config:
        from_attributes = True
def get_current_user_id(token: str) -> str:
    from app.core.security import decode_token
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None
@router.get("", response_model=List[dict])
def get_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    city: str | None = None,
    country: str | None = None,
    business_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str | None = None,
    sort_order: str = Query("asc", regex="^(asc|desc)$")
):
    # Build query - show all listings (no filter)
    query = supabase.table('listings').select('*')
    
    if city:
        query = query.ilike('address->>city', f'%{city}%')  # assuming address is jsonb with city
    if country:
        query = query.ilike('address->>country', f'%{country}%')
    if business_type:
        query = query.eq('business_type', business_type)
    if min_price is not None:
        query = query.gte('base_price', min_price)
    if max_price is not None:
        query = query.lte('base_price', max_price)
    
    # Apply sorting
    if sort_by:
        order_column = sort_by
        ascending = sort_order == "asc"
        query = query.order(order_column, ascending=ascending)
    
    response = execute_with_retry(
        lambda: query.range(skip, skip + limit - 1).execute(),
        "get_listings"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    return response.data
@router.get("/{listing_id}", response_model=dict)
def get_listing(listing_id: str):
    response = execute_with_retry(
        lambda: supabase.table('listings').select('*').eq('id', listing_id).execute(),
        "get_listing"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    if not response.data:
        raise HTTPException(status_code=404, detail="Listing not found")
    return response.data[0]
@router.post("", response_model=dict, status_code=201)
def create_listing(listing_data: ListingCreate, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    data = listing_data.model_dump(exclude_unset=True)
    data['business_id'] = user_id   # assuming user owns a business
    response = execute_with_retry(
        lambda: supabase.table('listings').insert(data).execute(),
        "create_listing"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    return response.data[0]
@router.put("/{listing_id}", response_model=dict)
def update_listing(listing_id: str, listing_data: ListingUpdate, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check ownership (business_id)
    response = execute_with_retry(
        lambda: supabase.table('listings').select('business_id').eq('id', listing_id).execute(),
        "check_listing_ownership_update"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    if not response.data:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if response.data[0]['business_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = {k: v for k, v in listing_data.model_dump(exclude_unset=True).items() if v is not None}
    response = execute_with_retry(
        lambda: supabase.table('listings').update(update_data).eq('id', listing_id).execute(),
        "update_listing"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    return response.data[0]
@router.delete("/{listing_id}", status_code=204)
def delete_listing(listing_id: str, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    response = execute_with_retry(
        lambda: supabase.table('listings').select('business_id').eq('id', listing_id).execute(),
        "check_listing_ownership_delete"
    )    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))    
    if not response.data:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if response.data[0]['business_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    execute_with_retry(
        lambda: supabase.table('listings').delete().eq('id', listing_id).execute(),
        "delete_listing"
    )
    return None
