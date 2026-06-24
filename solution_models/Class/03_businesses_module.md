# Businesses Module - Class Diagram with Operations (PlantUML)

```plantuml
@startuml BusinessesModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

' =========================
' BUSINESSES MODULE - MODELS WITH OPERATIONS
' =========================

class Business {
    +id: UUID PK
    +business_name: str
    +description: str
    +business_email: str
    +phone: str
    +address: str
    +website: str
    +logo_url: str
    +is_verified: bool
    +created_at: datetime
    +user_id: UUID FK
    +location: Geography (PostGIS point)
    --
    +list_businesses(db, skip, limit, verified_only): list[dict]
    +get_business_by_id(db, business_id): dict | None
    +get_business_by_user_id(db, user_id): Business | None
    +create_business(db, data, user_id): dict
    +update_business(db, business_id, update_data, user_id, is_admin): dict
    +get_business_employees(db, user_id): list[dict]
    +add_business_employee(db, business_owner_id, email, password, ...): dict
    +update_business_employee(db, business_owner_id, employee_id, ...): dict
    +add_employee_to_listing(db, business_owner_id, employee_id, listing_id): dict
    +remove_employee_from_listing(db, business_owner_id, employee_id, listing_id): dict
}

class BusinessType {
    +id: UUID PK
    +created_at: datetime
    +name: str UK
    +description: str
    --
    +list_business_types(db): list[BusinessType]
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' User (from users module) - Owner of business
class User {
    +id: UUID PK
    +email: str UK
}

' Listing (from listings module) - Business has listings
class Listing {
    +id: UUID PK
    +title: str
}

' User owns Business (1-to-many)
User "1" --> "0..*" Business : owns

' Business has Listings (1-to-many)
Business "1" --> "0..*" Listing : has

' BusinessType categorizes Listings (1-to-many)
BusinessType "1" --> "0..*" Listing : categorizes

@enduml
```

## Businesses Module - Models with Operations

This diagram shows the Businesses module models and their operations.

| Model | Description |
|-------|-------------|
| **Business** | Business entity owned by a user |
| **BusinessType** | Category/type for businesses and listings |

## Cross-Module Connections

The Businesses module connects to other modules through its models:

| Connected Module | Via Model | Relationship |
|-----------------|-----------|--------------|
| **users** | Business | User owns Business (user_id FK in Business) |
| **listings** | Business, Listing | Business has many Listings (business_id FK in Listing) |
| **listings** | BusinessType, Listing | BusinessType categorizes Listings (business_type FK in Listing) |
| **reviews** | Business, BusinessReply | Business can respond to reviews via BusinessReply |

## Key Model Attributes

### Business
- `id: UUID` - Primary key
- `business_name: str` - Name of the business
- `user_id: UUID` - Foreign key to User (owner)
- `is_verified: bool` - Verification status
- `location: Geography` - Geographic location (PostGIS)

### BusinessType
- `id: UUID` - Primary key
- `name: str` - Unique business type name (e.g., "hotel", "restaurant", "tour")
- `description: str` - Type description
