# Business Workflow Documentation

## Overview

This document describes the end-to-end business workflows for the Isle Be There platform. It covers business registration, listing management, service provisioning, employee management, and the booking/payment lifecycle.

---

## Business Registration Flow

### New Business Registration

```
User Registration → Business Account Upgrade → Business Profile Creation → Verification

┌──────────────┐     ┌────────────────────┐     ┌─────────────────────┐     ┌──────────────┐
│   Regular   │────▶│  Upgrade to        │────▶│  Create Business    │────▶│   Admin      │
│   User      │     │  Business Account  │     │  Profile            │     │   Reviews    │
└──────────────┘     └────────────────────┘     └─────────────────────┘     └──────────────┘
                                                                          │
                                                              ┌────────────▼───────────┐
                                                              │  Verified / Rejected   │
                                                              └────────────────────────┘
```

### User Registration (Auth Module)

| Step | Actor | Action | System Response |
|------|-------|--------|-----------------|
| 1 | User | Register with email, password, username | Create User record with `user_type = "regular"` |
| 2 | System | Send verification email | Email sent via Resend |
| 3 | User | Verify email | `is_verified = true`, user can login |

### Business Account Upgrade

| Step | Actor | Action | System Response |
|------|-------|--------|-----------------|
| 1 | User | Update profile to business account | Call `POST /api/auth/register` with `user_type = "business"` |
| 2 | System | Validate no existing business for user | Check `businesses.user_id` for duplicates |
| 3 | User | Submit business details | Create Business record |
| 4 | Admin | Review and verify business | Set `business.is_verified = true` |

### Business Profile Creation

**Endpoint:** `POST /api/businesses`

**Request Body:**
```json
{
  "business_name": "string",
  "description": "string",
  "business_email": "string",
  "phone": "string",
  "address": {
    "street": "string",
    "city": "string",
    "country": "string"
  },
  "website": "string (optional)",
  "logo_url": "string (optional)"
}
```

**Validation Rules:**
- User must not already have a business (`get_business_by_user_id`)
- Business email must be unique
- Address is stored as JSONB

---

## Listing Management Flow

### Create Listing

```
Business Owner → Create Listing → Admin Review → Published

┌───────────────┐     ┌─────────────┐     ┌────────────┐     ┌────────────┐
│ Business     │────▶│ POST        │────▶│ Admin      │────▶│ Status:    │
│ Owner        │     │ /api/       │     │ Reviews    │     │ Approved  │
│              │     │ listings    │     │            │     │ / Active  │
└───────────────┘     └─────────────┘     └────────────┘     └────────────┘
```

**Endpoint:** `POST /api/listings`

**Prerequisites:**
- User must have `user_type = "business"`
- User must have a verified business profile

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "address": {
    "street": "string",
    "city": "string",
    "country": "string",
    "location": { "type": "Point", "coordinates": [lng, lat] }
  },
  "base_price": 0.00,
  "image_urls": ["string"],
  "business_type_id": "uuid",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "details": { "key": "value" }
}
```

**Listing Status Flow:**
```
draft → pending_review → approved → active
                              ↓
                         rejected → (can resubmit)
```

**Validation Rules:**
- `title` max 255 characters
- `base_price` must be >= 0
- `location` stored as GeoJSON Point for geospatial queries
- `embedding` vector generated for recommendations (future)

### Update Listing

**Endpoint:** `PUT /api/listings/{listing_id}`

**Authorization:** Only listing owner or business admin can update.

**Updatable Fields:**
- title, description, address, base_price, image_urls
- details (JSONB for custom attributes)
- start_time, end_time

**Non-Updatable After First Publish:**
- business_type_id (requires new listing)

### Delete Listing

**Endpoint:** `DELETE /api/listings/{listing_id}`

**Behavior:**
- Soft delete: Sets `status = "inactive"`
- Cancels all pending bookings associated with listing's services
- Fails if active/approved bookings exist

---

## Service Management Flow

### Create Service

```
Business Owner → Add Service to Listing → Configure Slots → Activate

┌───────────────┐     ┌─────────────┐     ┌────────────────┐     ┌────────────┐
│ Business     │────▶│ POST        │────▶│ Configure      │────▶│ Status:    │
│ Owner        │     │ /api/       │     │ Service Slots  │     │ Active    │
│              │     │ services    │     │                │     │           │
└───────────────┘     └─────────────┘     └────────────────┘     └────────────┘
```

**Endpoint:** `POST /api/services`

**Prerequisites:**
- User must be `business` or `employee` role
- Employee must be assigned to the listing (`EmployeeListings`)

**Request Body:**
```json
{
  "listing_id": "uuid",
  "name": "string",
  "description": "string (optional)",
  "duration_minutes": 60,
  "max_capacity": 10,
  "buffer_time_minutes": 15,
  "status": "active"
}
```

**Service Status Flow:**
```
draft → active → archived
```

**Business Rules:**
- Service inherits listing's business (`listing.business_id`)
- Multiple services can be created per listing (e.g., different tour times)
- Capacity checked at booking time against `service_slots`

### Service Slots (Availability)

**Endpoint:** `POST /api/services/{service_id}/slots`

```json
{
  "slot_date": "2026-05-27",
  "start_time": "09:00",
  "end_time": "17:00",
  "max_capacity": 10,
  "is_available": true
}
```

**Availability Check Flow:**
1. Booking request arrives for `service_id` and time range
2. System queries `service_slots` for overlapping periods
3. Sums `max_capacity` across all matching slots
4. Subtracts already-booked count from `bookings` table
5. Returns remaining available capacity

---

## Employee Management Flow

### Add Employee to Business

```
Business Owner → Add Employee → Create User → Assign to Listings

┌───────────────┐     ┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│ Business      │────▶│ POST        │────▶│ Create User │────▶│ Assign to      │
│ Owner         │     │ /api/       │     │ (type:      │     │ Listings       │
│               │     │ businesses/ │     │  employee)  │     │                │
│               │     │ employees   │     │              │     │                │
└───────────────┘     └─────────────┘     └──────────────┘     └────────────────┘
```

**Endpoint:** `POST /api/businesses/employees`

**Request Body:**
```json
{
  "email": "string",
  "password": "string",
  "username": "string (optional)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "phone": "string (optional)"
}
```

**Business Rules:**
- Creates new User with `user_type = "employee"`
- Links Employee to Business via `Business_Employee` table
- Employee email must be unique across all users
- Same email cannot be added to same business twice

### Assign Employee to Listing

**Endpoint:** `POST /api/businesses/employees/{employee_id}/listings`

**Request Body:**
```json
{
  "listing_id": "uuid"
}
```

**Business Rules:**
- Employee must already belong to the business
- Listing must belong to the same business
- Employee can be assigned to multiple listings
- Same employee cannot be assigned to same listing twice

### Employee Permissions

| Action | Business Owner | Employee (Assigned) |
|--------|---------------|---------------------|
| Create listing | ✓ | ✗ |
| Update own listing | ✓ | ✓ |
| Delete own listing | ✓ | ✗ |
| Create service | ✓ | ✓ |
| Update service | ✓ | ✓ |
| Delete service | ✓ | ✗ |
| View bookings | ✓ | ✓ |
| Manage bookings | ✓ | ✓ |

---

## Booking Flow

### User Discovers and Books

```
User Browse → Select Service → Create Booking → Payment → Confirmation

┌──────────┐     ┌────────────┐     ┌─────────────┐     ┌─────────────┐     ┌────────────┐
│ Regular  │────▶│ Search/    │────▶│ POST        │────▶│ Payment     │────▶│ Booking    │
│ User     │     │ Browse     │     │ /api/       │     │ Intent      │     │ Confirmed  │
│          │     │ Listings   │     │ bookings    │     │ Created     │     │            │
└──────────┘     └────────────┘     └─────────────┘     └─────────────┘     └────────────┘
```

### Create Booking (Pre-Payment)

**Endpoint:** `POST /api/bookings`

**Request Body:**
```json
{
  "service_id": "uuid",
  "booking_from_time": "datetime",
  "booking_to_time": "datetime",
  "amount_of_people": 2,
  "itinerary_item_id": "uuid (optional)"
}
```

**Validation Steps:**

| Step | Check | Error Response |
|------|-------|----------------|
| 1 | Booking window valid | 400: "Booking end time must be after start time" |
| 2 | Service exists and active | 400/404: "Service not found" |
| 3 | Capacity available | 409: "Service not available" |
| 4 | User owns the booking (when modifying) | 403: "Not authorized" |

**Availability Check:**
```python
def get_booked_count(service_id, booking_from_time, booking_to_time):
    # Query overlapping bookings with status in (pending, approved)
    # Sum amount_of_people for overlapping time ranges
    # Compare against service.max_capacity
```

### Pricing Calculation

**Endpoint:** `POST /api/bookings/{booking_id}/payment-intent`

**Price Breakdown:**
```
base_price (from service)
+ service_fee (platform fee %)
- discount (if itinerary with applied_discount_id)
= final_price
```

**Pricing Service Logic:**
1. Fetch `service.listing_id` → `listing.base_price`
2. Fetch `pricing_configs` for business type or global default
3. Calculate `service_fee = base_price * service_fee_percent`
4. If `itinerary_item_id` present, fetch `Itinerary.applied_discount_id`
5. Calculate `final_price = base_price + service_fee - discount_amount`

### Payment Flow

```
User → Payment Intent Request → Stripe Payment Intent → User Pays → Confirm Payment

┌────────┐     ┌───────────────┐     ┌──────────────┐     ┌────────┐     ┌───────────────┐
│ User   │────▶│ POST          │────▶│ Stripe       │────▶│ User   │────▶│ POST          │
│        │     │ /payment-intent│     │ Create Intent│     │ Pays   │     │ /confirm-    │
│        │     │               │     │              │     │        │     │ payment      │
└────────┘     └───────────────┘     └──────────────┘     └────────┘     └───────────────┘
```

**Payment Intent Creation:**
```python
stripe.PaymentIntent.create(
    amount=int(final_price * 100),  # cents
    currency="usd",
    metadata={
        "booking_id": str(booking_id),
        "user_id": str(user_id)
    }
)
```

**Confirm Payment:**
1. Retrieve PaymentIntent from Stripe
2. Verify `status == "succeeded"`
3. Re-validate slot availability
4. Update booking status → `approved`
5. Record `PaymentEvent` for audit trail

### Booking Status Flow

```
pending → approved → completed
    ↓         ↓
 cancelled  cancelled

- pending: Booking created, awaiting payment
- approved: Payment confirmed, slot reserved
- completed: Booking time passed, service delivered
- cancelled: Booking cancelled (may trigger refund)
```

### Cancellation & Refunds

**Endpoint:** `POST /api/bookings/{booking_id}/cancel`

**Cancellation Rules:**

| Booking Status | Refund Required | Action |
|---------------|-----------------|--------|
| pending | No | Cancel, release slot |
| approved + paid | Yes | Process refund via Stripe, then cancel |
| approved + unpaid | No | Cancel without refund |
| completed | No | No cancellation allowed |
| cancelled | N/A | Already cancelled |

**Refund Process:**
```python
stripe.Refund.create(
    payment_intent=booking.stripe_payment_intent_id,
    amount=booking.final_price  # Full refund, can be partial
)
```

---

## Itinerary Flow (User Perspective)

### Plan and Book Multiple Services

```
User → Plan Itinerary → Save → Confirm → Book Items → Bookings Created

┌────────┐     ┌─────────────┐     ┌────────┐     ┌──────────┐     ┌────────────┐
│ User   │────▶│ POST         │────▶│ POST   │────▶│ POST     │────▶│ Multiple   │
│        │     │ /itineraries │     │ /confirm│     │ /book    │     │ Bookings   │
│        │     │ /plan        │     │        │     │          │     │ Created    │
└────────┘     └─────────────┘     └────────┘     └──────────┘     └────────────┘
```

### Plan Itinerary

**Endpoint:** `POST /api/itineraries/plan`

**Request:**
```json
{
  "start_date": "2026-06-01",
  "end_date": "2026-06-05",
  "country": "Jamaica",
  "interests": ["beach", "food", "adventure"],
  "budget_level": "medium",
  "pace": "balanced",
  "number_of_people": 2,
  "bookable_only": true
}
```

**Planning Algorithm:**
1. Load candidates: All active listings in country (limit 120)
2. Filter by availability if `bookable_only = true`
3. Select one hotel for entire trip (budget + interest match)
4. Schedule activities per day:
   - Score candidates by: interest match, variety, budget fit, proximity
   - Respect `DEFAULT_MAX_TRAVEL_KM_BETWEEN_STOPS` (25km)
   - Limit slots per day by pace: relaxed=2, balanced=3, packed=4
5. Return day-by-day schedule with costs

**Response:**
```json
{
  "trip_days": 5,
  "budget_level": "medium",
  "pace": "balanced",
  "total_estimated_cost": 850.00,
  "daily_target_budget": 240.00,
  "days": [
    {
      "date": "2026-06-01",
      "total_estimated_cost": 180.00,
      "total_duration_hours": 8.5,
      "stops": [
        {
          "listing_id": "uuid",
          "title": "Sunset Beach Resort",
          "business_type_name": "hotel",
          "estimated_cost": 180.00,
          "start_time": "15:00",
          "end_time": "16:00",
          "score": 100.0,
          "reason_tags": ["hotel_checkin"]
        }
      ]
    }
  ]
}
```

### Save Itinerary

**Endpoint:** `POST /api/itineraries`

Saves planned itinerary to database with items.

**Itinerary Status Flow:**
```
draft → saved → confirmed → completed
                       ↓
                  cancelled / archived
```

### Confirm and Apply Discount

**Endpoint:** `POST /api/itineraries/{itinerary_id}/confirm`

**Discount Eligibility:**
- Package discount requires 3+ services booked
- Minimum total cost $100
- Discount percentage: 10% (default)
- Maximum discount cap: configurable

**Response:**
```json
{
  "itinerary": { "id": "uuid", "status": "confirmed", "items": [...] },
  "discount_applied": true,
  "discount_amount": 85.00
}
```

### Book Itinerary Items

**Endpoint:** `POST /api/itineraries/{itinerary_id}/book`

**Request (optional):**
```json
{
  "item_ids": ["uuid1", "uuid2"]  // Book specific items, or all if empty
}
```

**Conversion Process:**
1. Validate itinerary is CONFIRMED
2. For each item without `linked_booking_id`:
   - Find active service for the listing
   - Create booking via `BookingService.create_booking()`
   - Link `ItineraryItem.linked_booking_id = booking.id`
   - Update item status → `BOOKED`
3. If all items booked → Update itinerary status → `COMPLETED`

---

## Financial Flow

### Platform Revenue Model

```
User Payment → Stripe → Platform Fee → Business Payout

┌────────┐     ┌───────────┐     ┌────────────┐     ┌────────────┐
│ User   │────▶│ Stripe    │────▶│ Platform   │────▶│ Business   │
│ Pays   │     │ (Payment  │     │ (Service   │     │ (Revenue   │
│        │     │  Intent)  │     │  Fee)      │     │  - Fee)    │
└────────┘     └───────────┘     └────────────┘     └────────────┘
```

### Service Fee Configuration

**Endpoint:** `GET /api/pricing/configs`

**Pricing Config Schema:**
```json
{
  "id": "uuid",
  "business_type_id": "uuid (nullable for global)",
  "service_fee_percent": 10.0,
  "effective_from": "2026-01-01",
  "effective_to": null
}
```

**Fee Calculation:**
```python
service_fee = base_price * (service_fee_percent / 100)
final_price = base_price + service_fee - discount
```

### Payment Events Tracking

**Stripe Payment Events Table:** `payment_events`

| Event Type | Trigger | Data Stored |
|------------|---------|-------------|
| `payment_intent.created` | PaymentIntent created | intent_id, amount |
| `payment_intent.confirmed` | Payment successful | intent_id, amount |
| `refund.initiated` | Refund started | intent_id, amount |
| `refund.completed` | Refund processed | intent_id, amount |
| `refund.failed` | Refund failed | intent_id, error |

### Payout Schedule (Future)

- Business receives payouts minus platform commission
- Payout frequency: Weekly (configurable)
- Minimum payout threshold: $50

---

## Access Control Matrix

### Roles and Permissions

| Action | Regular | Business | Employee | Admin |
|--------|---------|----------|----------|-------|
| Browse listings | ✓ | ✓ | ✓ | ✓ |
| Create booking | ✓ | ✓ | ✓ | ✓ |
| Cancel own booking | ✓ | ✓ | ✓ | ✓ |
| Create itinerary | ✓ | ✓ | ✓ | ✓ |
| Save itinerary | ✓ | ✓ | ✓ | ✓ |
| Create business | ✗ | ✓ | ✗ | ✓ |
| Create listing | ✗ | ✓ | ✗ | ✓ |
| Manage own listings | ✗ | ✓ | ✓ | ✓ |
| Create services | ✗ | ✓ | ✓ (assigned) | ✓ |
| Manage employees | ✗ | ✓ | ✗ | ✓ |
| Add employees | ✗ | ✓ | ✗ | ✓ |
| View all bookings | ✗ | Own business | Own listings | ✓ |
| Manage all businesses | ✗ | ✗ | ✗ | ✓ |
| Verify businesses | ✗ | ✗ | ✗ | ✓ |

### Permission Dependencies

```
Business Owner
├── Can manage own business profile
├── Can create/manage own listings
├── Can add employees to business
│   └── Employees can manage assigned listings
└── Can view bookings for own listings

Admin
├── Can verify businesses
├── Can view all data
└── Can manage platform settings
```

---

## Error Handling

### Common Error Responses

| HTTP Code | Scenario | Response Body |
|-----------|----------|---------------|
| 400 | Invalid request data | `{"detail": "Validation error message"}` |
| 401 | Not authenticated | `{"detail": "Not authenticated"}` |
| 403 | Not authorized | `{"detail": "Not authorized to perform this action"}` |
| 404 | Resource not found | `{"detail": "Resource not found"}` |
| 409 | Conflict (e.g., slot unavailable) | `{"detail": "Service not available"}` |
| 500 | Internal server error | `{"detail": "Internal server error"}` |

### Booking Conflict Resolution

When a slot becomes unavailable between booking creation and payment confirmation:

1. System re-validates availability on payment intent creation
2. If slot lost → Return 409 with clear message
3. User can choose alternative time or cancel

---

## Appendix: API Endpoint Summary

### Businesses
- `GET /api/businesses` - List businesses
- `GET /api/businesses/me` - Get own business
- `POST /api/businesses` - Create business
- `PUT /api/businesses/{business_id}` - Update business
- `GET /api/businesses/types` - List business types

### Listings
- `GET /api/listings` - List all listings
- `GET /api/listings/search` - Search with filters
- `GET /api/listings/personalized` - Personalized recommendations
- `POST /api/listings` - Create listing
- `PUT /api/listings/{listing_id}` - Update listing
- `DELETE /api/listings/{listing_id}` - Delete listing

### Services
- `GET /api/services` - List services
- `GET /api/services/{service_id}` - Get service details
- `POST /api/services` - Create service
- `PUT /api/services/{service_id}` - Update service
- `DELETE /api/services/{service_id}` - Delete service
- `PATCH /api/services/{service_id}/archive` - Archive service

### Bookings
- `POST /api/bookings` - Create booking
- `GET /api/bookings/{booking_id}` - Get booking details
- `GET /api/bookings/{booking_id}/price` - Get price breakdown
- `POST /api/bookings/{booking_id}/payment-intent` - Create payment intent
- `POST /api/bookings/{booking_id}/confirm-payment` - Confirm payment
- `POST /api/bookings/{booking_id}/cancel` - Cancel booking

### Itineraries
- `POST /api/itineraries/plan` - Plan itinerary
- `POST /api/itineraries` - Save itinerary
- `GET /api/itineraries` - List user itineraries
- `GET /api/itineraries/{itinerary_id}` - Get itinerary details
- `GET /api/itineraries/{itinerary_id}/price` - Get itinerary price
- `POST /api/itineraries/{itinerary_id}/confirm` - Confirm itinerary
- `POST /api/itineraries/{itinerary_id}/book` - Book itinerary items

### Employees
- `POST /api/businesses/employees` - Add employee
- `PUT /api/businesses/employees/{employee_id}` - Update employee
- `POST /api/businesses/employees/{employee_id}/listings` - Assign to listing
- `DELETE /api/businesses/employees/{employee_id}/listings/{listing_id}` - Remove from listing