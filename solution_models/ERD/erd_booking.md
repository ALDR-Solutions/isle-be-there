# Isle Be There - Booking Function ERD

```plantuml
@startuml Booking_Function
skinparam linetype ortho

top to bottom direction

skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

title Booking Function - Entity Relationship Diagram

entity bookings {
  *id : uuid
  created_at : timestamptz
  user_id : uuid
  service_id : uuid
  service_slot_id : int
  itinerary_item_id : uuid
  status : booking_statuses
  booking_from_time : timestamp
  booking_to_time : timestamp
  updated_at : timestamptz
  amount_of_people : int
  special_requests : text
  bookers_name : text
  cancellation_reason : text
  cancelled_by_role : text
  cancelled_at : timestamptz
  base_price : numeric
  service_fee_percent : numeric
  service_fee_amount : numeric
  discount_percent : numeric
  discount_amount : numeric
  display_price : numeric
  final_price : numeric
  stripe_payment_intent_id : text
}

entity payment_events {
  *id : uuid
  booking_id : uuid
  stripe_payment_intent_id : text
}

entity services {
  *service_id : uuid
  capacity : smallint
  availability : jsonb
  listing_id : uuid
}

entity service_slots {
  *id : int
  service_id : uuid
}


entity users {
  *id : uuid
  user_type : user_types
}

entity itinerary_items {
  *id : uuid
  itinerary_id : uuid
  listing_id : uuid
  linked_booking_id : uuid
}

entity itineraries {
  *id : uuid
  user_id : uuid
}


users ||--o bookings
services ||--o bookings
service_slots ||--o bookings
services ||--o service_slots
itinerary_items ||--o bookings
itinerary_items ||--o itineraries
users ||--o itineraries
bookings ||--o payment_events

@enduml
```

## Entity Summary

### Primary Entities

| Entity | Description |
|--------|-------------|
| bookings | Core booking record with pricing, timing, status, and payment info |
| payment_events | Stripe payment lifecycle events tied to a booking |
| services | Service offerings that can be booked |
| service_slots | Available time slots for a service |

### Supporting Entities

| Entity | Description |
|--------|-------------|
| users | The user making the booking |
| listings | Business listings that contain services |
| itinerary_items | Optional link between booking and itinerary |
| itineraries | Users trip plan containing multiple items |
| discounts | Discount rules that can apply to bookings |
| pricing_configs | Service fee percentage by business type |
| business_types | Category of business for pricing configuration |

## Booking Flow

Users makes bookings for services that are contained in listings and scheduled via service_slots.

## Pricing Calculation

display_price = base_price
service_fee_amount = base_price * service_fee_percent
discount_amount = display_price * discount_percent
final_price = display_price + service_fee_amount - discount_amount

## Status Flow

pending - confirmed - completed
cancelled (with cancellation_reason, cancelled_by_role, cancelled_at)
