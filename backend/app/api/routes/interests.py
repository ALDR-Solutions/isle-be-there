from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database.session import get_db
from app.services.interests_services import get_all_interests, get_user_interests
from app.schemas.interests import InterestResponse

router = APIRouter(prefix="/api/interests", tags=["Interests"])

@router.get("/", response_model=list[InterestResponse])
def get_interests(db: Session = Depends(get_db)):
    """Get all available interests."""
    return get_all_interests(db)
