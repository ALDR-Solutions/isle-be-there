from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_roles

from .schemas import CalendarEventResponse
from .service import list_calendar_events

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])


@router.get("", response_model=list[CalendarEventResponse])
def list_calendar_events_endpoint(
    start: datetime | None = None,
    end: datetime | None = None,
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    return list_calendar_events(db, current_user.id, start=start, end=end)
