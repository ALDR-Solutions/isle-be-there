# Bookings Module - Class Diagram (PlantUML)

```plantuml
@startuml BookingsModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

title Booking Module - Class Diagram
' =========================
' BOOKINGS MODULE - MODELS ONLY
' =========================

class Booking {
    +id: UUID PK
    +service_id: UUID FK
    +service_slot_id: int FK (nullable)
    +booking_from_time: datetime
    +booking_to_time: datetime
    +status: BookingStatus
    +user_id: UUID FK
    +created_at: datetime
    +updated_at: datetime
    +amount_of_people: int
    +special_requests: str
    +bookers_name: str
    +cancellation_reason: str (nullable)
    +cancelled_by_role: str (nullable)
    +cancelled_at: datetime (nullable)
    +base_price: float
    +service_fee_percent: float
    +service_fee_amount: float
    +discount_percent: float
    +discount_amount: float
    +display_price: float
    +final_price: float
    +itinerary_item_id: UUID FK (nullable)
    +stripe_payment_intent_id: str
    --
    +list_bookings(db, user_id): list[BookingResponse]
    +get_booking_by_id(db, booking_id, user_id): BookingResponse
    +list_bookings_for_listing(db, listing_id): list[BookingResponse]
    +create_booking(db, booking, user_id): Booking
    +create_bulk_bookings(db, items, user_id): list[Booking]
    +update_booking(db, booking, update_data): Booking
    +cancel_booking(db, booking, cancelled_by_role, cancellation_reason): Booking
    +delete_booking(db, booking): None
    +create_payment_intent(db, booking_id, user_id): dict
    +price_booking_by_id(db, booking_id, user_id): dict
    +check_booking_conflict(db, service_id, from_time, to_time, exclude_booking_id): bool
    +update_expired_bookings(db): dict
}

enum BookingStatus {
    pending
    cancelled
    approved
    completed
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' User (from users module) - Who made the booking
class User {
    +id: UUID PK
    +email: str
}

' Service (from services module) - What is being booked
class Service {
    +service_id: UUID PK
    +name: str
    +capacity: int
    +listing_id: UUID FK
}

' Listing (from listings module) - Parent of service
class Listing {
    +id: UUID PK
    +title: str
}

' ItineraryItem (from itineraries module) - Optional link to itinerary
class ItineraryItem {
    +id: UUID PK
    +itinerary_id: UUID FK
    +listing_id: UUID FK
}

' PaymentEvent (from stripe_payment module) - Payment events for booking
class PaymentEvent {
    +id: UUID PK
    +booking_id: UUID FK
    +event_type: str
    +amount_cents: int
    +created_at: datetime
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' User books Services (1-to-many)
User "1" --> "0..*" Booking : books

' Service is booked via Bookings (1-to-many)
Service "1" --> "0..*" Booking : booked_in

' Booking uses BookingStatus enum
Booking --> BookingStatus : <<uses>>

' Booking optionally linked from ItineraryItem (0..1-to-1)
ItineraryItem "0..1" --> "1" Booking : books

' Booking generates PaymentEvents (1-to-many)
Booking "1" --> "0..*" PaymentEvent : generates

@enduml
```

## Bookings Module - Models Only

This diagram shows only the models within the Bookings module and how it connects to other modules via models.

| Model             | Description                    |
| ----------------- | ------------------------------ |
| **Booking**       | Reservation for a service      |
| **BookingStatus** | Enum for booking status states |

## Internal Relationships

| Relationship            | Description                                        |
| ----------------------- | -------------------------------------------------- |
| Booking → BookingStatus | Booking status is determined by BookingStatus enum |

## Cross-Module Connections

The Bookings module connects to other modules:

| Connected Module   | Via Model     | Relationship                                                       |
| ------------------ | ------------- | ------------------------------------------------------------------ |
| **users**          | User          | User books services (user_id FK in Booking)                        |
| **services**       | Service       | Booking books Service (service_id FK in Booking)                   |
| **listings**       | Listing       | Service belongs to Listing (via Service.listings_id FK)            |
| **itineraries**    | ItineraryItem | ItineraryItem can link to Booking (itinerary_item_id FK, nullable) |
| **stripe_payment** | PaymentEvent  | Booking generates PaymentEvents (booking_id FK)                    |

## Booking Status Flow

```
    [pending]
        |
        +-----> [approved] -----> [completed]
        |              |
        v              v
    [cancelled]   [cancelled]
```

## Key Model Attributes

### Booking

- `id: UUID` - Primary key
- `service_id: UUID` - Foreign key to Service being booked
- `service_slot_id: int` - Foreign key to specific time slot (nullable)
- `user_id: UUID` - Foreign key to User making the booking
- `booking_from_time: datetime` - Start of booking
- `booking_to_time: datetime` - End of booking
- `amount_of_people: int` - Number of people
- `status: BookingStatus` - Current status enum (pending, approved, cancelled, completed)
- `itinerary_item_id: UUID` - Optional link to ItineraryItem (for package discounts)
- `bookers_name: str` - Name of the person booking
- `special_requests: str` - Special requests or notes
- `cancellation_reason: str` - Reason for cancellation (set when cancelled)
- `cancelled_by_role: str` - Who cancelled (user/business/admin)
- `cancelled_at: datetime` - When booking was cancelled
- `base_price: float` - Base price before fees
- `service_fee_percent: float` - Platform fee percentage
- `service_fee_amount: float` - Calculated platform fee
- `discount_percent: float` - Discount percentage applied
- `discount_amount: float` - Discount amount applied
- `display_price: float` - Price shown to user before discount
- `final_price: float` - Final price after fees and discounts
- `stripe_payment_intent_id: str` - Stripe payment intent reference
