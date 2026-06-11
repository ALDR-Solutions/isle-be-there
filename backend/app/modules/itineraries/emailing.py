from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.core.email import send_itinerary_email
from app.modules.users.models import User
from app.shared.domain import get_user_or_404

from .persistence import get_saved_itinerary
from .planner import plan_itinerary
from .schemas import ItineraryUnsavedEmailRequest
from .serialization import saved_itinerary_to_plan_response

logger = logging.getLogger(__name__)


def send_saved_itinerary_email(
    db: Session,
    user_id: UUID,
    itinerary_id: UUID,
    recipient_email: Optional[str] = None,
) -> str:
    user = get_user_or_404(db, user_id)

    saved_itinerary = get_saved_itinerary(db, user_id, itinerary_id)
    itinerary_preview = saved_itinerary_to_plan_response(saved_itinerary)
    resolved_email = recipient_email or user.email
    if not resolved_email:
        raise HTTPException(status_code=400, detail="Recipient email is required")

    view_url = f"{settings.resolved_frontend_url}/itinerary/{saved_itinerary.id}"

    try:
        send_itinerary_email(
            resolved_email,
            saved_itinerary.title,
            itinerary_preview,
            country=saved_itinerary.country,
            interests=saved_itinerary.interests,
            view_url=view_url,
        )
    except Exception:
        logger.exception(
            "Failed to send itinerary %s to %s",
            saved_itinerary.id,
            resolved_email,
        )
        raise HTTPException(status_code=502, detail="Failed to send itinerary email")

    return resolved_email


def send_unsaved_itinerary_email(
    db: Session,
    user_id: Optional[UUID],
    payload: ItineraryUnsavedEmailRequest,
) -> str:
    user = None
    if user_id:
        user = db.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    resolved_email = payload.email or (user.email if user else None)
    if not resolved_email:
        raise HTTPException(status_code=400, detail="Recipient email is required")

    itinerary_preview = payload.plan_response or plan_itinerary(
        db,
        payload.plan_request,
        user_id,
    )
    if itinerary_preview.trip_days != payload.plan_request.resolved_trip_days:
        raise HTTPException(
            status_code=400,
            detail="Unsaved itinerary does not match requested trip length",
        )

    itinerary_title = resolved_unsaved_title(payload)

    try:
        send_itinerary_email(
            resolved_email,
            itinerary_title,
            itinerary_preview,
            country=payload.plan_request.country,
            interests=payload.plan_request.interests,
        )
    except Exception:
        logger.exception("Failed to send unsaved itinerary to %s", resolved_email)
        raise HTTPException(status_code=502, detail="Failed to send itinerary email")

    return resolved_email


def resolved_unsaved_title(payload: ItineraryUnsavedEmailRequest) -> str:
    if payload.title and payload.title.strip():
        return payload.title.strip()

    location = payload.plan_request.country or "Trip"
    return f"{location} itinerary"
