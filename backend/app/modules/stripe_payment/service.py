"""Service for stripe payment module."""

from uuid import UUID

import stripe
from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.modules.bookings.models import Booking, BookingStatus, PaymentEvent
from app.modules.services.models import Service


def create_payment_intent(db: Session, booking_id: UUID, user_id: UUID) -> dict:
    """
    Create a Stripe Payment Intent for a booking.

    Returns dict with client_secret on success.
    Raises HTTPException if booking not found, not owned by user, not pending,
    or final_price < 0.50.
    """
    # Retrieve booking
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Verify user owns the booking
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this booking")

    # Verify booking is pending
    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=400, detail="Booking is not in pending status")

    # Verify slot availability BEFORE creating payment intent
    if booking.service_id and booking.booking_from_time and booking.booking_to_time:
        service = db.get(Service, booking.service_id)
        if service and service.capacity:
            from app.modules.availability.service import is_available as availability_is_available

            still_available = availability_is_available(
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

    # Verify final_price >= 0.50 (recalculate if None or seems incorrect)
    # Import and use price_booking_by_id to ensure correct price calculation
    if booking.final_price is None or booking.final_price < 0.50:
        from app.modules.bookings.service import price_booking_by_id
        try:
            recalculated = price_booking_by_id(db, booking_id, user_id)
            booking.base_price = recalculated["base_price"]
            booking.service_fee_percent = recalculated["service_fee_percent"]
            booking.service_fee_amount = recalculated["service_fee_amount"]
            booking.discount_percent = recalculated["discount_percent"]
            booking.discount_amount = recalculated["discount_amount"]
            booking.display_price = recalculated["display_price"]
            booking.final_price = recalculated["final_price"]
            db.add(booking)
            db.commit()
        except Exception as e:
            # If recalculation fails, fall back to simple calculation
            base = float(booking.base_price or 0)
            fee = float(booking.service_fee_amount or 0)
            discount = float(booking.discount_amount or 0)
            calculated_final = base + fee - discount
            if calculated_final < 0.50:
                raise HTTPException(status_code=400, detail="Booking final price must be at least $0.50")
            booking.final_price = calculated_final
            db.add(booking)
            db.commit()
    
    if booking.final_price < 0.50:
        raise HTTPException(status_code=400, detail="Booking final price must be at least $0.50")

    # Get Stripe key
    try:
        stripe_secret_key = settings.require_stripe_secret_key()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail="Stripe is not configured") from exc

    # Create Stripe Payment Intent
    stripe.api_key = stripe_secret_key
    amount_cents = int(booking.final_price * 100)

    payment_intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency="usd",
        metadata={"booking_id": str(booking_id)},
        automatic_payment_methods={"enabled": True},
    )

    # Store payment intent ID on booking
    booking.stripe_payment_intent_id = payment_intent.id
    db.add(booking)

    # Create PaymentEvent record
    payment_event = PaymentEvent(
        booking_id=booking_id,
        event_type="payment_intent.created",
        stripe_payment_intent_id=payment_intent.id,
        amount_cents=amount_cents,
    )
    db.add(payment_event)

    db.commit()
    db.refresh(booking)

    return {"client_secret": payment_intent.client_secret}


def process_refund(db: Session, booking: Booking) -> dict:
    """
    Process a full refund for a booking via Stripe.

    Returns dict with:
        - success: bool
        - refund_id: str (if successful)
        - already_processed: bool (if already refunded)
        - error: str (if failed)
    """
    # 1. Idempotency check - look for existing refund.initiated or refund.completed
    existing = db.exec(
        select(PaymentEvent).where(
            PaymentEvent.booking_id == booking.id,
            PaymentEvent.event_type.in_(["refund.initiated", "refund.completed"]),
        )
    ).first()

    if existing:
        return {"success": True, "already_processed": True}

    # 2. Get Stripe key
    try:
        stripe_secret_key = settings.require_stripe_secret_key()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail="Stripe is not configured") from exc

    # 3. Create Stripe refund
    stripe.api_key = stripe_secret_key
    refund = stripe.Refund.create(payment_intent=booking.stripe_payment_intent_id)

    # 4. Create PaymentEvent
    payment_event = PaymentEvent(
        booking_id=booking.id,
        event_type="refund.initiated",
        stripe_payment_intent_id=booking.stripe_payment_intent_id,
        amount_cents=refund.amount,
    )
    db.add(payment_event)
    db.commit()

    return {"success": True, "refund_id": refund.id, "amount_cents": refund.amount}


def confirm_payment(db: Session, booking: "Booking") -> dict:
    """
    Confirm payment was successful via Stripe API and update booking status.
    Used by bookings router to delegate payment confirmation to stripe_payment module.
    """
    import stripe as stripe_lib
    from app.modules.bookings.models import BookingStatus
    from app.modules.stripe_payment.models import PaymentEvent

    # Check if payment intent was created for this booking
    if not booking.stripe_payment_intent_id:
        return {"success": False, "error": "No payment initiated for this booking. Call /payment-intent first."}

    # Get Stripe key and verify payment intent status
    try:
        stripe_secret_key = settings.require_stripe_secret_key()
    except RuntimeError:
        return {"success": False, "error": "Stripe is not configured"}

    try:
        stripe_lib.api_key = stripe_secret_key
        payment_intent = stripe_lib.PaymentIntent.retrieve(booking.stripe_payment_intent_id)
    except stripe_lib.error.InvalidRequestError:
        return {"success": False, "error": "Payment intent not found"}

    if payment_intent.status != "succeeded":
        return {"success": False, "error": "Payment not yet completed or failed"}

    # Verify slot availability before confirming (dates may have been taken since payment intent created)
    from app.modules.services.models import Service
    if booking.service_id and booking.booking_from_time and booking.booking_to_time:
        service = db.get(Service, booking.service_id)
        if service and service.capacity:
            from app.modules.availability.service import is_available as check_availability
            still_available = check_availability(
                db,
                booking.service_id,
                service.capacity,
                booking.booking_from_time,
                booking.booking_to_time,
                booking.amount_of_people or 1,
            )
            if not still_available:
                return {"success": False, "error": "The selected time slot is no longer available. Please choose a different time."}

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

    return {"success": True, "status": "approved", "message": "Payment successful"}
