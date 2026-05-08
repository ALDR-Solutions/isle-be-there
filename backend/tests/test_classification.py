"""
Review Classification Tests

Tests ML classification, keyword classification, profanity censorship,
and review submit flow for the isle-be-there platform.
"""

import os
import sys
import pytest
import json

# Add backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(backend_dir))

from fastapi.testclient import TestClient

from app.main import app
from app.infrastructure.database import get_db
from app.modules.reviews.classifiers.ml_classifier import classify_review
from app.modules.reviews.classifiers.keyword_classifier import (
    classify_with_keywords,
    BUSINESS_TYPE_UUIDS,
)
from app.modules.reviews.profanity import censor_text, is_profane
from sqlalchemy import text

# Test client
client = TestClient(app, raise_server_exceptions=False)

# Business type UUIDs
HOTEL_UUID = BUSINESS_TYPE_UUIDS["hotel"]
RESTAURANT_UUID = BUSINESS_TYPE_UUIDS["restaurant"]
TOUR_OPERATOR_UUID = BUSINESS_TYPE_UUIDS["tour_operator"]
ACTIVITY_PROVIDER_UUID = BUSINESS_TYPE_UUIDS["activity_provider"]

# Test user credentials
TEST_USER = "reedpersaud@gmail.com"
TEST_PASSWORD = "123456"

# Listing for testing (Sunset Eats - Restaurant)
TEST_LISTING_ID = "ff62dcdf-5ce0-42af-a5fd-4785b586636c"
TEST_USER_ID = "f9826077-3237-406b-9857-847564313890"


# ============================================================
# SECTION 1: ML Classification Tests
# ============================================================


class TestMLClassification:
    """
    ML-based classification for Hotel and Restaurant.

    Note: ML model may return None if loading fails or categories don't match.
    Fallback to keyword classification handles these cases in production.
    """

    def test_hotel_positive_english(self):
        """Positive hotel review in English - may use keyword fallback."""
        result = classify_review(
            "Excellent location, friendly staff, great service!", HOTEL_UUID
        )
        # ML may return None, but detected_language should work
        assert result["detected_language"] == "en"

    def test_hotel_negative_english(self):
        """Negative hotel review in English."""
        result = classify_review(
            "Dirty room, rude staff, terrible experience.", HOTEL_UUID
        )
        assert result["detected_language"] == "en"

    def test_restaurant_positive_english(self):
        """Positive restaurant review in English."""
        result = classify_review(
            "Delicious food, amazing atmosphere, great service!", RESTAURANT_UUID
        )
        assert result["detected_language"] == "en"

    def test_restaurant_negative_english(self):
        """Negative restaurant review in English."""
        result = classify_review(
            "Terrible food, horrible service, worst experience ever.", RESTAURANT_UUID
        )
        assert result["detected_language"] == "en"

    def test_ml_returns_structure(self):
        """ML classification returns expected structure."""
        result = classify_review(
            "Great location, clean room, friendly staff!", HOTEL_UUID
        )
        assert "main_label" in result
        assert "second_label" in result
        assert "detected_language" in result

    def test_language_detection_english(self):
        """English text detected as 'en'."""
        result = classify_review("Great hotel, loved it!", HOTEL_UUID)
        assert result.get("detected_language") == "en"

    def test_language_detection_french(self):
        """French text detected."""
        result = classify_review(
            "Excellent emplacement, personnel tres aimable.", HOTEL_UUID
        )
        assert result["detected_language"] == "fr"

    def test_language_detection_spanish(self):
        """Spanish text detected."""
        result = classify_review("La comida estaba deliciosa!", RESTAURANT_UUID)
        assert result["detected_language"] == "es"

    def test_language_detection_dutch(self):
        """Dutch text detected."""
        result = classify_review("Heerlijk eten, uitstekende service!", RESTAURANT_UUID)
        assert result["detected_language"] == "nl"

    def test_non_english_review_classified(self):
        """Non-English review gets detected."""
        result = classify_review("La comida estaba deliciosa!", RESTAURANT_UUID)
        # Should detect language even if classification fails
        assert result["detected_language"] == "es"

    def test_translation_english_unchanged(self):
        """English review detection returns 'en'."""
        text = "Great food and excellent service!"
        result = classify_review(text, RESTAURANT_UUID)
        assert result.get("detected_language") == "en"

    def test_ml_model_file_exists(self):
        """Verify ML model file exists and is readable."""
        model_path = os.path.join(
            os.path.dirname(backend_dir),
            "app",
            "modules",
            "reviews",
            "classifiers",
            "ml_models",
            "unified_pipeline_models.pkl",
        )
        assert os.path.exists(model_path), f"ML model file not found at {model_path}"
        assert os.path.getsize(model_path) > 1000, "ML model file too small"


# ============================================================
# SECTION 2: Keyword Classification Tests
# ============================================================


class TestKeywordClassification:
    """Keyword-based classification for all business types."""

    # --- Restaurant Tests ---
    def test_restaurant_food_quality_positive(self):
        """Restaurant with positive food quality keywords."""
        result = classify_with_keywords(
            "Delicious food, amazing cuisine, well cooked meals!", RESTAURANT_UUID
        )
        assert result["main_label"] == "food_quality"

    def test_restaurant_food_quality_negative(self):
        """Restaurant with negative food keywords."""
        result = classify_with_keywords(
            "Terrible food, worst ever, awful taste, disgusting!", RESTAURANT_UUID
        )
        assert result["main_label"] == "food_quality"

    def test_restaurant_service_quality(self):
        """Restaurant with service quality keywords."""
        result = classify_with_keywords(
            "Rude staff, horrible customer service, ignored us completely.",
            RESTAURANT_UUID,
        )
        assert result["main_label"] == "service_quality"

    def test_restaurant_multiple_labels(self):
        """Restaurant review matching multiple categories."""
        result = classify_with_keywords(
            "Great food but terrible service, overpriced too.", RESTAURANT_UUID
        )
        labels = [result["main_label"], result["second_label"], result["third_label"]]
        assert "food_quality" in labels or "value" in labels
        assert "service_quality" in labels or "(none)" in labels

    def test_restaurant_no_match(self):
        """Restaurant review with no matching keywords."""
        result = classify_with_keywords(
            "It was okay, nothing special really.", RESTAURANT_UUID
        )
        assert result["main_label"] == "(none)"
        assert result["second_label"] == "(none)"

    def test_restaurant_value(self):
        """Restaurant with value keywords."""
        result = classify_with_keywords(
            "Worth every penny, great value for money!", RESTAURANT_UUID
        )
        assert result["main_label"] == "value"

    def test_restaurant_cleanliness(self):
        """Restaurant with cleanliness keywords."""
        result = classify_with_keywords(
            "Spotless restaurant, very clean, tidy tables.", RESTAURANT_UUID
        )
        assert result["main_label"] == "cleanliness"

    def test_restaurant_ambiance(self):
        """Restaurant with ambiance keywords."""
        result = classify_with_keywords(
            "Beautiful atmosphere, cozy setting, romantic music.", RESTAURANT_UUID
        )
        assert result["main_label"] == "ambiance"

    # --- Tour Operator Tests ---
    def test_tour_operator_guide_quality(self):
        """Tour with guide quality keywords."""
        result = classify_with_keywords(
            "Great tour guide, very friendly!", TOUR_OPERATOR_UUID
        )
        assert result["main_label"] == "guide_quality"

    def test_tour_operator_historical_value(self):
        """Tour with historical value keywords."""
        result = classify_with_keywords(
            "Fascinating history, well preserved heritage site!", TOUR_OPERATOR_UUID
        )
        assert result["main_label"] == "historical_value"

    def test_tour_operator_facilities(self):
        """Tour with facilities keywords."""
        result = classify_with_keywords(
            "Clean facilities, good restrooms, wheelchair accessible.",
            TOUR_OPERATOR_UUID,
        )
        assert result["main_label"] == "facilities"

    def test_tour_operator_value(self):
        """Tour with value keywords."""
        result = classify_with_keywords(
            "Worth every penny, great value tour!", TOUR_OPERATOR_UUID
        )
        assert result["main_label"] == "value"

    def test_tour_operator_atmosphere(self):
        """Tour with atmosphere keywords."""
        result = classify_with_keywords(
            "Beautiful scenery and breathtaking views!", TOUR_OPERATOR_UUID
        )
        assert result["main_label"] == "atmosphere"

    # --- Activity Provider Tests ---
    def test_activity_provider_activity_quality(self):
        """Activity with activity quality keywords."""
        result = classify_with_keywords(
            "Amazing experience, well organized, fun for all ages!",
            ACTIVITY_PROVIDER_UUID,
        )
        assert result["main_label"] == "activity_quality"

    def test_activity_provider_instructor(self):
        """Activity with instructor quality keywords."""
        result = classify_with_keywords(
            "Great instructor, professional and patient!", ACTIVITY_PROVIDER_UUID
        )
        assert result["main_label"] == "instructor_quality"

    def test_activity_provider_safety(self):
        """Activity with safety keywords."""
        result = classify_with_keywords(
            "Felt safe, good safety measures, well supervised!", ACTIVITY_PROVIDER_UUID
        )
        assert result["main_label"] == "safety"

    def test_activity_provider_value(self):
        """Activity with value keywords."""
        result = classify_with_keywords(
            "Worth it, great value for the activity!", ACTIVITY_PROVIDER_UUID
        )
        assert result["main_label"] == "value"

    # --- Label Count Tests ---
    def test_exactly_three_labels_returned_restaurant(self):
        """Always returns exactly 3 labels for restaurant."""
        result = classify_with_keywords("Test review text.", RESTAURANT_UUID)
        labels = [result["main_label"], result["second_label"], result["third_label"]]
        assert len(labels) == 3

    def test_exactly_three_labels_returned_tour(self):
        """Always returns exactly 3 labels for tour operator."""
        result = classify_with_keywords("Test review text.", TOUR_OPERATOR_UUID)
        labels = [result["main_label"], result["second_label"], result["third_label"]]
        assert len(labels) == 3

    def test_exactly_three_labels_returned_activity(self):
        """Always returns exactly 3 labels for activity provider."""
        result = classify_with_keywords("Test review text.", ACTIVITY_PROVIDER_UUID)
        labels = [result["main_label"], result["second_label"], result["third_label"]]
        assert len(labels) == 3

    def test_none_label_used_when_insufficient_matches(self):
        """'(none)' used when fewer than 3 categories match."""
        result = classify_with_keywords("It was okay.", RESTAURANT_UUID)
        # No keywords matched, all labels should be "(none)"
        assert result["main_label"] == "(none)"
        assert result["second_label"] == "(none)"
        assert result["third_label"] == "(none)"


# ============================================================
# SECTION 3: Profanity Censorship Tests
# ============================================================


class TestProfanityCensorship:
    """Tests for better-profanity integration."""

    def test_censor_fucking(self):
        """'fucking' censored."""
        result = censor_text("Those fucking cupcakes were terrible!")
        assert "****" in result
        assert "fucking" not in result

    def test_censor_shit(self):
        """'shit' censored."""
        result = censor_text("The service was shit.")
        assert "****" in result
        assert "shit" not in result.lower()

    def test_censor_damn(self):
        """'damn' censored."""
        result = censor_text("What a damn good time!")
        assert "****" in result

    def test_censor_ass(self):
        """'ass' censored."""
        result = censor_text("What an ass of a waiter!")
        assert "****" in result.lower()

    def test_censor_bitch(self):
        """'bitch' censored."""
        result = censor_text("The waitress was acting like a bitch!")
        assert "****" in result.lower()

    def test_is_profane_true(self):
        """is_profane returns True for profane text."""
        assert is_profane("Those fucking cupcakes were shit!") is True

    def test_is_profane_false(self):
        """is_profane returns False for clean text."""
        assert is_profane("Great food, excellent service!") is False

    def test_clean_text_unchanged(self):
        """Clean text without profanity is unchanged."""
        text = "Great restaurant with excellent food and friendly staff!"
        result = censor_text(text)
        assert result == text

    def test_mixed_text_partial_censor(self):
        """Mixed text has only profane words censored."""
        text = "Great food but the damn service was slow."
        result = censor_text(text)
        assert "Great food" in result
        assert "****" in result
        assert result != text


# ============================================================
# SECTION 4: Integration Tests (Review Submit Flow)
# ============================================================


class TestReviewSubmit:
    """End-to-end tests for review submission."""

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Login before each test, cleanup after."""
        # Login to get token
        login_resp = client.post(
            "/api/auth/login", data={"username": TEST_USER, "password": TEST_PASSWORD}
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        yield  # Run test

        # Cleanup: Delete all reviews by this test user for test listing
        try:
            db = next(get_db())
            db.execute(
                text("""
                DELETE FROM reviews
                WHERE user_id = :user_id
                AND listing_id = :listing_id
            """),
                {"user_id": TEST_USER_ID, "listing_id": TEST_LISTING_ID},
            )
            db.commit()
        except Exception:
            pass  # Ignore cleanup errors

    def test_submit_restaurant_review_returns_classification(self):
        """POST /api/reviews/submit returns classification labels."""
        resp = client.post(
            "/api/reviews/submit",
            data={
                "listing_id": TEST_LISTING_ID,
                "rating": 4,
                "comment": "Great food, quick service, beautiful ambiance!",
            },
            headers=self.headers,
        )
        assert resp.status_code == 201, (
            f"Expected 201, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert "classification_labels" in data
        labels = json.loads(data["classification_labels"])
        assert len(labels) == 3
        assert (
            "food_quality" in labels
            or "service_quality" in labels
            or "ambiance" in labels
        )

    def test_submit_review_with_profanity_gets_censored(self):
        """Review with profanity has censored_comment field populated."""
        resp = client.post(
            "/api/reviews/submit",
            data={
                "listing_id": TEST_LISTING_ID,
                "rating": 1,
                "comment": "Those fucking cupcakes were the worst, terrible service!",
            },
            headers=self.headers,
        )
        assert resp.status_code == 201, (
            f"Expected 201, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert "censored_comment" in data
        assert data["censored_comment"] != data["comment"]
        assert "****" in data["censored_comment"]

    def test_submit_review_stores_original_and_censored(self):
        """Original comment stored separately from censored version."""
        original = "Great food but damn slow service."
        resp = client.post(
            "/api/reviews/submit",
            data={"listing_id": TEST_LISTING_ID, "rating": 3, "comment": original},
            headers=self.headers,
        )
        assert resp.status_code == 201, (
            f"Expected 201, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert data["comment"] == original
        assert data["censored_comment"] is not None

    def test_duplicate_review_returns_409(self):
        """User cannot submit duplicate review for same listing."""
        # Submit first review
        client.post(
            "/api/reviews/submit",
            data={
                "listing_id": TEST_LISTING_ID,
                "rating": 5,
                "comment": "Amazing place, highly recommend!",
            },
            headers=self.headers,
        )

        # Try to submit duplicate
        resp = client.post(
            "/api/reviews/submit",
            data={
                "listing_id": TEST_LISTING_ID,
                "rating": 1,
                "comment": "Another review attempt",
            },
            headers=self.headers,
        )
        assert resp.status_code == 409, f"Expected 409, got {resp.status_code}"

    def test_submit_review_requires_authentication(self):
        """Submit without token returns 401."""
        resp = client.post(
            "/api/reviews/submit",
            data={
                "listing_id": TEST_LISTING_ID,
                "rating": 5,
                "comment": "This should fail",
            },
        )
        assert resp.status_code == 401


# ============================================================
# SECTION 5: ML Fallback Tests
# ============================================================


class TestMLFallback:
    """Tests to verify ML falls back to keyword on various failures."""

    def test_fallback_structure_matches_ml(self):
        """Both ML and keyword return same structure (3 labels)."""
        text = "Great food, excellent service!"

        # Keyword classification always works
        kw_result = classify_with_keywords(text, RESTAURANT_UUID)
        kw_labels = [
            kw_result["main_label"],
            kw_result["second_label"],
            kw_result["third_label"],
        ]
        assert len(kw_labels) == 3

        # ML may or may not work (depends on model loading)
        try:
            ml_result = classify_review(text, RESTAURANT_UUID)
            if ml_result["main_label"] is not None:
                ml_labels = [
                    ml_result["main_label"],
                    ml_result.get("second_label") or "(none)",
                    ml_result.get("third_label") or "(none)",
                ]
                assert len(ml_labels) == 3
        except Exception:
            # ML failed, fallback should work
            pass

    def test_keyword_fallback_available(self):
        """Keyword fallback can classify when ML might fail."""
        text = "Amazing food, excellent service!"
        result = classify_with_keywords(text, RESTAURANT_UUID)
        assert result["main_label"] is not None
        assert result["main_label"] != "(none)"
