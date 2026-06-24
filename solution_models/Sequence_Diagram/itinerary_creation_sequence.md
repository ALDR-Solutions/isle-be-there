# Itinerary Creation Flow

> Important business flows only. Basic read operations (get itinerary, list itineraries) are omitted.

## Plan Itinerary Flow

```plantuml
@startuml
title Plan Itinerary Flow

actor "Client" as Client
participant "Frontend Vue" as Frontend <<boundary>>
participant "Itineraries Router" as ItinerariesRouter <<control>>
participant "Itinerary Service" as ItineraryService <<service>>
participant "Listings Service" as ListingsService <<service>>
database "Database" as DB <<repository>>

Client -> Frontend: Submit itinerary preferences
Frontend -> ItinerariesRouter: POST /api/itineraries/plan\nItineraryPlanRequest(start_date, trip_days, budget_level, pace, interests, ...)
ItinerariesRouter -> ItineraryService: plan_itinerary(db, plan_request, user_id)

group Load candidate listings
    ItineraryService -> DB: SELECT listings WHERE status IN (active, approved)
    DB --> ItineraryService: raw_listings

    alt Country filter required
        ItineraryService -> DB: Filter by address["country"] ilike country
        DB --> ItineraryService: filtered_listings
    end

    alt bookable_only required
        ItineraryService -> DB: JOIN Service WHERE status = active
        ItineraryService -> ItineraryService: filter_by_availability(listings, start_dt, end_dt)
        note right
            filter_by_availability is imported directly from listings.service
            Queries services with capacity, then checks booked counts
        end note
        ItineraryService --> ItineraryService: available_listings
    end
end

alt No candidates found
    ItineraryService --> ItinerariesRouter: result (trip_days=[], total_cost=0)
    ItinerariesRouter --> Frontend: empty response
end

group Select hotel for entire trip
    ItineraryService -> ItineraryService: pick_hotel(candidates, request)
    note right
        Internal scoring by budget fit + interest match.
        Returns best hotel candidate or None.
    end note
end

group Schedule activities per day
    loop For each trip day (day_idx = 0 to days-1)
        alt day_idx < hotel_nights
            note right: Hotel stop scheduled for this night
        end note

        loop While scheduled< slots_per_day
            ItineraryService -> ItineraryService: pick_best_activity(candidates, ...)

            alt No valid candidate OR end_hour > 19:00
                note right: Scheduling ends for this day
                end note
                break
            else Candidate found
                note right: Best candidate selected and added to itinerary
            end
        end
    end
end

ItineraryService --> ItinerariesRouter: ItineraryPlanResponse(trip_days, budget_level, pace, total_cost, daily_target_budget, days)
ItinerariesRouter --> Frontend: Plan response with daily stops
Frontend --> Client: Display planned itinerary

@enduml
```

## Save Itinerary Flow

```plantuml
@startuml
title Save Itinerary Flow

actor "Client" as Client
participant "Frontend Vue" as Frontend <<boundary>>
participant "Itineraries Router" as ItinerariesRouter <<control>>
participant "Itinerary Service" as ItineraryService <<service>>
database "Database" as DB <<repository>>

Client -> Frontend: Save itinerary
Frontend -> ItinerariesRouter: POST /api/itineraries\nItinerarySaveRequest(plan_request, title, status: SAVED)
ItinerariesRouter -> ItineraryService: save_itinerary(db, user_id, payload)

group Validate plan matches request (re-plan for verification)
    ItineraryService -> ItineraryService: plan_itinerary(db, plan_request)

    alt Days mismatch
        ItineraryService -->> ItinerariesRouter: HTTPException 400: "Saved itinerary does not match requested trip length"
    end
end

ItineraryService -> DB: INSERT Itinerary(status=SAVED, ...)
DB --> ItineraryService: created_itinerary
ItineraryService -> DB: flush()

ItineraryService -> ItineraryService: build_items_for_saved_itinerary(itinerary_id, planned)

loop For each day and stop
    ItineraryService -> DB: INSERT ItineraryItem
end

note over ItineraryService, DB
    Transaction: Itinerary + Items committed atomically
end note

ItineraryService --> ItinerariesRouter: SavedItineraryResponse(201)
ItinerariesRouter --> Frontend: 201 Created with saved itinerary
Frontend --> Client: Itinerary saved successfully

@enduml
```

## Confirm Itinerary Flow

```plantuml
@startuml
title Confirm Itinerary Flow

actor "Client" as Client
participant "Frontend Vue" as Frontend <<boundary>>
participant "Itineraries Router" as ItinerariesRouter <<control>>
participant "Itinerary Service" as ItineraryService <<service>>
participant "Discounts Service" as DiscountsService <<service>>
database "Database" as DB <<repository>>

Client -> Frontend: Confirm itinerary
Frontend -> ItinerariesRouter: POST /api/itineraries/{id}/confirm
ItinerariesRouter -> ItineraryService: confirm_itinerary(db, itinerary_id, user_id)

ItineraryService -> DB: SELECT Itinerary WHERE id AND user_id
DB --> ItineraryService: itinerary or None

alt Not found
    ItineraryService -->> ItinerariesRouter: HTTPException 404
end

alt Status != DRAFT
    ItineraryService -->> ItinerariesRouter: HTTPException 400: "Only DRAFT itineraries can be confirmed"
end

ItineraryService -> DiscountsService: check_package_discount_eligibility(db, itinerary)
note right
    Internal helper. Checks item_count >= 3 AND total_cost >= $100.
    Returns eligibility_result dict.
end note

alt Discount eligible
    note right: result = {eligible: true, discount: Discount, estimated_discount: X}
    ItineraryService -> DB: UPDATE Itinerary SET applied_discount_id, discount_amount
else Not eligible
    note right: result = {eligible: false, reason: ...}
end

ItineraryService -> DB: UPDATE Itinerary SET status = CONFIRMED
ItineraryService -> DB: COMMIT

ItineraryService --> ItinerariesRouter: {itinerary, discount_applied, discount_amount}
ItinerariesRouter --> Frontend: ItineraryConfirmResponse
Frontend --> Client: Itinerary confirmed with discount applied

@enduml
```

## Convert Itinerary to Bookings Flow

```plantuml
@startuml
title Convert Itinerary to Bookings Flow

actor "Client" as Client
participant "Frontend Vue" as Frontend <<boundary>>
participant "Itineraries Router" as ItinerariesRouter <<control>>
participant "Itinerary Service" as ItineraryService <<service>>
participant "Bookings Service" as BookingsService <<service>>
database "Database" as DB <<repository>>

Client -> Frontend: Book itinerary items
Frontend -> ItinerariesRouter: POST /api/itineraries/{id}/book\nItineraryBookRequest(item_ids?)
ItinerariesRouter -> ItineraryService: convert_itinerary_to_bookings(db, itinerary_id, user_id, item_ids)

ItineraryService -> DB: SELECT Itinerary WITH items WHERE id AND user_id
DB --> ItineraryService: itinerary with items

alt Status != CONFIRMED
    ItineraryService -->> ItinerariesRouter: HTTPException 400: "Only CONFIRMED itineraries can be converted"
end

note over ItineraryService, DB
    BEGIN TRANSACTION
end note

ItineraryService -> ItineraryService: all_booked = true

loop For each item (optionally filtered by item_ids)
    alt item.linked_booking_id exists
        note right: Item already has booking, skip
    else No linked booking
        ItineraryService -> DB: SELECT Service WHERE listing_id AND status = active
        DB --> ItineraryService: service or None

        alt No active service
            ItineraryService -->> ItinerariesRouter: HTTPException 400: "Cannot convert without an active service"
            note over ItineraryService, DB: ROLLBACK TRANSACTION
            break
        else Service available
            ItineraryService -> BookingsService: create_booking(db, BookingCreate, user_id)
            BookingsService -> DB: INSERT Booking
            DB --> BookingsService: created_booking
            BookingsService --> ItineraryService: booking
            deactivate BookingsService

            ItineraryService -> DB: UPDATE ItineraryItem SET linked_booking_id, status=BOOKED

            alt booking.status == cancelled
                ItineraryService -> ItineraryService: all_booked = false
            end
        end
    end
end

alt all_booked == true AND items exist
    ItineraryService -> DB: UPDATE Itinerary SET status = COMPLETED
else all_booked == false
    note right: Itinerary stays as CONFIRMED (no status change)
end

ItineraryService -> DB: COMMIT
note over ItineraryService, DB
    END TRANSACTION: committed or rolled back
end note

ItineraryService --> ItinerariesRouter: itinerary with booking links
ItinerariesRouter --> Frontend: ItineraryResponse
Frontend --> Client: Bookings created (pending payment via separate flow)

@enduml
```
