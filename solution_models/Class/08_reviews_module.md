# Reviews Module - Class Diagram (PlantUML)

```plantuml
@startuml ReviewsModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

title Reviews Module - Class Diagram
' =========================
' REVIEWS MODULE - MODELS ONLY
' =========================

class Review {
    +id: UUID PK
    +listing_id: UUID FK
    +user_id: UUID FK
    +rating: int
    +comment: str
    +created_at: datetime
    +updated_at: datetime
    +detected_language: str
    +classification_labels: str
    +classified_at: datetime
    +translated_comment: str
    +censored_comment: str
    --
    +list_reviews(db, listing_id, current_user): list[dict]
    +submit_review(db, user_id, review_request): dict
    +update_review(db, review, review_request): dict
    +delete_review(db, review): None
    +create_business_reply(db, review_id, current_user, description): dict
    +get_business_reply(db, review_id): dict | None
    +update_business_reply(db, review_id, current_user, description): dict
    +delete_business_reply(db, review_id, current_user): None
}

class BusinessReply {
    +id: UUID PK
    +created_at: datetime
    +updated_at: datetime
    +business_id: UUID FK
    +user_id: UUID FK
    +review_id: UUID FK
    +description: str
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' User (from users module) - Who wrote the review
class User {
    +id: UUID PK
    +email: str
}

' Listing (from listings module) - Being reviewed
class Listing {
    +id: UUID PK
    +title: str
}

' Business (from businesses module) - Who can reply
class Business {
    +id: UUID PK
    +business_name: str
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' User writes Reviews (1-to-many)
User "1" --> "0..*" Review : writes

' Listing has Reviews (1-to-many)
Listing "1" --> "0..*" Review : has

' Review receives BusinessReply (1-to-0..1)
Review "1" --> "0..1" BusinessReply : receives

' Business writes BusinessReplies (1-to-many)
Business "1" --> "0..*" BusinessReply : writes

@enduml
```

## Reviews Module - Models Only

This diagram shows only the models within the Reviews module and how it connects to other modules via models.

| Model             | Description                   |
| ----------------- | ----------------------------- |
| **Review**        | User review for a listing     |
| **BusinessReply** | Business response to a review |

## Cross-Module Connections

The Reviews module connects to other modules:

| Connected Module | Via Model               | Relationship                                                         |
| ---------------- | ----------------------- | -------------------------------------------------------------------- |
| **users**        | User                    | User writes reviews (user_id FK in Review)                           |
| **listings**     | Listing                 | Listing has reviews (listing_id FK in Review)                        |
| **businesses**   | Business, BusinessReply | Business writes replies to reviews (business_id FK in BusinessReply) |

## Review Classification

Reviews can be classified using ML-based classification:

- `detected_language: str` - Language detected in comment
- `classification_labels: str` - Labels like "positive", "negative", "neutral"
- `translated_comment: str` - Translated text
- `censored_comment: str` - Profanity censored text

## Key Model Attributes

### Review

- `id: UUID` - Primary key
- `listing_id: UUID` - Foreign key to Listing being reviewed
- `user_id: UUID` - Foreign key to User who wrote the review
- `rating: int` - Rating value (1-5)
- `comment: str` - Review text

### BusinessReply

- `id: UUID` - Primary key
- `review_id: UUID` - Foreign key to Review (unique)
- `business_id: UUID` - Foreign key to Business responding
- `user_id: UUID` - Foreign key to User who wrote reply
- `description: str` - Reply text
