# Itineraries Module - Class Diagram with Operations (PlantUML)

```plantuml
@startuml ItinerariesModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle


title Itineraries Module - Class Diagram
' =========================
' ITINERARIES MODULE - MODELS WITH OPERATIONS
' =========================

class Itinerary {
    +id: UUID PK
    +user_id: UUID FK
    +title: str
    +start_date: date
    +end_date: date
    +status: ItineraryStatus
    +budget_level: str
    +pace: str
    +country: str
    +interests: dict
    +total_estimated_cost: float
    +created_at: datetime
    +updated_at: datetime
    +applied_discount_id: int (nullable)
    +discount_amount: float (nullable)
    --
    +list_saved_itineraries(db, user_id): list[SavedItinerarySummaryResponse]
    +get_saved_itinerary(db, user_id, itinerary_id): SavedItineraryResponse
    +create_itinerary(db, user_id, data): Itinerary
    +save_itinerary(db, user_id, itinerary_id, data): Itinerary
    +confirm_itinerary(db, user_id, itinerary_id): Itinerary
    +delete_saved_itinerary(db, user_id, itinerary_id): None
    +convert_itinerary_to_bookings(db, user_id, itinerary_id): list[Booking]
    +plan_itinerary(db, user_id, data): PlanItineraryResponse
    +send_saved_itinerary_email(user_id, itinerary_id): None
    +send_unsaved_itinerary_email(user_id, data): None
}

enum ItineraryStatus {
    DRAFT
    SAVED
    CONFIRMED
    CANCELLED
    COMPLETED
    ARCHIVED
}

class ItineraryItem {
    +id: UUID PK
    +itinerary_id: UUID FK
    +listing_id: UUID FK
    +linked_booking_id: UUID FK (nullable)
    +title: str
    +description: str
    +day_date: date
    +start_at: datetime
    +end_at: datetime
    +sort_order: int
    +estimated_cost: float
    +address_snapshot: dict
    +reason_tags: dict
    +extra_metadata: dict
    +created_at: datetime
    +updated_at: datetime
    --
    +build_items_for_saved_itinerary(db, itinerary): list[ItineraryItem]
    +serialize_saved_itinerary(itinerary, items): dict
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' User (from users module) - Who created the itinerary
class User {
    +id: UUID PK
    +email: str
}

' Listing (from listings module) - Referenced by items
class Listing {
    +id: UUID PK
    +title: str
}

' Booking (from bookings module) - Booked from itinerary item
class Booking {
    +id: UUID PK
    +status: BookingStatus
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' User creates Itineraries (1-to-many)
User "1" --> "0..*" Itinerary : creates

' Itinerary contains ItineraryItems (composition - 1-to-many)
Itinerary "1" *-- "0..*" ItineraryItem : contains

' Itinerary uses ItineraryStatus enum
Itinerary --> ItineraryStatus : <<uses>>

' Listing is referenced by ItineraryItems (1-to-many)
Listing "1" --> "0..*" ItineraryItem : referenced_by

' ItineraryItem optionally books a Booking (0..1-to-1)
ItineraryItem "0..1" *-- "1" Booking : books

@enduml
```

## Itineraries Module - Models with Operations

This diagram shows the Itineraries module models and their operations.

| Model               | Description                             |
| ------------------- | --------------------------------------- |
| **Itinerary**       | User's planned trip                     |
| **ItineraryItem**   | Individual stop/booking in an itinerary |
| **ItineraryStatus** | Enum for itinerary status               |

## Cross-Module Connections

The Itineraries module connects to other modules:

| Connected Module | Via Model | Relationship                                                       |
| ---------------- | --------- | ------------------------------------------------------------------ |
| **users**        | User      | User creates Itineraries (user_id FK)                              |
| **listings**     | Listing   | ItineraryItem references Listing (listing_id FK)                   |
| **bookings**     | Booking   | ItineraryItem can link to Booking (linked_booking_id FK, nullable) |

## Itinerary Lifecycle

```
    [DRAFT] --> [SAVED] --> [CONFIRMED] --> [COMPLETED]
       |           |            |
       v           v            v
    [ARCHIVED] [CANCELLED]  [CANCELLED]
```

## Key Model Attributes

### Itinerary

- `id: UUID` - Primary key
- `user_id: UUID` - Foreign key to User (creator)
- `title: str` - Itinerary title
- `start_date: date` - Trip start date
- `end_date: date` - Trip end date
- `status: ItineraryStatus` - Current status enum (DRAFT, SAVED, CONFIRMED, CANCELLED, COMPLETED, ARCHIVED)
- `budget_level: str` - Budget level
- `pace: str` - Pace preference
- `country: str` - Destination country
- `interests: dict` - User's interests for this trip
- `total_estimated_cost: float` - Running total of estimated costs
- `applied_discount_id: int` - Applied package discount (if any)
- `discount_amount: float` - Amount discounted

### ItineraryItem

- `id: UUID` - Primary key
- `itinerary_id: UUID` - Foreign key to parent Itinerary
- `listing_id: UUID` - Foreign key to referenced Listing
- `linked_booking_id: UUID` - Optional link to Booking (set when item is converted to booking)
- `day_date: date` - Date for this item
- `start_at: datetime` - Start time
- `end_at: datetime` - End time
- `sort_order: int` - Order within the itinerary
- `estimated_cost: float` - Estimated price
- `address_snapshot: dict` - Snapshot of listing address at time of planning
- `reason_tags: dict` - Tags explaining why this item was recommended
- `extra_metadata: dict` - Additional item-specific data
