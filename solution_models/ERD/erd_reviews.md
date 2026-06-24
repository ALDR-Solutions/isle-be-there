# Isle Be There - Reviews Function ERD

```plantuml
@startuml Reviews_Function
skinparam dpi 120
skinparam defaultFontSize 10
skinparam wrapWidth 280
hide circle
skinparam linetype ortho

title Reviews Function - Entity Relationship Diagram

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

entity business_replies {
  *id : bigint
  created_at : timestamptz
  business_id : uuid
  description : text
  review_id : uuid
}

entity users {
  *id : uuid
  email : text
  username : text
  first_name : text
  last_name : text
  is_active : boolean
  created_at : timestamptz
  updated_at : timestamptz
  user_type : user_types
}

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
  location : geography
  details : jsonb
}

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
  location : geography
}

users ||--o{ reviews  
listings ||--o{ reviews 
reviews ||--o{ business_replies 
businesses ||--o{ business_replies 

@enduml
```

## Entity Summary

### Core Entities

| Entity | Description |
|--------|-------------|
| reviews | User reviews for listings with rating and comment |
| business_replies | Business owner replies to reviews |

### Supporting Entities

| Entity | Description |
|--------|-------------|
| users | User who writes the review |
| listings | Listing being reviewed |
| businesses | Business that can reply to reviews |

## Review Flow

Users write reviews for listings with a rating (1-5) and comment. Businesses can reply to reviews. Reviews have AI-assisted language detection, classification, translation, and content moderation.

## Rating System

Reviews include a rating integer. Comments may be processed for:
- Language detection (detected_language)
- Content classification (classification_labels)
- Translation (translated_comment)
- Content moderation (censored_comment)

## PlantUML Legend

| Symbol | Meaning |
|--------|---------|
| ||--o{ | One-to-Many |
| }o--|| | Many-to-One |
| * | Primary Key |