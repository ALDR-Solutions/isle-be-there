# Listings Module Sequence Diagrams

> Important business flows only. Basic CRUD patterns (create, read, update, delete listing) are omitted as they follow the same sequence: Router → Service → DB.

## Search Listings Flow

```plantuml
@startuml
title Search Listings Flow

actor "User" as User
participant "Frontend Vue" as Frontend <<boundary>>
participant "Listings Router" as ListingsRouter <<control>>
participant "Listings Service" as ListingsService <<service>>
database "Database" as DB <<repository>>

User -> Frontend: Search listings\n?q=restaurant&lat=18.5&lng=-77.8&radius_km=25
Frontend -> ListingsRouter: GET /api/listings/search\n?q, lat, lng, radius_km, limit
ListingsRouter -> ListingsService: search_listings_combined(db, q, lat, lng, radius_km, limit)

alt Only one of lat/lng provided
    ListingsRouter -->> Frontend: HTTPException 400: "Both lat and lng are required together"
end

ListingsService -> DB: SELECT listings WHERE status IN (active, approved)

alt Full-text search provided
    ListingsService -> DB: to_tsvector(title, description) @@ plainto_tsquery(q)
    ListingsService -> DB: Add ts_rank for ordering
    DB --> ListingsService: filtered listings with rank
end

alt Geospatial search provided
    ListingsService -> DB: ST_SetSRID(ST_MakePoint(lng, lat), 4326)
    ListingsService -> DB: ST_DWithin(location, point, radius_km * 1000)
    ListingsService -> DB: ST_Distance for ordering
    DB --> ListingsService: filtered listings with distance
end

alt No results found
    ListingsService --> ListingsRouter: []
end

ListingsService --> ListingsRouter: [Listing, ...]
ListingsRouter --> Frontend: Search results
User <- Frontend: Display matching listings

@enduml
```

## Personalized Listings Flow

```plantuml
@startuml
title Personalized Listings Flow

actor "User" as User
participant "Frontend Vue" as Frontend <<boundary>>
participant "Listings Router" as ListingsRouter <<control>>
participant "Listings Service" as ListingsService <<service>>
database "Database" as DB <<repository>>

User -> Frontend: View personalized recommendations
Frontend -> ListingsRouter: GET /api/listings/personalized?limit=20
ListingsRouter -> ListingsService: get_personalized_listings(db, user_id, limit)

ListingsService -> DB: SELECT UserInterest WHERE user_id = user_id
DB --> ListingsService: user_interests

alt No user interests defined
    ListingsService -> ListingsService: fetch_active_listings(db, limit)
    note right: Randomly shuffled active listings
    DB --> ListingsService: listings
    ListingsService --> ListingsRouter: [Listing, ...]
    ListingsRouter --> Frontend: [Listing, ...]
    User <- Frontend: Display general listings (random)
end

ListingsService -> DB: SELECT ListingInterest\nJOIN Listing WHERE interest_id IN user_interests\nAND status IN (active, approved)\nORDER BY random()
DB --> ListingsService: listings
ListingsService --> ListingsRouter: [Listing, ...]
ListingsRouter --> Frontend: Personalized list
User <- Frontend: Display recommendations

@enduml
```

## Listing Creation with Location & Interests

```plantuml
@startuml
title Listing Creation with Location & Interests Validation

actor "Business Owner" as BO
participant "Frontend Vue" as Frontend <<boundary>>
participant "Listings Router" as ListingsRouter <<control>>
participant "Listings Service" as ListingsService <<service>>
database "Database" as DB <<repository>>

BO -> Frontend: Create new listing
Frontend -> ListingsRouter: POST /api/listings\nListingCreate{title, location, base_price, business_type, interest_ids}
ListingsRouter -> ListingsService: create_listing(db, listing_data, user_id)

alt User has no business
    ListingsService -->> ListingsRouter: HTTPException 400: "Create your business profile first"
end

ListingsService -> ListingsService: validate_interest_ids_for_business_type(db, business_type, interest_ids)
alt Invalid interests for this listing type
    ListingsService -->> ListingsRouter: HTTPException 400: "Invalid interests for this listing type: ..."
end

ListingsService -> ListingsService: build_location(location_data)
note right
    - Extract lat/lng from location dict
    - Convert to WKBElement using Shapely Point
    - Store with SRID 4326
end note

ListingsService -> DB: INSERT Listing
ListingsService -> DB: INSERT ListingInterest for each validated interest_id
ListingsService --> ListingsRouter: ListingResponse(201)
BO <- Frontend: Listing created successfully

@enduml
```

## Get Listing with Stats

```plantuml
@startuml
title Get Listing with Review Stats

actor "User" as User
participant "Frontend Vue" as Frontend <<boundary>>
participant "Listings Router" as ListingsRouter <<control>>
participant "Listings Service" as ListingsService <<service>>
database "Database" as DB <<repository>>

User -> Frontend: View listing details
Frontend -> ListingsRouter: GET /api/listings/{listing_id}
ListingsRouter -> ListingsService: get_listing_by_id(db, listing_id)

ListingsService -> DB: SELECT Listing WITH business_type_rel, business_rel
DB --> ListingsService: listing
alt Listing not found
    ListingsService -->> ListingsRouter: HTTPException 404: "Listing not found"
end

ListingsService -> DB: SELECT avg(rating), count(id) FROM reviews WHERE listing_id
DB --> ListingsService: review_stats
ListingsService -> DB: SELECT interest_id FROM listing_interests WHERE listing_id
DB --> ListingsService: interest_ids
ListingsService -> ListingsService: serialize_listing(listing, stats, interests)
ListingsService --> ListingsRouter: ListingResponse
ListingsRouter --> Frontend: ListingResponse
User <- Frontend: Display listing details

@enduml
```
