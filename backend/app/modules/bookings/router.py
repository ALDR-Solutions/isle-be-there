from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.listings.models import Listing
from app.modules.users.models import User, UserTypes
from app.shared.dependencies.permissions import (
    require_booking_listing_manager,
    require_booking_owner,
    require_listing_service_manager,
    require_roles,
)

from .models import Booking
from .schemas import BusinessBookingCancelRequest, BookingCreate, BookingCreateResponse, BookingUpdate, BookingResponse, BulkBookingCreateRequest, BulkBookingCreateResponse, PaymentIntentResponse
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
        bookings=[BookingCreateResponse.model_validate(b.model_dump()) for b in bookings]
    )


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking_endpoint(
    booking_data: BookingUpdate,
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    
    update_data = booking_data.model_dump(exclude_unset=True)

    return update_booking(db, booking, update_data)


@router.put("/{booking_id}/cancel", status_code=204)
def cancel_booking_endpoint(
    current_user: User = Depends(require_roles("regular", "admin")),
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    cancelled_by_role = "guest" if current_user.user_type == UserTypes.regular else current_user.user_type.value
    cancel_booking(db, booking, cancelled_by_role=cancelled_by_role)
    return Response(status_code=204)


@router.post("/{booking_id}/cancel-by-business", status_code=204)
def cancel_booking_by_business_endpoint(
    payload: BusinessBookingCancelRequest,
    current_user: User = Depends(require_roles("business", "employee", "admin")),
    booking: Booking = Depends(require_booking_listing_manager),
    db: Session = Depends(get_db),
):
    reason = payload.reason.strip()
    if not reason:
        raise HTTPException(status_code=400, detail="Cancellation reason is required")
    cancel_booking(
        db,
        booking,
        cancelled_by_role=current_user.user_type.value,
        cancellation_reason=reason,
    )
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
