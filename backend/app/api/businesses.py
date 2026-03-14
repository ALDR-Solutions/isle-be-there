"""
Businesses API - Business management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from app.supabase_client import supabase, execute_with_retry
from app.core.security import decode_token

router = APIRouter(prefix="/api/businesses", tags=["Businesses"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user_id(token: str) -> str:
    """Extract user ID from token."""
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None


class BusinessResponse(BaseModel):
    """Business response schema."""
    id: UUID
    business_name: str
    description: Optional[str] = None
    business_email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    is_verified: bool = False
    business_type_id: Optional[UUID] = None
    user_id: UUID
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BusinessWithType(BusinessResponse):
    """Business with type details."""
    business_type: Optional[dict] = {}


@router.get("", response_model=List[dict])
def get_businesses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    business_type: Optional[str] = None,
    verified_only: bool = False
):
    """Get all businesses."""
    query = supabase.table('businesses').select('*')
    
    if business_type:
        query = query.eq('business_type_id', business_type)
    
    if verified_only:
        query = query.eq('is_verified', True)
    
    response = execute_with_retry(
        lambda: query.range(skip, skip + limit - 1).order('business_name').execute(),
        "get_businesses"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    return response.data


@router.get("/{business_id}", response_model=dict)
def get_business(business_id: str):
    """Get a single business with type details."""
    response = execute_with_retry(
        lambda: supabase.table('businesses').select('*').eq('id', business_id).execute(),
        "get_business"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business = response.data[0]
    
    # Get business type if exists
    if business.get('business_type_id'):
        type_response = execute_with_retry(
            lambda: supabase.table('business_types').select('*').eq('id', business['business_type_id']).execute(),
            "get_business_type"
        )
        if type_response.data:
            business['business_type'] = type_response.data[0]
    
    return business


@router.get("/{business_id}/listings", response_model=List[dict])
def get_business_listings(business_id: str):
    """Get all listings for a business."""
    # First verify business exists
    business_response = execute_with_retry(
        lambda: supabase.table('businesses').select('id').eq('id', business_id).execute(),
        "verify_business"
    )
    
    if not business_response.data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get listings
    response = execute_with_retry(
        lambda: supabase.table('listings').select('*').eq('business_id', business_id).order('created_at', ascending=False).execute(),
        "get_business_listings"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    return response.data


@router.post("", response_model=dict, status_code=201)
def create_business(
    business_data: dict,
    token: str = Depends(oauth2_scheme)
):
    """Create a new business."""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user already has a business
    existing = execute_with_retry(
        lambda: supabase.table('businesses').select('id').eq('user_id', user_id).execute(),
        "check_existing_business"
    )
    
    if existing.data:
        raise HTTPException(status_code=400, detail="User already has a business")
    
    # Add user_id to business data
    business_data['user_id'] = user_id
    
    response = execute_with_retry(
        lambda: supabase.table('businesses').insert(business_data).execute(),
        "create_business"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    return response.data[0]


@router.put("/{business_id}", response_model=dict)
def update_business(
    business_id: str,
    business_data: dict,
    token: str = Depends(oauth2_scheme)
):
    """Update a business."""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check ownership
    existing = execute_with_retry(
        lambda: supabase.table('businesses').select('user_id').eq('id', business_id).execute(),
        "check_business_ownership"
    )
    
    if not existing.data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    if existing.data[0]['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Remove non-updateable fields
    update_data = {k: v for k, v in business_data.items() if k not in ['id', 'user_id'] and v is not None}
    
    response = execute_with_retry(
        lambda: supabase.table('businesses').update(update_data).eq('id', business_id).execute(),
        "update_business"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    return response.data[0]


@router.get("/types", response_model=List[dict])
def get_business_types():
    """Get all business types."""
    response = execute_with_retry(
        lambda: supabase.table('business_types').select('*').order('name').execute(),
        "get_business_types"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    return response.data
