# Pricing Module - Class Diagram (PlantUML)

```plantuml
@startuml PricingModule

top to bottom direction

skinparam linetype polyline
skinparam ranksep 40
skinparam nodesep 30
skinparam classAttributeIconSize 0

hide empty members
hide circle

' =========================
' PRICING MODULE - MODELS WITH OPERATIONS
' =========================

class PlatformPricingConfig {
    +id: UUID PK
    +business_type_id: UUID FK (nullable)
    +service_fee_percent: float
    +is_active: bool
    +effective_from: datetime
    +effective_to: datetime (nullable)
    --
    +get_pricing_config(db, business_type_id): PlatformPricingConfig
    +calculate_display_price(db, listing_id, service_id): dict
    +get_listing_display_price(db, listing_id, service_id): dict
    +create_pricing_config(db, data): PlatformPricingConfig
    +update_pricing_config(db, config_id, data): PlatformPricingConfig
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' Listing (from listings module) - For price calculation
class Listing {
    +id: UUID PK
    +title: str
    +base_price: Decimal
    +business_type: UUID FK
}

' Service (from services module) - Optional service for price
class Service {
    +service_id: UUID PK
    +name: str
    +price: float
    +listing_id: UUID FK
}

' BusinessType (from businesses module) - For business-type specific pricing
class BusinessType {
    +id: UUID PK
    +name: str
}

' =========================
' CROSS-MODULE RELATIONSHIPS
' =========================

' BusinessType has PlatformPricingConfigs (1-to-many)
BusinessType "1" --> "0..*" PlatformPricingConfig : has pricing configs

' Listing uses PlatformPricingConfig for display price calculation
Listing "1" --> "0..*" PlatformPricingConfig : uses for pricing

' Service can override listing base_price
Service "1" --> Listing : offered_by

@enduml
```

## Pricing Module - Models with Operations

This diagram shows the Pricing module models and their operations.

| Model | Description |
|-------|-------------|
| **PlatformPricingConfig** | Platform fee configuration per business type |

## Key Operations

### PlatformPricingConfig

| Operation | Description |
|-----------|-------------|
| `get_pricing_config(db, business_type_id)` | Get active pricing config for a business type or global fallback |
| `calculate_display_price(db, listing_id, service_id)` | Calculate display price (base + service fee) |
| `get_listing_display_price(db, listing_id, service_id)` | Get display price for a listing |
| `create_pricing_config(db, data)` | Create new pricing configuration |
| `update_pricing_config(db, config_id, data)` | Update existing configuration |

## Pricing Calculation Formula

```
display_price = base_price + service_fee_amount
service_fee_amount = base_price × service_fee_percent
```

Where `base_price` comes from either:
- `Service.price` (if service_id provided)
- `Listing.base_price` (fallback)

## Cross-Module Connections

| Connected Module | Via Model | Relationship |
|-----------------|-----------|--------------|
| **businesses** | BusinessType | BusinessType-specific pricing configs |
| **listings** | Listing | Listing uses config for price display |
| **services** | Service | Service price can override listing base price |
