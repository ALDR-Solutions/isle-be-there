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
| Payments | Stripe |
| Email | Resend |
| Task Scheduling | APScheduler (booking auto-approval) |

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
│ verification_token│  │ is_verified     │     │ status          │
│ avatar_url      │     │ user_id (owner) │     │ business_type   │
│ phone           │     │ latitude        │     │ start_time      │
│ birth_date      │     │ longitude       │     │ end_time        │
│ interests_handled│    │ created_at      │     │ details (JSON)  │
│ created_at      │     └─────────────────┘     │ phone_number    │
└─────────────────┘                             │ email_address   │
                                                 └─────────────────┘
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
         Business_Employee   Booking ────▶ ItineraryItem
               │                    │
               ▼                    ▼
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
├── main.py                 # FastAPI app entry point, CORS, static files
├── core/
│   ├── config.py           # Environment configuration (Pydantic Settings)
│   ├── security.py         # JWT & password utilities
│   ├── email.py            # Resend email integration
│   └── stripe.py          # Stripe client configuration
├── infrastructure/
│   ├── database/
│   │   ├── engine.py       # Database engine setup
│   │   └── session.py      # Session management
│   └── storage.py          # Supabase storage client
└── modules/
    ├── auth/               # Authentication (login/register)
    ├── users/              # User management, profiles
    ├── businesses/         # Business profiles, owners
    ├── listings/           # Travel listings/experiences
    ├── services/           # Bookable services (tours, etc.)
    ├── bookings/            # Booking system + scheduler
    ├── reviews/             # User reviews + AI classification
    ├── employees/          # Business employees
    ├── interests/          # Interest categories & tagging
    ├── favourites/         # User's saved listings
    ├── recommendations/    # AI-powered recommendations (TODO)
    ├── itineraries/         # Trip planning engine
    ├── calendar/           # Unified calendar view (bookings + itinerary items)
    ├── availability/        # Listing hours & service slots
    ├── pricing/            # Platform-wide service fee configuration
    ├── discounts/           # Discount types & rules
    └── stripe_payment/     # Stripe payment events tracking
```

---

## Key Features

### 1. Listings & Search
- Full-text + vector search (embeddings for similarity)
- Geospatial filtering (nearby locations)
- Filter by business type, price range, status
- Images stored in Supabase
- Flexible `details` JSONB for custom attributes

### 2. Booking System
- Book services or listings directly
- Time slots with `booking_from_time` / `booking_to_time`
- Status flow: `pending` → `approved` → `completed`
- Guest count, special requests support
- Full pricing breakdown: base_price, service_fee_percent, service_fee_amount, discount_percent, discount_amount, display_price, final_price
- Links to `ItineraryItem` for planned bookings
- Stripe payment integration with `stripe_payment_intent_id`
- APScheduler for automatic approval of pending bookings

### 3. Reviews & Classification
- Rating (1-5) with constraints
- Language detection
- AI-based sentiment/aspect classification (keyword_classifier.py, review_classifier.py)
- Flagging system for moderation
- Business reply capability

### 4. Recommendations (In Development)
- User interest profiling
- Vector similarity matching (`embedding` column)
- Content-based filtering via business types
- Background worker for async generation

### 5. Itinerary Planning
- Input: dates, location, interests, budget, pace
- Output: day-by-day schedule with:
  - Suggested listings
  - Estimated costs
  - Travel time between stops
  - Respects max travel distance
- Status flow: `draft` → `saved` → `confirmed` → `completed` / `cancelled` / `archived`
- Links to bookings via `linked_booking_id`
- Supports discount application (`applied_discount_id`, `discount_amount`)

### 6. Calendar
- Unified view combining:
  - Booking events (from services/listings)
  - Itinerary item events
- Filterable by date range
- Color-coded by status

### 7. Pricing & Discounts
- **Platform Pricing**: Configurable `service_fee_percent` per business type or global
- **Discounts**: Multiple types (`package`, `vip`, `repeat_customer`, `holiday`, `manual`)
  - Percentage-based with optional cap
  - Validity windows, max uses, min total cost requirements
  - Business type restrictions

### 8. Availability
- **ListingHours**: Per-day-of-week open/close times
- **ServiceSlots**: Per-day time slots with capacity

### 9. Access Control
- JWT-based authentication
- Role-based permissions (`user_type`)
- Employee can manage their business listings
- Business owners manage their listings

---

## Database Schema Summary

| Table | Purpose |
|-------|---------|
| `users` | Platform users (regular, business, employee, admin) |
| `businesses` | Business profiles with location, owner FK |
| `business_types` | Categories (restaurant, tour, activity, etc.) |
| `listings` | Travel experiences/venues with geospatial + vector |
| `services` | Bookable offerings (tours, tickets) with availability |
| `service_slots` | Time-based capacity per service |
| `bookings` | User reservations with full pricing breakdown |
| `payment_events` | Stripe payment/refund event tracking |
| `reviews` | User feedback on listings |
| `business_replies` | Business responses to reviews |
| `business_employees` | Employee ↔ Business mapping |
| `employee_listings` | Employee ↔ Listing management |
| `listing_hours` | Per-day operating hours |
| `interests` | Interest categories |
| `user_interests` | User interest preferences |
| `listing_interests` | Listing tags |
| `business_type_interests` | Business type interest mapping |
| `favourites` | User saved listings |
| `itineraries` | Trip plans with budget, pace, dates |
| `itinerary_items` | Scheduled stops in an itinerary |
| `pricing_configs` | Platform service fee configuration |
| `discounts` | Discount rules and types |

---

## API Pattern

Each module follows the same pattern:

```
modules/<name>/
├── models.py    # SQLModel classes (database tables)
├── schemas.py   # Pydantic models (request/response)
├── service.py   # Business logic
├── router.py    # FastAPI endpoints
└── __init__.py  # Module exports
```

Some modules may also include:
- `scheduler.py` — APScheduler jobs (bookings)
- `worker.py` — Background processing (recommendations)
- `classifier.py` — AI classification logic (reviews)

---

## Dependencies

### Environment Variables

**Database & Storage:**
- `DATABASE_URL` — PostgreSQL connection string
- `SUPABASE_URL` — Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` — Server-side storage key
- `SUPABASE_STORAGE_BUCKET` — Storage bucket name (default: `uploads`)

**Auth & Security:**
- `JWT_SECRET_KEY` — JWT signing secret
- `JWT_ALGORITHM` — Default: `HS256`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` — Default: `30`
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS` — Default: `7`
- `FORGET_PWD_SECRET_KEY` — Password reset secret

**Stripe:**
- `STRIPE_SECRET_KEY` — Stripe secret key
- `STRIPE_PUBLISHABLE_KEY` — Stripe publishable key
- `STRIPE_WEBHOOK_SECRET` — Webhook verification

**Email:**
- `RESEND_API_KEY` — Resend API key
- `MAIL_FROM` — Sender email
- `FRONTEND_URL` — Frontend base URL

**Frontend:** Vue 3 + Pinia stores, Axios with JWT interceptors