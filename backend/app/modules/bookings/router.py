from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.listings.models import Listing
from app.modules.users.models import User
from app.shared.dependencies.permissions import (
    require_booking_owner,
    require_listing_service_manager,
    require_roles,
)

from .models import Booking
from .schemas import BookingCreate, BookingCreateResponse, BookingUpdate, BookingResponse, BookingPriceResponse, BulkBookingCreateRequest, BulkBookingCreateResponse, PaymentIntentResponse
from .service import (
    cancel_booking,
    create_booking,
    create_bulk_bookings,
    create_payment_intent,
    delete_booking,
    get_booking_by_id,
    list_bookings_for_listing,
    list_bookings,
    update_booking,
    price_booking_by_id,
)

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])



@router.get("", response_model=List[BookingResponse])
def get_bookings(
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    return list_bookings(db, current_user.id)


@router.get("/listing/{listing_id}", response_model=List[BookingResponse])
def get_bookings_by_listing(
    listing: Listing = Depends(require_listing_service_manager),
    db: Session = Depends(get_db),
):
    return list_bookings_for_listing(db, listing.id)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    current_user: User = Depends(require_roles("regular", "admin")),
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    return get_booking_by_id(db, booking.id, current_user.id)




@router.post("", response_model=BookingCreateResponse, status_code=201)
def create_booking_endpoint(
    booking_data: BookingCreate,
    current_user: User = Depends(require_roles("regular")),
    db: Session = Depends(get_db),
):
    return create_booking(db, booking_data, current_user.id)


@router.post("/bulk", response_model=BulkBookingCreateResponse, status_code=201)
def create_bulk_bookings_endpoint(
    request: BulkBookingCreateRequest,
    current_user: User = Depends(require_roles("regular")),
    db: Session = Depends(get_db),
):
    bookings = create_bulk_bookings(db, request.items, current_user.id)
    return BulkBookingCreateResponse(
        bookings=[BookingCreateResponse.model_validate(b) for b in bookings]
    )


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking_endpoint(
    booking_data: BookingUpdate,
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    
    update_data = booking_data.model_dump(exclude_unset=True)

    return update_booking(db, booking, update_data)


@router.post("/{booking_id}/cancel", status_code=204)
def cancel_booking_endpoint(
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):

    cancel_booking(db, booking)
    return Response(status_code=204)


@router.post("/{booking_id}/payment-intent", response_model=PaymentIntentResponse)
def create_payment_intent_endpoint(
    current_user: User = Depends(require_roles("regular", "admin")),
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    result = create_payment_intent(db, booking.id, current_user.id)
    return PaymentIntentResponse(**result)


@router.post("/{booking_id}/confirm-payment")
def confirm_payment_endpoint(
    current_user: User = Depends(require_roles("regular", "admin")),
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    """Confirm payment was successful via Stripe API and update booking status."""
    # Delegate to stripe_payment service
    from app.modules.stripe_payment.service import confirm_payment as stripe_confirm_payment
    result = stripe_confirm_payment(db, booking)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.delete("/{booking_id}", status_code=204)
def delete_booking_endpoint(
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    delete_booking(db, booking)
    return Response(status_code=204)


@router.get("/{booking_id}/price", response_model=BookingPriceResponse)
def get_booking_price_endpoint(
    current_user: User = Depends(require_roles("regular", "admin")),
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    price = price_booking_by_id(db, booking.id, current_user.id)
    return BookingPriceResponse(**price)
