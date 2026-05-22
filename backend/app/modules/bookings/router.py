from typing import List
import os

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel import Session
from sqlmodel.sql.expression import select

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_booking_owner, require_roles

from .models import Booking, BookingStatus, PaymentEvent
from uuid import UUID
from .schemas import BookingCreate, BookingCreateResponse, BookingUpdate, BookingResponse, BookingPriceResponse, BulkBookingCreateRequest, BulkBookingCreateResponse, PaymentIntentResponse
from .service import (
    cancel_booking,
    create_booking,
    create_bulk_bookings,
    create_payment_intent,
    delete_booking,
    get_booking_by_id,
    list_bookings,
    update_booking,
    price_booking_by_id,
)
from app.modules.availability.service import is_available as check_availability
from app.modules.services.models import Service

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])




@router.get("", response_model=List[BookingResponse])
def get_bookings(
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    return list_bookings(db, current_user.id)


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
    # Check if payment intent was created for this booking
    if not booking.stripe_payment_intent_id:
        raise HTTPException(
            status_code=400,
            detail="No payment initiated for this booking. Call /payment-intent first."
        )

    # Get Stripe key and verify payment intent status
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    try:
        payment_intent = stripe.PaymentIntent.retrieve(booking.stripe_payment_intent_id)
    except stripe.error.InvalidRequestError:
        raise HTTPException(status_code=404, detail="Payment intent not found")

    if payment_intent.status != "succeeded":
        raise HTTPException(
            status_code=400,
            detail="Payment not yet completed or failed"
        )

    # Verify slot availability before confirming (dates may have been taken since payment intent created)
    if booking.service_id and booking.booking_from_time and booking.booking_to_time:
        service = db.get(Service, booking.service_id)
        if service and service.capacity:
            still_available = check_availability(
                db,
                booking.service_id,
                service.capacity,
                booking.booking_from_time,
                booking.booking_to_time,
                booking.amount_of_people or 1,
            )
            if not still_available:
                raise HTTPException(
                    status_code=409,
                    detail="The selected time slot is no longer available. Please choose a different time."
                )

    # Update booking status to approved
    booking.status = BookingStatus.approved
    db.add(booking)

    # Create PaymentEvent record
    payment_event = PaymentEvent(
        booking_id=booking.id,
        event_type="payment_intent.confirmed",
        stripe_payment_intent_id=payment_intent.id,
        amount_cents=payment_intent.amount,
    )
    db.add(payment_event)
    db.commit()
    db.refresh(booking)

    return {"status": "approved", "message": "Payment successful"}


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


@router.post("/payments/webhook", include_in_schema=False)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(500, "Webhook secret not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    # Check if already processed (idempotency)
    existing = db.exec(
        select(PaymentEvent).where(
            PaymentEvent.stripe_payment_intent_id == event.data.object["id"]
        )
    ).first()
    if existing:
        return {"received": True}

    if event.type == "payment_intent.succeeded":
        booking_id = event.data.object["metadata"].get("booking_id")
        if booking_id:
            booking = db.get(Booking, UUID(booking_id))
            if booking:
                booking.status = BookingStatus.approved
                db.add(booking)

                payment_event = PaymentEvent.model_validate({
                    "booking_id": booking.id,
                    "event_type": "payment_intent.succeeded",
                    "stripe_payment_intent_id": event.data.object["id"],
                    "amount_cents": event.data.object["amount"],
                })
                db.add(payment_event)
                db.commit()

    elif event.type == "payment_intent.payment_failed":
        # Log but booking stays pending
        booking_id = event.data.object["metadata"].get("booking_id")
        if booking_id:
            payment_event = PaymentEvent.model_validate({
                "booking_id": UUID(booking_id),
                "event_type": "payment_intent.payment_failed",
                "stripe_payment_intent_id": event.data.object["id"],
                "amount_cents": event.data.object["amount"],
            })
            db.add(payment_event)
            db.commit()

    return {"received": True}
