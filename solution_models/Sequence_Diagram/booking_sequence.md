# Booking Flow Sequence Diagrams

> Important business flows only. Basic CRUD patterns are omitted as they follow the same sequence: Router → Service → DB.

## Complete Booking Lifecycle

```plantuml
@startuml
title Complete Booking Lifecycle

actor "Client" as Client
participant "Frontend Vue" as Frontend <<boundary>>
participant "Bookings Router" as BookingsRouter <<control>>
participant "Bookings Service" as BookingsService <<service>>
participant "Availability Service" as AvailabilityService <<service>>
participant "Pricing Service" as PricingService <<service>>
participant "Stripe Payment Service" as StripeService <<service>>
database "Database" as DB <<repository>>
participant "Stripe API" as StripeAPI <<external>>

== Create Booking ==

Client -> Frontend: Submit booking request
Frontend -> BookingsRouter: POST /api/bookings\nBookingCreate(service_id, booking_from_time, booking_to_time, amount_of_people, itinerary_item_id)
BookingsRouter -> BookingsService: create_booking(db, booking_data, user_id)

alt invalid booking window
    BookingsService -->> BookingsRouter: HTTPException: "Booking end time must be after start time"
end

alt service not found or inactive
    BookingsService -> DB: GET Service(service_id)
    alt service status != active
        BookingsService -->> BookingsRouter: HTTPException: "Only active services can be booked"
    end
end

alt has capacity check
    BookingsService -> AvailabilityService: get_booked_count(service_id, booking_from_time, booking_to_time)
    AvailabilityService -> DB: Query overlapping bookings\n(status NOT IN cancelled, pending)
    DB --> AvailabilityService: booked_count
    BookingsService -> BookingsService: available_slots = service.capacity - booked_count
    alt available_slots < amount_of_people
        BookingsService -->> BookingsRouter: HTTPException: "Service is not available"
    end
end

alt has itinerary_item_id (package discount)
    BookingsService -> BookingsService: price_booking_from_itinerary_item()
    BookingsService -> DB: GET ItineraryItem(itinerary_item_id)
    BookingsService -> DB: GET Itinerary(applied_discount_id)
    BookingsService -> PricingService: calculate_display_price(db, listing_id, service_id)
    BookingsService -> BookingsService: apply discount if eligible
else standalone booking
    BookingsService -> PricingService: calculate_display_price(db, listing_id, service_id)
    BookingsService -> BookingsService: multiply by people/nights
end

BookingsService -> DB: INSERT Booking
DB --> BookingsService: booking_record
BookingsService --> BookingsRouter: Booking
BookingsRouter --> Frontend: BookingCreateResponse(201)

== Create Payment Intent ==

Client -> Frontend: Request to pay booking
Frontend -> BookingsRouter: POST /api/bookings/{booking_id}/payment-intent
BookingsRouter -> StripeService: create_payment_intent(db, booking_id, user_id)

alt booking not pending
    StripeService -->> BookingsRouter: HTTPException: "Booking is not in pending status"
end

alt slot no longer available
    StripeService -> AvailabilityService: is_available(service_id, capacity, from_time, to_time, people)
    alt not available
        StripeService -->> BookingsRouter: HTTPException: "The selected time slot is no longer available"
    end
end

alt final_price < 0.50
    StripeService -->> BookingsRouter: HTTPException: "Booking final price must be at least $0.50"
end

StripeService -> StripeAPI: stripe.PaymentIntent.create(amount_cents, currency, metadata)
StripeAPI --> StripeService: PaymentIntent(client_secret, id)
StripeService -> DB: UPDATE Booking SET stripe_payment_intent_id = id
StripeService -> DB: INSERT PaymentEvent(booking_id, "payment_intent.created", ...)
StripeService --> BookingsRouter: {client_secret: ...}
BookingsRouter --> Frontend: PaymentIntentResponse

== Confirm Payment ==

Client -> Frontend: Confirm payment
Frontend -> BookingsRouter: POST /api/bookings/{booking_id}/confirm-payment
BookingsRouter -> StripeService: confirm_payment(db, booking)

StripeService -> StripeAPI: stripe.PaymentIntent.retrieve(stripe_payment_intent_id)
alt payment not succeeded
    StripeService -->> BookingsRouter: {success: false, error: "Payment not yet completed or failed"}
end

alt slot no longer available (race condition check)
    StripeService -> AvailabilityService: is_available()
    alt slot unavailable
        StripeService -->> BookingsRouter: {success: false, error: "The selected time slot is no longer available"}
    end
end

StripeService -> DB: UPDATE Booking SET status = "approved"
StripeService -> DB: INSERT PaymentEvent(booking_id, "payment_intent.confirmed", ...)
StripeService --> BookingsRouter: {success: true, status: "approved"}
BookingsRouter --> Frontend: Success confirmation

== Cancel Booking (with Refund) ==

Client -> Frontend: Request to cancel booking
Frontend -> BookingsRouter: POST /api/bookings/{booking_id}/cancel
BookingsRouter -> BookingsService: cancel_booking(db, booking)

alt approved booking with payment requires refund
    BookingsService -> StripeService: process_refund(db, booking)
    alt refund failed or already processed
        StripeService -->> BookingsService: {success: false, error: ...}
        BookingsService -->> BookingsRouter: HTTPException: "Cannot cancel: {error}"
    end
end

BookingsService -> DB: UPDATE Booking SET status = "cancelled"
BookingsService --> BookingsRouter: 204 No Content
BookingsRouter --> Frontend: 204 No Content

@enduml
```

## Availability Check Logic

```plantuml
@startuml
title Availability Check Logic

participant "Bookings Service" as BookingsService <<service>>
participant "Availability Service" as AvailabilityService <<service>>
database "Database" as DB <<repository>>

BookingsService -> AvailabilityService: get_booked_count(service_id, booking_from_time, booking_to_time)
AvailabilityService -> DB: SELECT COALESCE(SUM(amount_of_people), 0)\nFROM bookings\nWHERE service_id AND status NOT IN (cancelled, pending)\nAND booking_from_time < new_to_time AND booking_to_time > new_from_time
DB --> AvailabilityService: booked_count (int)

alt service.capacity - booked_count < requested_people
    AvailabilityService --> BookingsService: insufficient capacity
else
    AvailabilityService --> BookingsService: available
end

@enduml
```

## Pricing Calculation Logic

```plantuml
@startuml
title Pricing Calculation Logic

participant "Bookings Service" as BookingsService <<service>>
participant "Pricing Service" as PricingService <<service>>
database "Database" as DB <<repository>>

alt has itinerary_item_id (package discount eligible)
    BookingsService -> DB: GET ItineraryItem(itinerary_item_id)
    BookingsService -> DB: GET Itinerary(applied_discount_id)
    alt discount exists and eligible
        BookingsService -> PricingService: calculate_display_price(db, listing_id, service_id)
        PricingService --> BookingsService: base_price, service_fee_percent
        BookingsService -> BookingsService: final_price = (base_price + fee) - discount
    else no discount
        BookingsService -> PricingService: calculate_display_price()
        BookingsService -> BookingsService: final_price = base_price + service_fee
    end
else standalone booking
    BookingsService -> PricingService: calculate_display_price()
    BookingsService -> BookingsService: final_price = base_price + service_fee (no discount)
end

@enduml
```

## Scheduler - Auto-Complete/Cancel

```plantuml
@startuml
title Scheduler - Auto-Update Expired Bookings

participant "Bookings Service" as BookingsService <<service>>
database "Database" as DB <<repository>>

note over BookingsService
    Background scheduler runs periodically
end note

BookingsService -> BookingsService: update_expired_bookings(db)

alt approved -> completed
    BookingsService -> DB: UPDATE Booking SET status = "completed"\nWHERE status = "approved" AND booking_to_time < now()
end

alt pending -> cancelled
    BookingsService -> DB: UPDATE Booking SET status = "cancelled"\nWHERE status = "pending" AND booking_to_time < now()
end

@enduml
```
