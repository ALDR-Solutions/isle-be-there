# Isle Be There - ERD Diagrams (3-Part A4)

## Part 1: Users & Businesses

```plantuml
@startuml Part1_Users_Businesses
skinparam dpi 120
skinparam defaultFontSize 10
skinparam wrapWidth 280
skinparam pageSize 1080 1080
hide circle
skinparam linetype ortho

title Part 1: Users & Businesses

left to right direction

' =========================
' CORE USER TABLE
' =========================
entity users {
  *id : uuid
  email : text
  hashed_password : text
  username : text
  first_name : text
  last_name : text
  is_active : boolean
  created_at : timestamptz
  updated_at : timestamptz
  avatar_url : text
  phone : text
  birth_date : date
  interests_handled : boolean
  is_verified : boolean
  verification_token : text
  user_type : user_types
}

' =========================
' BUSINESSES
' =========================
entity businesses {
  *id : uuid
  business_name : text
  description : text
  business_email : varchar
  phone : varchar
  address : text
  website : varchar
  logo_url : varchar
  is_verified : boolean
  created_at : timestamptz
  user_id : uuid
  latitude : float
  longitude : float
}

entity business_employees {
  *id : uuid
  business_id : uuid
  employee_id : uuid
  role : varchar
}

entity business_types {
  *id : uuid
  created_at : timestamptz
  name : text
  description : text
}

entity business_replies {
  *id : bigint
  created_at : timestamptz
  business_id : uuid
  description : text
  review_id : uuid
}

entity business_type_interests {
  *business_type_id : uuid
  *interest_id : uuid
  created_at : timestamptz
}

' =========================
' RELATIONSHIPS
' =========================
users ||--o{ businesses : owns
users ||--o{ business_employees : employee
users ||--o{ user_interests

businesses ||--o{ listings
businesses ||--o{ business_employees
businesses ||--o{ business_replies

business_types ||--o{ listings
business_types ||--o{ pricing_configs
business_types ||--o{ business_type_interests

pricing_configs }o--|| business_types

@enduml
```

---

## Part 2: Listings & Services

```plantuml
@startuml Part2_Listings_Services
skinparam dpi 120
skinparam defaultFontSize 10
skinparam wrapWidth 280
skinparam pageSize 1080 1080
hide circle
skinparam linetype ortho

title Part 2: Listings & Services

left to right direction

' =========================
' LISTINGS + SERVICES
' =========================
entity listings {
  *id : uuid
  created_at : timestamptz
  business_id : uuid
  title : text
  description : text
  address : jsonb
  base_price : numeric
  business_type : uuid
  updated_at : timestamp
  image_urls : array
  status : statuses
  phone_number : text
  email_address : text
  location : user-defined
  embedding : user-defined
  details : jsonb
  start_time : timestamptz
  end_time : timestamptz
}

entity services {
  *service_id : uuid
  created_at : timestamptz
  name : text
  description : text
  price : double precision
  season_price : double precision
  capacity : smallint
  availability : jsonb
  type_data : jsonb
  updated_at : timestamp
  listing_id : uuid
  status : status_types
}

entity service_slots {
  *id : int
  service_id : uuid
  day_of_week : int
  start_time : time
  end_time : time
  capacity : int
}

entity listing_hours {
  *id : int
  listing_id : uuid
  day_of_week : int
  open_time : time
  close_time : time
}

entity listing_interests {
  *listing_id : uuid
  *interest_id : uuid
  created_at : timestamptz
}

entity employee_listings {
  *id : uuid
  employee_id : uuid
  listing_id : uuid
}

' =========================
' RELATIONSHIPS
' =========================
listings ||--o{ services
listings ||--o{ reviews
listings ||--o{ favourites
listings ||--o{ listing_interests
listings ||--o{ listing_hours
listings ||--o{ employee_listings

services ||--o{ service_slots
services ||--o{ bookings

@enduml
```

---

## Part 3: Bookings, Itineraries, Reviews & Pricing

```plantuml
@startuml Part3_Bookings_Itineraries_Reviews
skinparam dpi 120
skinparam defaultFontSize 10
skinparam wrapWidth 280
skinparam pageSize 1080 1080
hide circle
skinparam linetype ortho

title Part 3: Bookings, Itineraries, Reviews & Pricing

left to right direction

' =========================
' BOOKINGS SYSTEM
' =========================
entity bookings {
  *id : uuid
  created_at : timestamptz
  user_id : uuid
  service_id : uuid
  itinerary_item_id : uuid
  status : user-defined
  booking_from_time : timestamp
  booking_to_time : timestamp
  updated_at : timestamptz
  amount_of_people : int
  special_requests : text
  bookers_name : text
  base_price : numeric
  service_fee_percent : numeric
  service_fee_amount : numeric
  discount_percent : numeric
  discount_amount : numeric
  display_price : numeric
  final_price : numeric
  stripe_payment_intent_id : text
}

entity payment_events {
  *id : uuid
  booking_id : uuid
  event_type : text
  stripe_payment_intent_id : text
  amount_cents : int
  created_at : timestamptz
}

' =========================
' ITINERARIES
' =========================
entity itineraries {
  *id : uuid
  user_id : uuid
  title : text
  start_date : date
  end_date : date
  status : text
  budget_level : text
  pace : text
  total_budget : float
  strict_budget : boolean
  city : text
  country : text
  interests : jsonb
  preferred_business_types : jsonb
  total_estimated_cost : float
  created_at : timestamptz
  updated_at : timestamptz
  applied_discount_id : int
  discount_amount : numeric
}

entity itinerary_items {
  *id : uuid
  itinerary_id : uuid
  listing_id : uuid
  linked_booking_id : uuid
  item_type : text
  title : text
  description : text
  day_date : date
  start_at : timestamp
  end_at : timestamp
  sort_order : int
  estimated_cost : float
  address_snapshot : jsonb
  reason_tags : jsonb
  extra_metadata : jsonb
  created_at : timestamptz
  updated_at : timestamptz
}

' =========================
' REVIEWS + FAVOURITES
' =========================
entity reviews {
  *id : uuid
  created_at : timestamptz
  listing_id : uuid
  user_id : uuid
  rating : int
  comment : text
  updated_at : timestamptz
  detected_language : text
  classification_labels : text
  classified_at : timestamptz
  translated_comment : text
  censored_comment : text
}

entity favourites {
  *id : uuid
  created_at : timestamptz
  listing_id : uuid
  user_id : uuid
}

' =========================
' INTEREST SYSTEM
' =========================
entity interest_categories {
  *id : uuid
  created_at : timestamptz
  name : text
  description : text
}

entity interests {
  *id : uuid
  created_at : timestamptz
  name : varchar
  category_id : uuid
}

entity user_interests {
  *user_id : uuid
  *interest_id : uuid
  created_at : timestamptz
}

' =========================
' DISCOUNTS + PRICING
' =========================
entity discounts {
  *id : uuid
  name : varchar
  discount_type : user-defined
  discount_percent : float
  min_services : int
  required_business_types : array
  min_total_cost : float
  max_discount_amount : float
  is_active : boolean
  valid_from : timestamp
  valid_to : timestamp
  max_uses : int
  current_uses : int
  description : text
}

entity pricing_configs {
  *id : uuid
  business_type_id : uuid
  service_fee_percent : float
  is_active : boolean
  effective_from : timestamp
  effective_to : timestamp
}

' =========================
' RELATIONSHIPS
' =========================
users ||--o{ bookings
users ||--o{ reviews
users ||--o{ favourites
users ||--o{ itineraries
users ||--o{ user_interests

bookings ||--o{ payment_events

itineraries ||--o{ itinerary_items

itinerary_items ||--o{ bookings

reviews ||--o{ business_replies

interests ||--o{ user_interests
interests ||--o{ listing_interests
interests ||--o{ business_type_interests

interest_categories ||--o{ interests

@enduml
```

---

## Usage Notes

### Export Settings for A4
- **DPI**: 120 (optimized for print)
- **Font Size**: 10pt
- **Wrap Width**: 280
- **Format**: PNG or PDF
- **Layout**: Horizontal (left to right)

### Diagram Breakdown
- **Part 1**: Users, Businesses, Business Employees, Business Types, Business Replies
- **Part 2**: Listings, Services, Service Slots, Listing Hours, Employee Listings
- **Part 3**: Bookings, Payments, Itineraries, Itinerary Items, Reviews, Favourites, Interests, Discounts, Pricing

### PlantUML Export (VS Code)
- `Alt+D` to preview
- `Alt+P` to export as PNG

### Cross-Diagram Relationships
Note that some relationships reference entities in other parts:
- `business_types ||--o{ business_type_interests` → Part 1
- `listings ||--o{ listing_interests` → Part 2
- `user_interests` → Part 1 (Users) to Part 3 (Interests)
- `employee_listings` → Part 1 (Users) to Part 2 (Listings)