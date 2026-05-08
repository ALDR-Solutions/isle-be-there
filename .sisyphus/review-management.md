# Review Management Implementation Plan

## Status: Implementation Complete

---

## Changes Made

### Phase 1: Model Updates (Complete)
- `models.py`: Changed `Review.id` from `int` to `UUID` with `gen_random_uuid()` default
- `models.py`: Changed `BusinessReply.review_id` to `UUID` type with proper FK (CASCADE delete)
- `models.py`: Added `censored_comment` field
- `models.py`: Removed `is_flagged`, `flag_reason`, `is_visible` (no longer needed)
- `models.py`: UniqueConstraint on `(listing_id, user_id)` already exists

### Phase 2: Profanity Censorship (Complete)
- `profanity.py`: Created with `better-profanity` — `censor_text()` and `is_profane()`
- `content_moderation.py`: DELETED
- `service.py`: Uses `censor_text()` on submit — stores both original and censored

### Phase 3: Service Layer (Complete)
- `service.py`: Updated to use UUID for review IDs
- `service.py`: Added IntegrityError handling for duplicate reviews (409 response)
- `service.py`: Added `classify_review_text()` fallback function for keyword classification
- `service.py`: ML classifier falls back to keyword classification on failure
- `service.py`: Added business reply functions (create, get, update, delete)
- `service.py`: `delete_review()` — hard deletes (no status field)

### Phase 4: Router Updates (Complete)
- `router.py`: All `review_id` params changed from `int` to `UUID`
- `router.py`: Removed toggle visibility endpoint (deleted)
- `router.py`: Added reply endpoints (GET, POST, PUT, DELETE /{review_id}/reply)
- `schemas.py`: Updated UUID types for Review and BusinessReply

### Phase 5: Keyword Classifier Extended (Complete)
- `keyword_classifier.py`: Added Hotel and Restaurant categories
- Hotel: cleanliness, service_quality, room_quality, value, location, amenities
- Restaurant: food_quality, service_quality, ambiance, value, cleanliness, location
- Fallback works for all 5 business types

### Phase 6: Frontend Updates (Complete)
- `ListingDetail.vue`: Label tabs sorted by frequency, "(none)" excluded from tabs
- `ListingDetail.vue`: Global censorship toggle ("Show Original" / "Show Censored")
- `ListingDetail.vue`: Translation display when `detected_language !== 'en'`
- `ListingDetail.vue`: Only reviews with profanity are affected by toggle

### Phase 7: Permissions (Complete)
- `permissions.py`: Updated `require_review_owner` to accept `UUID` instead of `int`

---

## Database Migration Required
- Run `alembic revision --autogenerate` on develop branch to generate migration
- Migration will:
  - Change `reviews.id` from int to UUID
  - Add `censored_comment` column
  - Remove `is_flagged`, `flag_reason`, `is_visible` columns
  - Change `business_replies.review_id` from bigint to UUID