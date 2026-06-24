# Services Module - Class Diagram (PlantUML)

```plantuml
@startuml ServicesModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

' =========================
' SERVICES MODULE - MODELS ONLY
' =========================

class Service {
    +service_id: UUID PK
    +created_at: datetime
    +name: str
    +description: str
    +price: float
    +season_price: float
    +status: StatusTypes
    +capacity: int
    +availability: dict
    +type_data: dict
    +updated_at: datetime
    +listing_id: UUID FK
    +image_urls: list[str]
    --
    +get_service_by_id(db, service_id): Service
    +get_services(db): list[Service]
    +get_services_by_listing(db, listing_id, user_type): list[Service]
    +get_services_by_listing_ids(db, listing_ids, user_type): list[Service]
    +create_service(db, data, user_id): Service
    +update_service(db, service_id, data): Service
    +delete_service(db, service_id): Service
    +deactivate_service(db, service_id): Service
}

enum StatusTypes {
    active
    inactive
    deleted
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' Listing (from listings module) - Parent listing
class Listing {
    +id: UUID PK
    +title: str
}

' Booking (from bookings module) - Bookings for this service
class Booking {
    +id: UUID PK
    +service_id: UUID FK
}

' ServiceSlots (from availability module) - Availability slots
class ServiceSlots {
    +id: int PK
    +service_id: UUID FK
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' Listing offers Services (1-to-many)
Listing "1" --> "0..*" Service : offers

' Service uses StatusTypes enum
Service --> StatusTypes : <<uses>>

' Service has ServiceSlots (1-to-many) - managed by availability module
Service "1" --> "0..*" ServiceSlots : has

' Service is booked via Bookings (1-to-many)
Service "1" --> "0..*" Booking : booked_in

@enduml
```

## Services Module - Models Only

This diagram shows only the models within the Services module and how it connects to other modules via models.

| Model | Description |
|-------|-------------|
| **Service** | Bookable service offered by a listing |
| **StatusTypes** | Enum for service status states |

**Note:** ServiceSlots is in the **availability** module, not services module.

## Cross-Module Connections

The Services module connects to other modules:

| Connected Module | Via Model | Relationship |
|-----------------|-----------|--------------|
| **listings** | Listing | Service belongs to Listing (listing_id FK) |
| **availability** | ServiceSlots | ServiceSlots belongs to Service (service_id FK) |
| **bookings** | Booking | Service is booked via Booking (service_id FK) |

## Key Model Attributes

### Service
- `service_id: UUID` - Primary key
- `listing_id: UUID` - Foreign key to Listing (parent)
- `name: str` - Service name
- `price: float` - Base price
- `season_price: float` - Seasonal pricing
- `capacity: int` - Maximum capacity
- `status: StatusTypes` - Current status enum
- `image_urls: list[str]` - Service images
