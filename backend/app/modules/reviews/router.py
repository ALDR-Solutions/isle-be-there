from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_review_owner, require_roles

from .models import Review
from .schemas import ReviewCreate, ReviewUpdate
from .service import create_review, delete_review, get_review, list_reviews, update_review

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get("", response_model=list[dict])
def get_reviews(
    listing_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_reviews(db, listing_id)


@router.get("/{review_id}", response_model=dict)
def get_review_route(review_id: int, db: Session = Depends(get_db)):
    return get_review(db, review_id)


@router.post("", response_model=dict, status_code=201)
def create_review_route(
    payload: ReviewCreate,
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    return create_review(db, current_user.id, payload)


@router.put("/{review_id}", response_model=dict)
def update_review_route(
    review_id: int,
    payload: ReviewUpdate,
    review: Review = Depends(require_review_owner),
    db: Session = Depends(get_db),
):
    return update_review(db, review, payload)


@router.delete("/{review_id}", status_code=204)
def delete_review_route(
    review_id: int,
    review: Review = Depends(require_review_owner),
    db: Session = Depends(get_db),
):
    delete_review(db, review)
    return None
