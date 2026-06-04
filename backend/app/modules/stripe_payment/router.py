"""Router for stripe payment module."""

from uuid import UUID

import stripe
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.infrastructure.database import get_db
from app.modules.bookings.models import Booking, BookingStatus, PaymentEvent
from app.modules.users.models import User
from app.modules.stripe_payment.service import process_refund
from app.shared.dependencies.permissions import require_roles


router = APIRouter(prefix="/api/stripe_payment", tags=["stripe_payment"])


@router.post("/payments/webhook", include_in_schema=False)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        webhook_secret = settings.require_stripe_webhook_secret()
    except RuntimeError as exc:
        raise HTTPException(500, "Webhook secret not configured") from exc

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    # Handle payment_intent.succeeded
    if event.type == "payment_intent.succeeded":
        booking_id = event.data.object["metadata"].get("booking_id")
        if booking_id:
            # Idempotency check
            existing = db.exec(
                select(PaymentEvent).where(
                    PaymentEvent.stripe_payment_intent_id == event.data.object["id"]
                )
            ).first()
            if existing:
                return {"received": True}

            booking = db.get(Booking, UUID(booking_id))
            if booking:
                booking.status = BookingStatus.approved
                db.add(booking)

                payment_event = PaymentEvent(
                    booking_id=booking.id,
                    event_type="payment_intent.succeeded",
                    stripe_payment_intent_id=event.data.object["id"],
                    amount_cents=event.data.object["amount"],
                )
                db.add(payment_event)
                db.commit()

    # Handle payment_intent.payment_failed
    elif event.type == "payment_intent.payment_failed":
        booking_id = event.data.object["metadata"].get("booking_id")
        if booking_id:
            payment_event = PaymentEvent(
                booking_id=UUID(booking_id),
                event_type="payment_intent.payment_failed",
                stripe_payment_intent_id=event.data.object["id"],
                amount_cents=event.data.object["amount"],
            )
            db.add(payment_event)
            db.commit()

    # Handle charge.refunded
    elif event.type == "charge.refunded":
        payment_intent_id = event.data.object.get("payment_intent")
        if payment_intent_id:
            # Idempotency check - look for existing refund.completed for this payment intent
            existing = db.exec(
                select(PaymentEvent).where(
                    PaymentEvent.stripe_payment_intent_id == payment_intent_id,
                    PaymentEvent.event_type == "refund.completed",
                )
            ).first()
            if existing:
                return {"received": True}

            # Find booking by payment intent
            booking = db.exec(
                select(Booking).where(
                    Booking.stripe_payment_intent_id == payment_intent_id
                )
            ).first()

            if booking:
                # Create refund.completed event
                payment_event = PaymentEvent(
                    booking_id=booking.id,
                    event_type="refund.completed",
                    stripe_payment_intent_id=payment_intent_id,
                    amount_cents=event.data.object.get("amount_refunded"),
                )
                db.add(payment_event)
                db.commit()

    return {"received": True}


@router.get("/admin/refunds")
def list_refunds(
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    """List all refund-related payment events."""
    refunds = db.exec(
        select(PaymentEvent).where(
            PaymentEvent.event_type.like("refund.%")
        ).order_by(PaymentEvent.created_at.desc())
    ).all()
    return refunds


@router.post("/admin/refunds/{booking_id}/manual")
def manual_refund(
    booking_id: UUID,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    """Manually trigger a refund for a booking."""
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")

    result = process_refund(db, booking)
    if not result.get("success"):
        raise HTTPException(400, f"Refund failed: {result.get('error')}")

    return {"status": "refund_initiated", "booking_id": str(booking_id)}
