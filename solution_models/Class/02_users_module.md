# Users Module - Class Diagram (PlantUML)

```plantuml
@startuml UsersModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

' =========================
' USERS MODULE - MODELS ONLY
' =========================

class User {
    +id: UUID PK
    +email: str UK
    +hashed_password: str
    +username: str UK
    +first_name: str
    +last_name: str
    +user_type: UserTypes
    +is_active: bool
    +is_verified: bool
    +verification_token: str
    +avatar_url: str
    +phone: str
    +birth_date: date
    +interests_handled: bool
    +created_at: datetime
    +updated_at: datetime
    --
    +get_user_by_email(db, email): User | None
    +get_user_by_id(db, user_id): User | None
    +get_user_by_username(db, username): User | None
    +create_user(db, user_data): User
    +update_profile(db, user_id, data): User
    +get_profile(db, user_id): User
    +mark_interests_handled(db, user_id): User
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' User is created/managed by Users module

@enduml
```

## Users Module - Models Only

This diagram shows only the models within the Users module.

| Model | Description |
|-------|-------------|
| **User** | Core user entity with authentication data |

## Cross-Module Connections

The Users module connects to other modules through the **User** model:

| Connected Module | Via Model | Relationship |
|-----------------|-----------|--------------|
| **auth** | User | Auth module authenticates users |
| **bookings** | User | User books services (user_id FK in Booking) |
| **reviews** | User | User writes reviews (user_id FK in Review) |
| **favourites** | User | User saves favourites (user_id FK in Favourites) |
| **itineraries** | User | User creates itineraries (user_id FK in Itinerary) |
| **businesses** | User | User owns businesses (user_id FK in Business) |

## Key Model Attributes

### User
- `id: UUID` - Primary key
- `email: str` - Unique email for login
- `username: str` - Unique username
- `hashed_password: str` - Stored password hash
- `user_type: UserTypes` - Enum: regular, business, admin, employee
- `is_verified: bool` - Email verification status
