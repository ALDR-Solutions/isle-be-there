"""Business logic for businesses."""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.business import Business
from app.models.listing import Listing


def list_businesses(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    verified_only: bool = False,
):
    query = select(Business)
    if verified_only:
        query = query.where(Business.is_verified == True)

    businesses = db.exec(query.order_by(Business.business_name).offset(skip).limit(limit)).all()
    return [business.model_dump() for business in businesses]


def get_business_by_id(db: Session, business_id: str):
    business = db.exec(select(Business).where(Business.id == business_id)).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business.model_dump()




def create_business(db: Session, data: dict, user_id: str):
    existing = db.exec(select(Business).where(Business.user_id == user_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already has a business")

    data["user_id"] = user_id
    business = Business(**data)
    db.add(business)
    db.commit()
    db.refresh(business)
    return business.model_dump()


def update_business(
    db: Session,
    business_id: str,
    update_data: dict,
    user_id: str,
    is_admin: bool = False,
):
    business = db.exec(select(Business).where(Business.id == business_id)).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if not is_admin and str(business.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    for key, value in update_data.items():
        setattr(business, key, value)
    db.commit()
    db.refresh(business)
    return business.model_dump()
