# Business Owner Flow Sequence Diagrams

> Important business flows only. Basic CRUD patterns (view profile, list listings) are omitted as they follow the same sequence: Router → Service → DB.

## Business Registration& Setup

```plantuml
@startuml
title Business Registration & Setup

actor "Business Owner" as BO
participant "Frontend Vue" as Frontend <<boundary>>
participant "Auth Router" as AuthRouter <<control>>
participant "Auth Service" as AuthService <<service>>
participant "Users Service" as UsersService <<service>>
participant "Businesses Router" as BusinessesRouter <<control>>
participant "Businesses Service" as BusinessesService <<service>>
database "Database" as DB <<repository>>

== Register Business Owner Account ==

BO -> Frontend: Navigate to Business Registration
Frontend -> AuthRouter: POST /api/auth/register\n{email, password, user_type: "business", ...}
AuthRouter -> AuthService: register_user(db, user_data)
AuthService -> UsersService: create_user(db, UserCreate{...})
UsersService -> DB: INSERT User
DB --> UsersService: User created
UsersService --> AuthService: User
AuthService --> AuthRouter: UserResponse
AuthRouter --> Frontend: UserResponse(201)

== Create Business Profile ==

BO -> Frontend: Create business profile
Frontend -> BusinessesRouter: POST /api/businesses\n{business_name, description, address, location, ...}
BusinessesRouter -> BusinessesService: create_business(db, data, user_id)
BusinessesService -> DB: SELECT business WHERE user_id = user_id

alt User already has business
    BusinessesService -->> BusinessesRouter: HTTPException: "User already has a business"
end

BusinessesService -> DB: INSERT Business
DB --> BusinessesService: Business created
BusinessesService --> BusinessesRouter: BusinessResponse
BusinessesRouter --> Frontend: Business profile created

@enduml
```

## Employee Management

```plantuml
@startuml
title Employee Management - Add & Assign

actor "Business Owner" as BO
participant "Frontend Vue" as Frontend <<boundary>>
participant "Employees Router" as EmployeesRouter <<control>>
participant "Businesses Service" as BusinessesService <<service>>
participant "Users Service" as UsersService <<service>>
database "Database" as DB <<repository>>

== Create Employee ==

BO -> Frontend: Create new employee
Frontend -> EmployeesRouter: POST /api/employees\n{email, password, first_name, last_name, phone}
EmployeesRouter -> BusinessesService: add_business_employee(db, owner_id, email, password, ...)

BusinessesService -> DB: SELECT business WHERE user_id = owner_id
alt No business found
    BusinessesService -->> EmployeesRouter: HTTPException: "No business found"
end

BusinessesService -> DB: SELECT user WHERE email = email
alt Email already registered
    BusinessesService -->> EmployeesRouter: HTTPException: "Email already registered. Use a different email"
end

alt Email already assigned to this business
    BusinessesService -->> EmployeesRouter: HTTPException: "Employee with this email is already assigned"
end

BusinessesService -> UsersService: create_user(db, UserCreate{user_type: "employee", ...})
UsersService -> DB: INSERT new employee user
DB --> UsersService: Employee user created

BusinessesService -> DB: INSERT Business_Employee{business_id, employee_id}
BusinessesService --> EmployeesRouter: EmployeeResponse
EmployeesRouter --> Frontend: Employee created

== Assign Employee to Listing ==

BO -> Frontend: Assign employee to listing
Frontend -> EmployeesRouter: POST /api/employees/{employee_id}/listings/{listing_id}
EmployeesRouter -> BusinessesService: add_employee_to_listing(db, owner_id, employee_id, listing_id)

BusinessesService -> DB: SELECT business WHERE user_id = owner_id
alt No business
    BusinessesService -->> EmployeesRouter: HTTPException 404
end

BusinessesService -> DB: SELECT Business_Employee WHERE business_id AND employee_id
alt Not an employee of this business
    BusinessesService -->> EmployeesRouter: HTTPException 404
end

BusinessesService -> DB: SELECT Listing WHERE id = listing_id AND business_id
alt Listing doesn't belong to business
    BusinessesService -->> EmployeesRouter: HTTPException 403
end

BusinessesService -> DB: SELECT EmployeeListings WHERE employee_id AND listing_id
alt Already assigned
    BusinessesService -->> EmployeesRouter: HTTPException 400
end

BusinessesService -> DB: INSERT EmployeeListings{employee_id, listing_id}
BusinessesService --> EmployeesRouter: AssignmentResponse
EmployeesRouter --> Frontend: Employee assigned to listing

== Remove Employee from Listing ==

BO -> Frontend: Remove employee from listing
Frontend -> EmployeesRouter: DELETE /api/employees/{employee_id}/listings/{listing_id}
EmployeesRouter -> BusinessesService: remove_employee_from_listing(db, owner_id, employee_id, listing_id)

BusinessesService -> DB: SELECT EmployeeListings WHERE employee_id AND listing_id
alt Not assigned
    BusinessesService -->> EmployeesRouter: HTTPException 400
end

BusinessesService -> DB: DELETE EmployeeListings
BusinessesService --> EmployeesRouter: Success
EmployeesRouter --> Frontend: Employee removed

@enduml
```

## Listing Creation with Validation

```plantuml
@startuml
title Listing Creation with Validation

actor "Business Owner" as BO
participant "Frontend Vue" as Frontend <<boundary>>
participant "Listings Router" as ListingsRouter <<control>>
participant "Listings Service" as ListingsService <<service>>
database "Database" as DB <<repository>>

BO -> Frontend: Create new listing
Frontend -> ListingsRouter: POST /api/listings\n{title, description, location, base_price, business_type, interest_ids}
ListingsRouter -> ListingsService: create_listing(db, listing_data, user_id)

alt User has no business
    ListingsService -->> ListingsRouter: HTTPException: "Create your business profile first"
end

ListingsService -> ListingsService: validate_interest_ids_for_business_type(db, business_type_id, interest_ids)
alt Invalid interests for business_type
    ListingsService -->> ListingsRouter: HTTPException: "Invalid interests for this listing type: ..."
end

ListingsService -> ListingsService: build_location(location_data)
note right
    Location validation:
    - Extract lat/lng from location dict
    - Convert to WKBElement using Shapely Point
    - Store with SRID 4326
end note

ListingsService -> DB: INSERT Listing
ListingsService -> DB: INSERT ListingInterest for each interest_id
ListingsService --> ListingsRouter: ListingResponse
ListingsRouter --> Frontend: Listing created

@enduml
```

## Availability Setup

```plantuml
@startuml
title Availability Setup

actor "Business Owner" as BO
participant "Frontend Vue" as Frontend <<boundary>>
participant "Availability Router" as AvailabilityRouter <<control>>
participant "Availability Service" as AvailabilityService <<service>>
database "Database" as DB <<repository>>

== Configure Listing Hours ==

BO -> Frontend: Configure listing hours
Frontend -> AvailabilityRouter: POST /api/availability/listings/{listing_id}/hours\n{day_of_week, open_time, close_time}
AvailabilityRouter -> AvailabilityService: create_listing_hours(db, data)
AvailabilityService -> DB: INSERT ListingHours
AvailabilityService --> AvailabilityRouter: ListingHoursResponse
AvailabilityRouter --> Frontend: Hours configured

== Create Service Time Slots ==

BO -> Frontend: Create service time slots
Frontend -> AvailabilityRouter: POST /api/availability/services/{service_id}/slots\n{day_of_week, start_time, end_time, capacity}
AvailabilityRouter -> AvailabilityService: create_service_slot(db, data)

alt Service not found
    AvailabilityService -->> AvailabilityRouter: HTTPException 404
end

AvailabilityService -> DB: SELECT Service(service_id) to get listing_id
AvailabilityService -> AvailabilityService: _validate_slot_within_listing_hours()
alt Slot times outside listing hours
    AvailabilityService -->> AvailabilityRouter: HTTPException: "Slot times must be within listing hours"
end

AvailabilityService -> AvailabilityService: _check_slot_overlap()
alt Slot overlaps with existing
    AvailabilityService -->> AvailabilityRouter: HTTPException: "Slot overlaps with existing slot"
end

AvailabilityService -> DB: INSERT ServiceSlots
AvailabilityService --> AvailabilityRouter: ServiceSlotsResponse
AvailabilityRouter --> Frontend: Slots created

@enduml
```
