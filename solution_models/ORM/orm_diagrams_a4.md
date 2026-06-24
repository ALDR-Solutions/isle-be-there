# Isle Be There - ORM Diagrams (3-Part A4)

## Part 1: Core Entities (User, Business, Listing, Service)

```plantuml
@startuml Part1_Core_Entities
hide circle
skinparam linetype ortho
skinparam classAttributeIconSize 0

title Part 1: Core Entities

left to right direction

class User {
    - id : UUID PK
    - email : str UK
    - username : str UK
    - hashed_password : str
    - first_name : str
    - last_name : str
    - user_type : enum
    - is_active : bool
    - is_verified : bool
    - avatar_url : str
    - phone : str
    - birth_date : date
    - created_at : datetime

    + bookings : List<Booking>
    + reviews : List<Review>
    + favourites : List<Favourite>
    + itineraries : List<Itinerary>
    + employee_listings : List<EmployeeListing>
}

class Business {
    - id : UUID PK
    - user_id : UUID FK → User
    - business_name : str
    - is_verified : bool
    - created_at : datetime

    + owner : User
    + listings : List<Listing>
    + employees : List<BusinessEmployee>
}

class BusinessEmployee {
    - id : UUID PK
    - business_id : UUID FK → Business
    - employee_id : UUID FK → User
}

class BusinessType {
    - id : UUID PK
    - name : str
}

class Listing {
    - id : UUID PK
    - business_id : UUID FK → Business
    - title : str
    - description : str
    - base_price : decimal
    - status : enum
    - image_urls : list~str~
    - location : Geography
    - embedding : vector
    - details : dict
    - created_at : datetime

    + business : Business
    + services : List<Service>
    + reviews : List<Review>
    + favourites : List<Favourite>
    + hours : List<ListingHours>
    + itinerary_items : List<ItineraryItem>
    + employee_listings : List<EmployeeListing>
}

class EmployeeListing {
    - id : UUID PK
    - employee_id : UUID FK → User
    - listing_id : UUID FK → Listing
}

class ListingHours {
    - id : int PK
    - listing_id : UUID FK → Listing
    - day_of_week : int
    - open_time : time
    - close_time : time

    + listing : Listing
}

class Service {
    - service_id : UUID PK
    - listing_id : UUID FK → Listing
    - name : str
    - description : str
    - price : float
    - season_price : float
    - status : enum
    - capacity : int
    - availability : dict
    - type_data : dict
    - created_at : datetime

    + listing : Listing
    + bookings : List<Booking>
    + slots : List<ServiceSlot>
}

class ServiceSlot {
    - id : int PK
    - service_id : UUID FK → Service
    - day_of_week : int
    - start_time : time
    - end_time : time
    - capacity : int
}

' COMPOSITION
User *-- Business
Business *-- Listing
Listing *-- Service
Listing *-- ListingHours
Service *-- ServiceSlot

' AGGREGATION
User o-- BusinessEmployee
Business o-- BusinessEmployee
Business o-- BusinessType
Listing o-- EmployeeListing
User o-- EmployeeListing
Service o-- ServiceSlot

' ASSOCIATION
BusinessType --> Listing

@enduml
```

---

## Part 2: Bookings, Payments & Favourites

```plantuml
@startuml Part2_Bookings_Payments
skinparam dpi 120
skinparam defaultFontSize 10
skinparam wrapWidth 250
hide circle
skinparam linetype ortho
skinparam classAttributeIconSize 0

title Part 2: Bookings, Payments & Favourites

package "bookings" {
    class Booking {
        - id : UUID PK
        - user_id : UUID FK → User
        - service_id : UUID FK → Service
        - service_slot_id : int FK → ServiceSlot (nullable)
        - itinerary_item_id : UUID FK → ItineraryItem (nullable)
        - status : enum
        - booking_from_time : datetime
        - booking_to_time : datetime
        - amount_of_people : int
        - bookers_name : str
        - special_requests : str
        - cancellation_reason : str
        - cancelled_by_role : str
        - cancelled_at : datetime
        - base_price : decimal
        - service_fee_percent : decimal
        - service_fee_amount : decimal
        - discount_percent : decimal
        - discount_amount : decimal
        - display_price : decimal
        - final_price : decimal
        - stripe_payment_intent_id : str UK
        - created_at : datetime
        - updated_at : datetime

        + user : User
        + service : Service
        + itinerary_item : ItineraryItem (nullable)
        + payments : List<PaymentEvent>
    }

    class PaymentEvent {
        - id : UUID PK
        - booking_id : UUID FK → Booking
        - event_type : str
        - stripe_payment_intent_id : str
        - amount_cents : int
        - created_at : datetime

        + booking : Booking
    }
}

package "favourites" {
    class Favourite {
        - id : UUID PK
        - user_id : UUID FK → User
        - listing_id : UUID FK → Listing
        - created_at : datetime
        - <<unique>> (user_id, listing_id)

        + user : User
        + listing : Listing
    }
}

' COMPOSITION
Booking *-- PaymentEvent

' AGGREGATION
User o-- Booking
Service o-- Booking
User o-- Favourite
Listing o-- Favourite

' ASSOCIATION
Review --> User
Favourite --> User

note top of Booking
    Package discount eligibility:
    - 3+ services in itinerary
    - $100+ total cost
    - 10% discount applied
end note

@enduml
```

---

## Part 3: Reviews, Itineraries & Lookup

```plantuml
@startuml Part3_Reviews_Itineraries_Lookup
skinparam dpi 120
skinparam defaultFontSize 10
skinparam wrapWidth 250
hide circle
skinparam linetype ortho
skinparam classAttributeIconSize 0

title Part 3: Reviews, Itineraries & Lookup

package "reviews" {
    class Review {
        - id : UUID PK
        - listing_id : UUID FK → Listing
        - user_id : UUID FK → User
        - rating : int
        - comment : str
        - created_at : datetime
        - updated_at : datetime
        - detected_language : str
        - classification_labels : str
        - classified_at : datetime
        - translated_comment : str
        - censored_comment : str

        + listing : Listing
        + user : User
        + business_reply : BusinessReply
    }

    class BusinessReply {
        - id : UUID PK
        - review_id : UUID FK → Review (unique)
        - business_id : UUID FK → Business
        - user_id : UUID FK → User
        - description : str
        - created_at : datetime
        - updated_at : datetime
    }
}

package "itineraries" {
    class Itinerary {
        - id : UUID PK
        - user_id : UUID FK → User
        - title : str
        - start_date : date
        - end_date : date
        - status : enum
        - budget_level : str
        - pace : str
        - country : str
        - interests : dict
        - total_estimated_cost : float
        - created_at : datetime
        - updated_at : datetime
        - applied_discount_id : int
        - discount_amount : decimal

        + user : User
        + items : List<ItineraryItem>
    }

    class ItineraryItem {
        - id : UUID PK
        - itinerary_id : UUID FK → Itinerary
        - listing_id : UUID FK → Listing
        - linked_booking_id : UUID FK → Booking (nullable)
        - title : str
        - description : str
        - day_date : date
        - start_at : datetime
        - end_at : datetime
        - sort_order : int
        - estimated_cost : float
        - address_snapshot : dict
        - reason_tags : dict
        - extra_metadata : dict
        - created_at : datetime
        - updated_at : datetime

        + itinerary : Itinerary
        + listing : Listing
        + booking : Booking (nullable)
    }
}

package "lookup" {
    class Interest {
        - id : UUID PK
        - name : str
        - category_id : UUID FK → InterestCategory
    }

    class InterestCategory {
        - id : UUID PK
        - name : str
        - description : str
    }

    class UserInterest {
        - user_id : UUID FK → User
        - interest_id : UUID FK → Interest
        - created_at : datetime
    }

    class ListingInterest {
        - listing_id : UUID FK → Listing
        - interest_id : UUID FK → Interest
        - created_at : datetime
    }

    class BusinessTypeInterest {
        - business_type_id : UUID FK → BusinessType
        - interest_id : UUID FK → Interest
        - created_at : datetime
    }

    class PricingConfig {
        - id : UUID PK
        - business_type_id : UUID FK → BusinessType
        - service_fee_percent : float
        - is_active : bool
        - effective_from : datetime
        - effective_to : datetime
    }

    class Discount {
        - id : UUID PK
        - name : str
        - discount_type : DiscountType enum
        - discount_percent : float
        - min_services : int
        - required_business_types : list~str~
        - min_total_cost : float
        - max_discount_amount : float
        - is_active : bool
        - valid_from : datetime
        - valid_to : datetime
        - max_uses : int
        - current_uses : int
        - description : str
    }
}

' COMPOSITION
Itinerary *-- ItineraryItem

' AGGREGATION
Listing o-- Review
User o-- Review
User o-- Itinerary
Listing o-- ItineraryItem
Business o-- BusinessReply
ItineraryItem o-- Booking
User o-- UserInterest
Listing o-- ListingInterest

' REALIZATION
BusinessType ..> PricingConfig
Interest ..> InterestCategory

' ASSOCIATION
ItineraryItem --> Listing
Booking --> ItineraryItem
Interest --> UserInterest
Interest --> ListingInterest
Interest --> BusinessTypeInterest

note top of ItineraryItem
    linked_booking_id is nullable.
    Set when item is converted to booking.
end note

@enduml
```

---

## Usage Notes

### Export Settings for A4
- **DPI**: 120 (optimized for print)
- **Font Size**: 10pt
- **Wrap Width**: 250
- **Format**: PNG or PDF

### Diagram Breakdown
- **Part 1**: Core entities - User, Business, Listing, Service and their direct relationships
- **Part 2**: Transactional entities - Booking, PaymentEvent, Favourite
- **Part 3**: Reviews, Itineraries, plus Interest/Pricing/Discount lookup tables

### PlantUML Export (VS Code)
- `Alt+D` to preview
- `Alt+P` to export as PNG