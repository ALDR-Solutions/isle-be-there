"""Review service - business logic for reviews."""
from typing import Optional, List
from uuid import UUID
from sqlmodel import Session, select

from app.models.review import Review
from app.models.listing import Listing
from app.models.booking import Booking
from app.services.review_classifier import classify_review


class ReviewError(Exception):
    """Custom exception for review errors."""
    pass


def validate_can_review(db: Session, user_id: UUID, listing_id: UUID) -> tuple[bool, str]:
    """
    Validate user can review a listing.
    Checks: completed booking exists + hasn't already reviewed.
    """
    # Check for completed booking
    booking = db.exec(
        select(Booking)
        .where(Booking.user_id == user_id)
        .where(Booking.listing_id == listing_id)
        .where(Booking.status == "completed")
    ).first()
    
    if not booking:
        return False, "You can only review after completing a booking"
    
    # Check hasn't already reviewed
    existing = db.exec(
        select(Review)
        .where(Review.listing_id == listing_id)
        .where(Review.user_id == user_id)
    ).first()
    
    if existing:
        return False, "You already reviewed this listing"
    
    return True, ""


def create_review_with_classification(
    db: Session,
    user_id: UUID,
    listing_id: UUID,
    rating: int,
    comment: Optional[str],
    listing: Listing
) -> Review:
    """Create a review with ML classification."""
    review = Review(
        listing_id=listing_id,
        user_id=user_id,
        rating=rating,
        comment=comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    
    if comment and listing.business_type:
        try:
            result = classify_review(
                text=comment,
                business_type_uuid=str(listing.business_type),
                hotel_name=listing.title
            )
            if result and "error" not in result:
                review.auto_labels = {
                    "main_label": result.get("main_label"),
                    "second_label": result.get("second_label"),
                    "third_label": result.get("third_label"),
                    "detected_language": result.get("detected_language"),
                }
                review.detected_language = result.get("detected_language")
                db.add(review)
                db.commit()
                db.refresh(review)
        except Exception as e:
            print(f"Classification failed: {e}")
    
    return review


def get_reviews_for_listing(
    db: Session,
    listing_id: UUID,
    filter_label: Optional[str] = None
) -> List[Review]:
    """Get reviews for a listing with optional label filtering."""
    query = select(Review).where(Review.listing_id == listing_id)
    
    if filter_label:
        query = query.where(Review.auto_labels != None)
    
    reviews = db.exec(query.order_by(Review.created_at.desc())).all()
    
    if filter_label:
        reviews = [
            r for r in reviews 
            if r.auto_labels and (
                r.auto_labels.get("main_label") == filter_label or
                r.auto_labels.get("second_label") == filter_label or
                r.auto_labels.get("third_label") == filter_label
            )
        ]
    
    return reviews
