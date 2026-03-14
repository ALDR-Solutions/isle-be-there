from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.supabase_client import supabase, execute_with_retry
from app.core.security import decode_token

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
from uuid import UUID

class BookingCreate(BaseModel):
    service_id: int                 # matches services.service_id
    booking_time: datetime
    status: str | None = None
    user_id: UUID | None = None  # auto-filled from token
class BookingUpdate(BaseModel):
    booking_time: datetime | None = None
    status: str | None = None
def get_current_user_id(token: str) -> str:
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None
@router.get("", response_model=List[dict])
def get_bookings(skip: int = 0, limit: int = 20, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    response = execute_with_retry(
        lambda: supabase.table('bookings').select('*').eq('user_id', user_id).range(skip, skip + limit - 1).execute(),
        "get_bookings"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    return response.data
@router.get("/{booking_id}", response_model=dict)
def get_booking(booking_id: int, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    response = execute_with_retry(
        lambda: supabase.table('bookings').select('*').eq('id', booking_id).execute(),
        "get_booking"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    if not response.data:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if response.data[0]['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return response.data[0]
@router.post("", response_model=dict, status_code=201)
def create_booking(booking_data: BookingCreate, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    data = booking_data.dict(exclude_unset=True)
    data['user_id'] = user_id
    response = execute_with_retry(
        lambda: supabase.table('bookings').insert(data).execute(),
        "create_booking"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    return response.data[0]
@router.put("/{booking_id}", response_model=dict)
def update_booking(booking_id: int, booking_data: BookingUpdate, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    response = execute_with_retry(
        lambda: supabase.table('bookings').select('*').eq('id', booking_id).execute(),
        "check_booking_ownership_update"
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if response.data[0]['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = {k: v for k, v in booking_data.dict(exclude_unset=True).items() if v is not None}
    response = execute_with_retry(
        lambda: supabase.table('bookings').update(update_data).eq('id', booking_id).execute(),
        "update_booking"
    )
    return response.data[0]
@router.delete("/{booking_id}", status_code=204)
def cancel_booking(booking_id: int, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    response = execute_with_retry(
        lambda: supabase.table('bookings').select('user_id').eq('id', booking_id).execute(),
        "check_booking_ownership_delete"
    )
    if response.error:
        raise HTTPException(status_code=500, detail=str(response.error))
    if not response.data:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if response.data[0]['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    execute_with_retry(
        lambda: supabase.table('bookings').update({'status': 'cancelled'}).eq('id', booking_id).execute(),
        "cancel_booking"
    )
    return None
