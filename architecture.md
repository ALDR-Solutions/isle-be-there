# Backend Architecture

## Overview

The Isle Be There backend is a FastAPI application using SQLModel with PostgreSQL as the database. It provides RESTful APIs for a travel platform where users can discover Caribbean locations, book services, and plan itineraries.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| ORM | SQLModel / SQLAlchemy |
| Database | PostgreSQL |
| Vector Search | pgvector (embeddings for recommendations) |
| Geospatial | GeoAlchemy2 (location-based queries) |
| Auth | JWT with Passlib |
| Image Storage | Supabase Storage |

---

## Data Models

### Core Entities

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      User       │────▶│    Business     │────▶│    Listing     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (UUID)       │     │ id (UUID)       │     │ id (UUID)       │
│ email           │     │ business_name   │     │ title           │
│ username        │     │ description     │     │ description     │
│ first_name      │     │ business_email  │     │ address (JSON)  │
│ last_name       │     │ phone           │     │ base_price      │
│ user_type       │     │ address         │     │ image_urls[]    │
│ is_active       │     │ website         │     │ location (GEO)  │
│ is_verified     │     │ logo_url        │     │ embedding (VEC) │
│ avatar_url      │     │ is_verified     │     │ status          │
│ phone           │     │ latitude        │     │ business_type   │
│ birth_date      │     │ longitude       │     │ start_time      │
│ created_at      │     │ created_at      │     │ end_time        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### User Types

| Type | Description |
|------|-------------|
| `regular` | Regular customer |
| `business` | Business owner |
| `employee` | Business employee |
| `admin` | Platform admin |

### Relationships

```
User ─────────┬──────────┬──────────────┐
              │          │              │
              ▼          ▼              ▼
         Business   Favourites    Bookings
              │                │
              ▼                ▼
        Business_Employee   Booking
              │
              ▼
         Listing ◀─────── Service
              │
              ├──────────────┬──────────────┐
              ▼              ▼              ▼
         ListingInterest  Review     EmployeeListings
              │                            │
              ▼                            ▼
        Interests                    User (employee)
```

---

## Module Structure

```
backend/app/
├── main.py                 # FastAPI app entry point
├── core/
│   ├── config.py           # Environment configuration
│   └── security.py         # JWT & password utilities
├── infrastructure/
│   ├── database/
│   │   ├── engine.py       # Database engine setup
│   │   └── session.py      # Session management
│   └── storage.py          # Supabase storage client
└── modules/
    ├── auth/               # Authentication (login/register)
    ├── users/              # User management
    ├── businesses/         # Business profiles
    ├── listings/           # Travel listings/experiences
    ├── services/          # Bookable services (tours, etc.)
    ├── bookings/           # Booking system
    ├── reviews/            # User reviews + AI classification
    ├── employees/          # Business employees
    ├── interests/          # Interest categories & tagging
    ├── favourites/         # User's saved listings
    ├── recommendations/    # AI-powered recommendations
    └── itineraries/        # Trip planning engine
```

---

## Key Features

### 1. Listings & Search
- Full-text + vector search (embeddings for similarity)
- Geospatial filtering (nearby locations)
- Filter by business type, price range, status
- Images stored in Supabase

### 2. Booking System
- Book services or listings directly
- Time slots with `booking_from_time` / `booking_to_time`
- Status flow: `pending` → `approved` → `completed`
- Guest count, special requests support

### 3. Reviews & Classification
- Rating (1-5) with constraints
- Language detection
- AI-based sentiment/aspect classification
- Flagging system for moderation
- Business reply capability

### 4. Recommendations
- User interest profiling
- Vector similarity matching (`embedding` column)
- Content-based filtering via business types
- Collaborative filtering potential

### 5. Itinerary Planning
- Input: dates, location, interests, budget, pace
- Output: day-by-day schedule with:
  - Suggested listings
  - Estimated costs
  - Travel time between stops
  - Respects max travel distance

### 6. Access Control
- JWT-based authentication
- Role-based permissions (`user_type`)
- Employee can manage their business listings
- Business owners manage their listings

---

## Database Schema Summary

| Table | Purpose |
|-------|---------|
| `users` | Platform users (regular, business, employee, admin) |
| `businesses` | Business profiles with location |
| `business_types` | Categories (restaurant, tour, activity, etc.) |
| `listings` | Travel experiences/venues |
| `services` | Bookable offerings (tours, tickets) |
| `bookings` | User reservations |
| `reviews` | User feedback on listings |
| `business_replies` | Business responses to reviews |
| `business_employees` | Employee ↔ Business mapping |
| `employee_listings` | Employee ↔ Listing management |
| `interests` | Interest categories |
| `user_interests` | User interest preferences |
| `listing_interests` | Listing tags |
| `business_type_interests` | Business type interest mapping |
| `favourites` | User saved listings |

---

## API Pattern

Each module follows the same pattern:

```
modules/<name>/
├── models.py    # SQLModel classes (database tables)
├── schemas.py   # Pydantic models (request/response)
├── service.py   # Business logic
└── router.py    # FastAPI endpoints
```

---

## Dependencies

- **Frontend**: Vue 3 + Pinia stores
- **API Communication**: Axios with JWT interceptors
- **Environment Variables**: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, etc.