# Auth Module - Class Diagram with Operations (PlantUML)

```plantuml
@startuml AuthModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

' =========================
' AUTH MODULE - MODELS WITH OPERATIONS
' =========================

' User model (from users module)
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
    +register_user(db, user_data): User
    +authenticate_user(db, email, password): User
    +build_token_response(user): dict
    +refresh_user_token(db, request): dict
    +reset_authenticated_user_password(db, user_id, data): None
    +disable_user_account(db, user_id): None
    +verify_email(token, db): None
    +resend_verification_email_for_user(db, email): None
    +forget_password(db, data, background_tasks): None
    +reset_password_with_token(db, data): None
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' User is authenticated by Auth module

@enduml
```

## Auth Module - Models with Operations

This diagram shows the Auth module models and their operations.

| Model | Source Module | Relationship |
|-------|--------------|--------------|
| **User** | users | Core user entity - Auth module authenticates users |

## Cross-Module Connections

The Auth module connects to the **users** module through:
- User model: Authentication validates against User credentials

## Key Model Attributes

### User
- `id: UUID` - Primary key
- `email: str` - Unique email for login
- `hashed_password: str` - Stored password hash
- `username: str` - Unique username
- `is_verified: bool` - Email verification status
- `verification_token: str` - Token for email verification
- `user_type: UserTypes` - Enum: regular, business, admin, employee
