# Isle Be There - Itinerary Function ERD

```plantuml
@startuml Itinerary_Function
hide circle
skinparam linetype ortho

title Itinerary Function - Entity Relationship Diagram

entity itineraries {
  *id : uuid
  user_id : uuid
  title : text
  start_date : date
  end_date : date
  status : itinerary_statuses
  budget_level : text

  pace : text
  country : text
  interests : jsonb
  total_estimated_cost : float
  created_at : timestamptz
  updated_at : timestamptz
  applied_discount_id : int
  discount_amount : numeric
}

entity itinerary_items {
  *id : uuid
  itinerary_id : uuid
  listing_id : uuid
  linked_booking_id : uuid
  title : text
  description : text
  day_date : date
  start_at : timestamp
  end_at : timestamp
  sort_order : int
  estimated_cost : float
  address_snapshot : jsonb
  reason_tags : jsonb
  extra_metadata : jsonb
  created_at : timestamptz
  updated_at : timestamptz
}

entity users {
  *id : uuid
  user_type : user_types
}

entity listings {
  *id : uuid
  business_id : uuid
  title : text
  description : text
  address : jsonb
  base_price : numeric
  business_type : uuid
}

entity bookings {
  *id : uuid
  created_at : timestamptz
  user_id : uuid
  service_id : uuid
  service_slot_id : int
  itinerary_item_id : uuid
  status : booking_statuses
  stripe_payment_intent_id : text
}

users ||--o{ itineraries 
itineraries ||--o{ itinerary_items 
itinerary_items ||--o{ listings 
itinerary_items ||--o{ bookings 
bookings ||--o{ users 

@enduml
```

## Entity Summary

### Core Entities

| Entity | Description |
|--------|-------------|
| itineraries | User trip plan with dates, budget, and preferences |
| itinerary_items | Individual items/activities in an itinerary |

### Supporting Entities

| Entity | Description |
|--------|-------------|
| users | User who creates and owns the itinerary |
| listings | Business listings referenced by itinerary items |
| bookings | Bookings linked from itinerary items |

## Itinerary Flow

Users create itineraries and add items to them. Each item can reference a listing and optionally link to a booking.

## Status Flow

Itinerary status: draft - planned - in_progress - completed
Item status: pending - confirmed - cancelled

## PlantUML Legend

| Symbol | Meaning |
|--------|---------|
| ||--o{ | One-to-Many |
| }o--|| | Many-to-One |
| * | Primary Key |