# Listings Module - Class Diagram with Operations (PlantUML)

```plantuml
@startuml ListingsModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

' =========================
' LISTINGS MODULE - MODELS WITH OPERATIONS
' =========================

class Listing {
    +id: UUID PK
    +created_at: datetime
    +business_id: UUID FK
    +title: str
    +description: str
    +address: dict (JSONB)
    +base_price: Decimal
    +business_type: UUID FK
    +updated_at: datetime
    +image_urls: list[str]
    +status: Statuses
    +phone_number: str
    +email_address: str
    +location: Geography
    +embedding: vector
    +details: dict (JSONB)
    --
    +list_listings(db, skip, limit, city, country, business_type, min_price, max_price, sort_by, sort_order, status, availability_date, city_lat, city_lng, radius_km): list[dict]
    +get_listing_by_id(db, listing_id): dict
    +create_listing(db, data, user_id): dict
    +update_listing(db, listing, update_data, is_admin): dict
    +delete_listing(db, listing): Listing
    +get_active_listings(db, limit): list[dict]
    +get_business_listings(db, user_id): list[dict]
    +get_personalized_listings(db, user_id, limit): list[dict]
    +search_listings_combined(db, q, lat, lng, radius_km, limit): list[dict]
    +filter_by_availability(db, listings, start_dt, end_dt, requested_quantity): list[Listing]
    +get_cities_for_country(db, country): dict
}

enum Statuses {
    active
    inactive
    suspended
    pending
    approved
    rejected
}

class EmployeeListings {
    +id: UUID PK
    +employee_id: UUID FK
    +listing_id: UUID FK
    --
    +add_employee_to_listing(db, business_owner_id, employee_id, listing_id): dict
    +remove_employee_from_listing(db, business_owner_id, employee_id, listing_id): dict
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' Business (from businesses module) - Owns this listing
class Business {
    +id: UUID PK
    +business_name: str
}

' BusinessType (from businesses module) - Categorizes listing
class BusinessType {
    +id: UUID PK
    +name: str
}

' Service (from services module) - Offered by listing
class Service {
    +service_id: UUID PK
    +name: str
}

' ListingHours (from availability module) - Operating hours
class ListingHours {
    +id: int PK
    +listing_id: UUID FK
}

' Review (from reviews module) - For this listing
class Review {
    +id: UUID PK
    +listing_id: UUID FK
}

' Favourites (from favourites module) - Saved listing
class Favourites {
    +id: UUID PK
    +listing_id: UUID FK
}

' ItineraryItem (from itineraries module) - References this listing
class ItineraryItem {
    +id: UUID PK
    +listing_id: UUID FK
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' Business owns Listing (1-to-many)
Business "1" --> "0..*" Listing : owns

' BusinessType categorizes Listing (1-to-many)
BusinessType "1" --> "0..*" Listing : categorizes

' Listing uses Statuses enum
Listing --> Statuses : <<uses>>

' Listing has Employees via junction table
Listing "1" --> "0..*" EmployeeListings : has employees
EmployeeListings --> User : assigned to (employee_id FK)

' Listing offers Services (1-to-many)
Listing "1" --> "0..*" Service : offers

' Listing has Operating Hours (1-to-many)
Listing "1" --> "0..*" ListingHours : has

' Listing has Reviews (1-to-many)
Listing "1" --> "0..*" Review : has

' Listing is saved in Favourites (1-to-many)
Listing "1" --> "0..*" Favourites : saved_in

' Listing is referenced by ItineraryItems (1-to-many)
Listing "1" --> "0..*" ItineraryItem : referenced_by

@enduml
```

## Listings Module - Models with Operations

This diagram shows the Listings module models and their operations.

| Model | Description |
|-------|-------------|
| **Listing** | Travel experience/service listing |
| **Statuses** | Enum for listing status states |
| **EmployeeListings** | Junction table for employee-listing assignment |

## Cross-Module Connections

The Listings module is a central hub connecting many modules:

| Connected Module | Via Model | Relationship |
|-----------------|-----------|--------------|
| **businesses** | Business | Business owns Listing (business_id FK) |
| **businesses** | BusinessType | BusinessType categorizes Listing (business_type FK) |
| **users** | User | Employees assigned via EmployeeListings |
| **services** | Service | Listing offers Services (1-to-many) |
| **availability** | ListingHours | Listing has operating hours (1-to-many) |
| **reviews** | Review | Listing has Reviews (1-to-many) |
| **favourites** | Favourites | Listing can be saved in Favourites (1-to-many) |
| **itineraries** | ItineraryItem | ItineraryItem references Listing (1-to-many) |

## Key Model Attributes

### Listing
- `id: UUID` - Primary key
- `business_id: UUID` - Foreign key to Business (owner)
- `business_type: UUID` - Foreign key to BusinessType (category)
- `title: str` - Listing title
- `base_price: Decimal` - Base price for the listing
- `status: Statuses` - Current status enum
- `location: Geography` - PostGIS geography point
- `embedding: vector` - For similarity search

### EmployeeListings
- `employee_id: UUID` - Foreign key to User
- `listing_id: UUID` - Foreign key to Listing
