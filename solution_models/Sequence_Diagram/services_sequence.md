# Services Module - Sequence Diagrams

> Important business flows only. Basic CRUD patterns (create, read, update, delete service) are omitted as they follow the same sequence: Router → Service → DB.

## Service Availability Check Flow

```plantuml
@startuml
title Service Availability Check Flow

actor "User" as User
participant "Frontend Vue" as Frontend <<boundary>>
participant "Availability Router" as AvailabilityRouter <<control>>
participant "Availability Service" as AvailabilityService <<service>>
database "Database" as DB <<repository>>

User -> Frontend: Check service availability
Frontend -> AvailabilityRouter: GET /api/availability/services/{service_id}/available?date=YYYY-MM-DD&people=2
AvailabilityRouter -> AvailabilityService: get_service_availability(db, service_id, date, people)

AvailabilityService -> DB: SELECT Service WHERE service_id
alt Service not found
    AvailabilityService --> AvailabilityRouter: ServiceAvailableResponse(is_available=False, closed_reason="service_not_found")
end

AvailabilityService -> AvailabilityService: is_hotel_service(db, service_id)
note right
    Check BusinessType.name contains "hotel"
end note

AvailabilityService -> DB: SELECT ServiceSlots WHERE service_id AND day_of_week
DB --> AvailabilityService: slots

alt No slots found
    alt Has listing hours for this day
        AvailabilityService -> DB: SELECT ListingHours WHERE listing_id AND day_of_week
        DB --> AvailabilityService: listing_hours
        AvailabilityService --> AvailabilityService: Generate virtual slot from listing hours
    else No listing hours
        AvailabilityService --> AvailabilityService: Generate 24h virtual slot
    end
end

loop For each slot
    AvailabilityService -> DB: get_slot_remaining_capacity(service_id, slot_id, slot_date)
    DB --> AvailabilityService: remaining_capacity

    alt is_hotel
        note right: remaining >= 1
    else
        note right: remaining >= people
    end
end

alt ALL slots unavailable
    AvailabilityService --> AvailabilityRouter: closed_reason="fully_booked"
end

AvailabilityService --> AvailabilityRouter: ServiceAvailableResponse(slots, is_available, is_open)
AvailabilityRouter --> Frontend: AvailabilityResponse
User <- Frontend: Display available time slots

@enduml
```

## Service Access Control Flow

```plantuml
@startuml
title Service Access Control Flow

actor "User" as User
participant "Frontend Vue" as Frontend <<boundary>>
participant "Services Router" as ServicesRouter <<control>>
participant "require_service_access" as RequireServiceAccess <<dependency>>
database "Database" as DB <<repository>>

note right of ServicesRouter
    FastAPI dependency "require_service_access" validates:
    1. Admin: can access any service
    2. Business owner: owns the listing's business
    3. Employee: assigned to the listing
end note

User -> Frontend: View service details
Frontend -> ServicesRouter: GET /api/services/{service_id}
ServicesRouter -> RequireServiceAccess: require_service_access(service_id, user)

RequireServiceAccess -> DB: SELECT Service WHERE service_id = service_id
alt Not found
    RequireServiceAccess -->> ServicesRouter: HTTPException 404
end

RequireServiceAccess -> DB: SELECT Listing WHERE id = service.listing_id
DB --> RequireServiceAccess: listing

alt User is admin
    RequireServiceAccess --> ServicesRouter: Service (allowed)
else User is business owner
    RequireServiceAccess -> DB: SELECT Business WHERE id = listing.business_id AND user_id = user.id
    DB --> RequireServiceAccess: business
    alt Not owner
        RequireServiceAccess -->> ServicesRouter: HTTPException 403: "Not authorized"
    end
else User is employee
    RequireServiceAccess -> DB: SELECT EmployeeListings WHERE employee_id = user.id AND listing_id = listing.id
    DB --> RequireServiceAccess: assignment
    alt Not assigned
        RequireServiceAccess -->> ServicesRouter: HTTPException 403: "Not authorized"
    end
end

RequireServiceAccess --> ServicesRouter: Service (access granted)
ServicesRouter --> Frontend: ServiceResponse
Frontend --> User: Display service details

@enduml
```

## Service Status Transitions

```plantuml
@startuml
title Service Status Transitions

actor "Business Owner/Employee" as BO
participant "Frontend Vue" as Frontend <<boundary>>
participant "Services Router" as ServicesRouter <<control>>
participant "Services Service" as ServicesService <<service>>
database "Database" as DB <<repository>>

note right of ServicesService
    Service Status Lifecycle:
    - active: Visible and bookable (default on create)
    - inactive: Hidden, not bookable (archive)
    - deleted: Soft deleted, fully hidden (delete)
end note

== Create Service (Default: Active) ==

BO -> Frontend: Create new service
Frontend -> ServicesRouter: POST /api/services\nServiceCreate{listing_id, name, price, capacity, ...}
ServicesRouter -> ServicesService: create_service(db, data, user_id)
ServicesService -> DB: GET Listing(listing_id)
ServicesService -> DB: INSERT Service(status = active)
DB --> ServicesService: service created
ServicesService --> ServicesRouter: ServiceResponse(201)
BO <- Frontend: Service created (active)

== Deactivate Service (Archive) ==

BO -> Frontend: Archive service
Frontend -> ServicesRouter: PATCH /api/services/{service_id}/archive
ServicesRouter -> ServicesService: deactivate_service(db, service_id)
ServicesService -> DB: UPDATE Service SET status = inactive
DB --> ServicesService: service deactivated
ServicesService --> ServicesRouter: ServiceResponse
BO <- Frontend: Service archived (inactive)

== Delete Service (Soft Delete) ==

BO -> Frontend: Delete service
Frontend -> ServicesRouter: DELETE /api/services/{service_id}
ServicesRouter -> ServicesService: delete_service(db, service_id)
ServicesService -> DB: UPDATE Service SET status = deleted
DB --> ServicesService: service deleted
ServicesService --> ServicesRouter: ServiceResponse
BO <- Frontend: Service deleted (hidden)

@enduml
```

## Get Services by Listing (Role-Based)

```plantuml
@startuml
title Get Services by Listing (Role-Based Visibility)

actor "User" as User
participant "Frontend Vue" as Frontend <<boundary>>
participant "Services Router" as ServicesRouter <<control>>
participant "Services Service" as ServicesService <<service>>
database "Database" as DB <<repository>>

User -> Frontend: Get services for listing
Frontend -> ServicesRouter: GET /api/services?listing_id={uuid}
ServicesRouter -> ServicesService: get_services_by_listing(db, listing_id, user.user_type)

alt No listing_id (public - all active services)
    ServicesService -> DB: SELECT Service WHERE status = active ORDER BY created_at
    DB --> ServicesService: services
else With listing_id
    alt User is regular user
        ServicesService -> DB: SELECT Service WHERE listing_id AND status = active
        DB --> ServicesService: services
    else User is business or employee
        ServicesService -> DB: SELECT Service WHERE listing_id AND status != deleted
        DB --> ServicesService: services
    end
end

alt No services found
    ServicesService --> ServicesRouter: []
end

ServicesService --> ServicesRouter: List[ServiceResponse]
ServicesRouter --> Frontend: List[ServiceResponse]
User <- Frontend: Display services

@enduml
```
