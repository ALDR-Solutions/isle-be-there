# Discounts Module - Class Diagram (PlantUML)

```plantuml
@startuml DiscountsModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

' =========================
' DISCOUNT MODULE - MODELS WITH OPERATIONS
' =========================

class Discount {
    +id: UUID PK
    +name: str
    +discount_type: DiscountType
    +discount_percent: float
    +min_services: int (nullable)
    +required_business_types: list[str] (nullable)
    +min_total_cost: float (nullable)
    +max_discount_amount: float (nullable)
    +is_active: bool
    +valid_from: datetime
    +valid_to: datetime (nullable)
    +max_uses: int (nullable)
    +current_uses: int
    +description: str (nullable)
    --
    +get_active_discounts(db, discount_type): list[Discount]
    +get_discount_by_id(db, discount_id): Discount
    +check_package_discount_eligibility(db, itinerary_or_id): dict
    +get_eligible_package_discount(db, itinerary_or_id): Discount | None
    +apply_discount_to_itinerary(db, itinerary_id, discount_id): Itinerary
    +calculate_discount_for_amount(display_price, discount_percent, max_discount_amount): float
    +create_discount(db, data): Discount
    +update_discount(db, discount_id, data): Discount
    +increment_discount_usage(db, discount_id): Discount
    +get_or_create_package_discount(db): Discount
}

enum DiscountType {
    PACKAGE
    VIP
    REPEAT_CUSTOMER
    HOLIDAY
    MANUAL
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' Itinerary (from itineraries module) - Can have discount applied
class Itinerary {
    +id: UUID PK
    +title: str
    +applied_discount_id: int FK (nullable)
    +discount_amount: float (nullable)
}

' Listing (from listings module) - For business type checking
class Listing {
    +id: UUID PK
    +title: str
    +business_type: UUID FK
}

' ItineraryItem (from itineraries module) - For service counting
class ItineraryItem {
    +id: UUID PK
    +itinerary_id: UUID FK
    +listing_id: UUID FK
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' Itinerary applies Discount (0..1-to-1)
Itinerary "0..1" --> "1" Discount : applies

' Discount eligibility checked against ItineraryItems
Itinerary "1" *-- "0..*" ItineraryItem : contains
ItineraryItem --> Listing : references

' Discount checked against required BusinessTypes
Listing --> BusinessType : categorized_by

@enduml
```

## Discounts Module - Models with Operations

This diagram shows the Discounts module models and their operations.

| Model | Description |
|-------|-------------|
| **Discount** | Discount entity with eligibility rules |
| **DiscountType** | Enum: PACKAGE, VIP, REPEAT_CUSTOMER, HOLIDAY, MANUAL |

## Key Operations

### Discount

| Operation | Description |
|-----------|-------------|
| `get_active_discounts(db, discount_type)` | Get all active discounts, optionally filtered by type |
| `get_discount_by_id(db, discount_id)` | Get a specific discount by ID |
| `check_package_discount_eligibility(db, itinerary_or_id)` | Check if an itinerary qualifies for package discount |
| `get_eligible_package_discount(db, itinerary_or_id)` | Get the eligible package discount for an itinerary |
| `apply_discount_to_itinerary(db, itinerary_id, discount_id)` | Apply a discount to an itinerary |
| `calculate_discount_for_amount(display_price, discount_percent, max_discount_amount)` | Calculate discount amount with cap |
| `create_discount(db, data)` | Create a new discount |
| `update_discount(db, discount_id, data)` | Update an existing discount |
| `increment_discount_usage(db, discount_id)` | Increment usage counter |
| `get_or_create_package_discount(db)` | Get or create default package discount |

## Package Discount Eligibility Rules

A package discount is eligible when:
1. Discount is active and within valid date range
2. Itinerary has `min_services` or more items
3. Itinerary total cost meets `min_total_cost`
4. Usage count is below `max_uses`
5. All required business types are present in itinerary

## Cross-Module Connections

| Connected Module | Via Model | Relationship |
|-----------------|-----------|--------------|
| **itineraries** | Itinerary | Itinerary can have discount applied (applied_discount_id FK) |
| **listings** | Listing, ItineraryItem | Business types checked for eligibility |
