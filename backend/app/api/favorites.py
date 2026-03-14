"""
Favorites API - User favorites management
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from uuid import UUID
from typing import List
from app.supabase_client import supabase, execute_with_retry
from app.core.security import decode_token

router = APIRouter(prefix="/api/favorites", tags=["Favorites"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user_id(token: str) -> str:
    """Extract user ID from token."""
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None


class FavoriteResponse(BaseModel):
    """Favorite response schema."""
    id: UUID
    user_id: UUID
    listing_id: UUID


class FavoriteWithListing(BaseModel):
    """Favorite with listing details."""
    id: UUID
    user_id: UUID
    listing_id: UUID
    listing: dict = {}


@router.get("", response_model=List[dict])
def get_favorites(token: str = Depends(oauth2_scheme)):
    """Get current user's favorites with listing details."""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get favorites
    response = execute_with_retry(
        lambda: supabase.table('favourites').select('*').eq('user_id', user_id).execute(),
        "get_favorites"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    favorites = response.data
    
    # Get listing details for each favorite
    if favorites:
        listing_ids = [f['listing_id'] for f in favorites]
        listings_response = execute_with_retry(
            lambda: supabase.table('listings').select('*').in_('id', listing_ids).execute(),
            "get_favorite_listings"
        )
        
        listings_map = {str(l['id']): l for l in listings_response.data}
        
        # Combine favorites with listing details
        for fav in favorites:
            listing_id = str(fav['listing_id'])
            if listing_id in listings_map:
                fav['listing'] = listings_map[listing_id]
    
    return favorites


@router.post("/{listing_id}", response_model=dict)
def add_favorite(
    listing_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Add a listing to favorites."""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if listing exists
    listing_response = execute_with_retry(
        lambda: supabase.table('listings').select('id').eq('id', listing_id).execute(),
        "check_listing"
    )
    
    if not listing_response.data:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Check if already favorited
    existing = execute_with_retry(
        lambda: supabase.table('favourites').select('id').eq('user_id', user_id).eq('listing_id', listing_id).execute(),
        "check_existing_favorite"
    )
    
    if existing.data:
        raise HTTPException(status_code=400, detail="Already in favorites")
    
    # Add to favorites
    response = execute_with_retry(
        lambda: supabase.table('favourites').insert({
            "user_id": user_id,
            "listing_id": listing_id
        }).execute(),
        "add_favorite"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    return response.data[0]


@router.delete("/{listing_id}", status_code=204)
def remove_favorite(
    listing_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Remove a listing from favorites."""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if favorite exists
    existing = execute_with_retry(
        lambda: supabase.table('favourites').select('id').eq('user_id', user_id).eq('listing_id', listing_id).execute(),
        "check_favorite_remove"
    )
    
    if not existing.data:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    # Remove from favorites
    response = execute_with_retry(
        lambda: supabase.table('favourites').delete().eq('user_id', user_id).eq('listing_id', listing_id).execute(),
        "remove_favorite"
    )
    
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    
    return None


@router.get("/{listing_id}/check", response_model=dict)
def check_favorite(
    listing_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Check if a listing is in user's favorites."""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    existing = execute_with_retry(
        lambda: supabase.table('favourites').select('id').eq('user_id', user_id).eq('listing_id', listing_id).execute(),
        "check_favorite_status"
    )
    
    return {"is_favorite": bool(existing.data)}
