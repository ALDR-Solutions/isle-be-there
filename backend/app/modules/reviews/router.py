from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_review_owner, require_roles

from .keyword_classifier import BUSINESS_TYPE_UUIDS, check_flags, classify_with_keywords
from .review_classifier import classify_review as ml_classify_review
from .models import Review
from .schemas import ReviewClassifyRequest, ReviewClassifyResponse, ReviewCreate, ReviewUpdate, ReviewSubmitRequest, ReviewSubmitResponse, ReviewVisibilityUpdate
from .service import delete_review, get_review, list_reviews, submit_review, toggle_review_visibility, update_review

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get("", response_model=list[dict])
def get_reviews(
    listing_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_reviews(db, listing_id)


@router.post("/submit", response_model=ReviewSubmitResponse, status_code=201)
def submit_review_route(
    review_request: ReviewSubmitRequest,
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    """Submit a review with automatic classification.
    
    - Classifies the review text using keyword-based (Events/Tours/Services)
      or ML-based (Hotel/Restaurant) classification
    - Checks for inappropriate content (profanity, hate speech, spam, personal attacks)
    - Returns review with classification labels and flag status
    """
    # Build a ReviewCreate-compatible object from review_request
    review_create_payload = ReviewCreate(
        listing_id=review_request.listing_id,
        rating=review_request.rating,
        comment=review_request.comment,
    )
    
    return submit_review(
        db=db,
        user_id=current_user.id,
        review_request=review_create_payload,
        business_type_uuid=review_request.business_type_uuid,
        hotel_name=review_request.hotel_name,
    )


@router.put("/{review_id}", response_model=dict)
def update_review_route(
    review_id: int,
    review_request: ReviewUpdate,
    review: Review = Depends(require_review_owner),
    db: Session = Depends(get_db),
):
    return update_review(db, review, review_request)


@router.delete("/{review_id}", status_code=204)
def delete_review_route(
    review_id: int,
    review: Review = Depends(require_review_owner),
    db: Session = Depends(get_db),
):
    delete_review(db, review)
    return None


@router.patch("/{review_id}/visibility", response_model=dict)
def toggle_review_visibility_route(
    review_id: int,
    review_request: ReviewVisibilityUpdate,
    current_user: User = Depends(require_roles("admin")),  # Admin only
    db: Session = Depends(get_db),
):
    """Toggle review visibility (admin only).
    
    Allows admins to hide/show flagged reviews.
    """
    # Get review (must exist)
    review = db.exec(select(Review).where(Review.id == review_id)).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return toggle_review_visibility(
        db=db,
        review=review,
        is_visible=review_request.is_visible,
    )


@router.post("/classify", response_model=ReviewClassifyResponse)
def classify_review_route(
    review_request: ReviewClassifyRequest,
):
    """Classify a review text using keyword-based or ML-based classification.

    - Events/Tours/Services: Uses keyword-based classification
    - Hotel/Restaurant: ML-based classification (placeholder - returns not implemented)

    All reviews are checked for inappropriate content (profanity, hate speech, spam, personal attacks).
    """
    # First check for flags (applies to ALL business types)
    flag_result = check_flags(review_request.text)

    # Get keyword-based business type UUIDs
    events_uuid = BUSINESS_TYPE_UUIDS["events"]
    tours_uuid = BUSINESS_TYPE_UUIDS["tours"]
    services_uuid = BUSINESS_TYPE_UUIDS["services"]

    # Route to appropriate classifier based on business type
    if review_request.business_type_uuid in [events_uuid, tours_uuid, services_uuid]:
        # Keyword-based classification for Events, Tours, Services
        result = classify_with_keywords(review_request.text, review_request.business_type_uuid)
        return ReviewClassifyResponse(
            business_type_id=result["business_type_id"],
            business_type=result["business_type"],
            hotel_name=review_request.hotel_name,
            main_label=result["main_label"],
            second_label=result["second_label"],
            third_label=result["third_label"],
            is_flagged=flag_result["is_flagged"],
            flag_reason=flag_result["reason"],
        )
    else:
        # ML classification for Hotel/Restaurant
        try:
            ml_result = ml_classify_review(
                text=review_request.text,
                business_type_uuid=review_request.business_type_uuid,
                hotel_name=review_request.hotel_name,
                verbose=False
            )
            
            # Handle case where ML returns error or None labels
            main_label = ml_result.get('main_label') or '(none)'
            second_label = ml_result.get('second_label') or '(none)'
            third_label = ml_result.get('third_label') or '(none)'
            
            # Map business_type_id to string UUID if needed
            if ml_result.get('business_type') == 'Hotel':
                business_type_id = BUSINESS_TYPE_UUIDS["hotel"]
            elif ml_result.get('business_type') == 'Restaurant':
                business_type_id = BUSINESS_TYPE_UUIDS["restaurant"]
            else:
                business_type_id = review_request.business_type_uuid
            
            return ReviewClassifyResponse(
                business_type_id=business_type_id,
                business_type=ml_result.get('business_type', 'Hotel'),
                hotel_name=review_request.hotel_name,
                main_label=main_label,
                second_label=second_label,
                third_label=third_label,
                is_flagged=flag_result["is_flagged"],
                flag_reason=flag_result["reason"],
            )
        except Exception as e:
            # Fallback on error - still return flags
            return ReviewClassifyResponse(
                business_type_id=review_request.business_type_uuid,
                business_type="Hotel" if review_request.business_type_uuid == BUSINESS_TYPE_UUIDS["hotel"] else "Restaurant",
                hotel_name=review_request.hotel_name,
                main_label="(error)",
                second_label="(error)",
                third_label="(error)",
                is_flagged=flag_result["is_flagged"],
                flag_reason=flag_result["reason"],
            )
