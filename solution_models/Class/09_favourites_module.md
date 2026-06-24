# Favourites Module - Class Diagram with Operations (PlantUML)

```plantuml
@startuml FavouritesModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

' =========================
' FAVOURITES MODULE - MODELS WITH OPERATIONS
' =========================

class Favourites {
    +id: UUID PK
    +user_id: UUID FK
    +listing_id: UUID FK
    +created_at: datetime
    <<unique>> (user_id, listing_id)
    --
    +list_favourites(db, user_id): list[dict]
    +add_favourite(db, user_id, listing_id): dict
    +remove_favourite(db, user_id, listing_id): None
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' User (from users module) - Who saved the favourite
class User {
    +id: UUID PK
    +email: str
}

' Listing (from listings module) - Being favourited
class Listing {
    +id: UUID PK
    +title: str
    +base_price: Decimal
    +image_urls: list[str]
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' User has Favourites (1-to-many)
User "1" --> "0..*" Favourites : has

' Listing is saved in Favourites (1-to-many)
Listing "1" --> "0..*" Favourites : saved_in

@enduml
```

## Favourites Module - Models with Operations

This diagram shows the Favourites module models and their operations.

| Model | Description |
|-------|-------------|
| **Favourites** | User's saved listings |

## Internal Relationships

The Favourites module has no internal model relationships - it only has the Favourites model.

## Cross-Module Connections

The Favourites module connects to other modules:

| Connected Module | Via Model | Relationship |
|-----------------|-----------|--------------|
| **users** | User | User saves favourites (user_id FK in Favourites) |
| **listings** | Listing | Listing is saved in favourites (listing_id FK in Favourites) |

## Unique Constraint

```
Favourites table has unique constraint on (user_id, listing_id)

This ensures:
- User can only favourite a listing once
- Adding again returns existing favourite (idempotent)
```

## Key Model Attributes

### Favourites
- `id: UUID` - Primary key
- `user_id: UUID` - Foreign key to User who favourited
- `listing_id: UUID` - Foreign key to Listing that was favourited
- `created_at: datetime` - When the favourite was created
