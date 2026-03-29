from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import get_current_user

from .schemas import FavouriteResponse
from .service import add_favourite, list_favourites, remove_favourite

router = APIRouter(prefix="/api/favourites", tags=["Favourites"])


@router.get("/", response_model=list[FavouriteResponse], include_in_schema=False)
@router.get("", response_model=list[FavouriteResponse])
def get_favourites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_favourites(db, current_user.id)


@router.post("/{listing_id}", response_model=FavouriteResponse)
def add_favourite_route(
    listing_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return add_favourite(db, current_user.id, listing_id)


@router.delete("/{listing_id}")
def remove_favourite_route(
    listing_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    remove_favourite(db, current_user.id, listing_id)
    return {"detail": "Removed"}
