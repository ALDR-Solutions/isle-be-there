# Availability Module - Class Diagram (PlantUML)

```plantuml
@startuml AvailabilityModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

' =========================
' AVAILABILITY MODULE - MODELS ONLY
' =========================

class ListingHours {
    +id: int PK
    +listing_id: UUID FK
    +day_of_week: int
    +open_time: time
    +close_time: time
    --
    +get_listing_hours(db, listing_id, day): ListingHours | None
    +list_listing_hours(db, listing_id): list[ListingHours]
    +create_listing_hours(db, data): ListingHours
    +update_listing_hours(db, listing_id, day, data): ListingHours
    +delete_listing_hours(db, listing_id, day): None
}

class ServiceSlots {
    +id: int PK
    +service_id: UUID FK
    +day_of_week: int
    +start_time: time
    +end_time: time
    +capacity: int
    --
    +get_service_slot(db, slot_id): ServiceSlots | None
    +get_service_slot_for_service(db, service_id, slot_id): ServiceSlots | None
    +list_service_slots(db, service_id): list[ServiceSlots]
    +create_service_slot(db, data): ServiceSlots
    +update_service_slot(db, service_id, slot_id, data): ServiceSlots
    +delete_service_slot(db, service_id, slot_id): None
    +is_available(db, service_id, capacity, start_dt, end_dt, requested_quantity): bool
    +get_service_availability(db, service_id, date, people): ServiceAvailableResponse
    +get_bulk_service_availability(db, requests): BulkServiceAvailabilityResponse
    +get_mass_availability(db, service_id, start_date, end_date, people): MassAvailabilityResponse
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' Listing (from listings module) - Has operating hours
class Listing {
    +id: UUID PK
    +title: str
}

' Service (from services module) - Has availability slots
class Service {
    +service_id: UUID PK
    +name: str
    +capacity: int
}

' Booking (from bookings module) - Checked for availability
class Booking {
    +id: UUID PK
    +service_id: UUID FK
    +booking_from_time: datetime
    +booking_to_time: datetime
    +amount_of_people: int
    +status: enum
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' Listing has Operating Hours (1-to-many)
Listing "1" --> "0..*" ListingHours : has

' Service has ServiceSlots (1-to-many)
Service "1" --> "0..*" ServiceSlots : has

' ServiceSlots is used to check Booking availability
' (Availability is calculated by counting Bookings within a slot)

@enduml
```

## Availability Module - Models Only

This diagram shows only the models within the Availability module and how it connects to other modules via models.

| Model | Description |
|-------|-------------|
| **ListingHours** | Operating hours for listings |
| **ServiceSlots** | Availability time slots for services |

## Internal Relationships

| Relationship | Description |
|--------------|-------------|
| Service → ServiceSlots | Service has multiple time slots (1-to-many) |
| Listing → ListingHours | Listing has operating hours per day of week (1-to-many) |

## Cross-Module Connections

The Availability module connects to other modules:

| Connected Module | Via Model | Relationship |
|-----------------|-----------|--------------|
| **listings** | Listing, ListingHours | ListingHours belongs to Listing (listing_id FK) |
| **services** | Service, ServiceSlots | ServiceSlots belongs to Service (service_id FK) |
| **bookings** | Booking | Availability checks Booking counts to determine if slot is available |

## Availability Calculations

The Availability module determines if a service slot is available by:
1. Getting the ServiceSlots capacity
2. Counting existing Bookings that overlap with the requested time slot
3. Checking if remaining capacity >= requested quantity

```
Available = ServiceSlots.capacity - Count(Bookings where overlap)
```

## Key Model Attributes

### ListingHours
- `listing_id: UUID` - Foreign key to Listing
- `day_of_week: int` - Day of week (0=Sunday, 6=Saturday)
- `open_time: time` - Opening time
- `close_time: time` - Closing time

### ServiceSlots
- `service_id: UUID` - Foreign key to Service
- `day_of_week: int` - Day of week
- `start_time: time` - Slot start time
- `end_time: time` - Slot end time
- `capacity: int` - Maximum bookings for this slot
