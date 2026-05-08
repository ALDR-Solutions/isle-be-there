"""Keyword-based classifier for Hotel, Restaurant, Tour Operator, and Activity Provider reviews."""

import re

BUSINESS_TYPE_UUIDS = {
    "hotel": "390a6943-b75a-465b-a09b-560e7522682c",
    "restaurant": "b155ad8f-91e8-4cee-9384-de3eb498bec5",
    "tour_operator": "6c9556f5-a0f8-4b1d-be0d-31e618e3e193",
    "activity_provider": "82587fcf-c462-4547-9b2f-1fd972a72553",
}

KEYWORD_CATEGORIES = {
    BUSINESS_TYPE_UUIDS["tour_operator"]: {
        "guide_quality": [
            "knowledgeable guide",
            "great tour guide",
            "informative guide",
            "expert guide",
            "friendly guide",
            "excellent guide",
            "bad guide",
            "uninformed guide",
            "boring guide",
            "unprofessional",
            "rude guide",
            "missing information",
        ],
        "historical_value": [
            "rich history",
            "fascinating history",
            "important heritage",
            "interesting history",
            "well preserved",
            "educational",
            "no history",
            "boring history",
            "poorly preserved",
            "disappointing",
            "lack of information",
        ],
        "facilities": [
            "clean facilities",
            "good restrooms",
            "accessible",
            "well maintained",
            "wheelchair friendly",
            "clean",
            "dirty restrooms",
            "poor facilities",
            "not accessible",
            "broken",
            "poorly maintained",
            "unsanitary",
        ],
        "value": [
            "worth it",
            "great value",
            "affordable",
            "good price",
            "excellent tour value",
            "overpriced",
            "expensive",
            "not worth it",
            "tour too short",
            "poor value",
        ],
        "atmosphere": [
            "beautiful scenery",
            "amazing views",
            "stunning",
            "breathtaking",
            "impressive",
            "fascinating",
            "boring",
            "disappointing",
            "underwhelming",
            "nothing special",
            "dull",
        ],
        "information": [
            "great audio guide",
            "good signage",
            "informative displays",
            "excellent explanations",
            "detailed plaques",
            "poor signage",
            "no information",
            "missing plaques",
            "confusing",
            "audio guide broken",
            "lack of info",
        ],
    },
    BUSINESS_TYPE_UUIDS["activity_provider"]: {
        "activity_quality": [
            "amazing experience",
            "great activity",
            "well organized",
            "excellent program",
            "fun for all ages",
            "loved it",
            "fantastic",
            "boring activity",
            "disappointing",
            "poorly organized",
            "not as described",
            "waste of money",
        ],
        "instructor_quality": [
            "great instructor",
            "professional",
            "patient",
            "helpful",
            "knowledgeable",
            "rude instructor",
            "unprofessional",
            "unhelpful",
            "poor instruction",
        ],
        "safety": [
            "felt safe",
            "secure",
            "good safety measures",
            "well supervised",
            "unsafe",
            "dangerous",
            "poor safety",
            "no supervision",
            "risky",
        ],
        "value": [
            "worth it",
            "great value",
            "affordable",
            "good price",
            "excellent value",
            "overpriced",
            "expensive",
            "not worth it",
            "too pricey",
            "poor value",
        ],
        "facilities": [
            "clean facilities",
            "good equipment",
            "well maintained",
            "modern gear",
            "dirty facilities",
            "broken equipment",
            "poor maintenance",
            "worn out gear",
        ],
        "booking_experience": [
            "easy booking",
            "smooth reservation",
            "great customer service",
            "difficult booking",
            "booking issues",
            "poor communication",
            "cancelled last minute",
        ],
    },
    BUSINESS_TYPE_UUIDS["hotel"]: {
        "cleanliness": [
            "clean",
            "spotless",
            "immaculate",
            "tidy",
            "neat",
            "well maintained",
            "dirty",
            "filthy",
            "dusty",
            "stained",
            "grimy",
            "unclean",
            "smelly",
            "moldy",
        ],
        "service_quality": [
            "friendly staff",
            "professional",
            "helpful",
            "welcoming",
            "attentive",
            "courteous",
            "rude staff",
            "unhelpful",
            "slow service",
            "dismissive",
            "unprofessional",
        ],
        "room_quality": [
            "comfortable bed",
            "spacious room",
            "cozy",
            "nice room",
            "well appointed",
            "cramped",
            "small room",
            "uncomfortable bed",
            "broken AC",
            "noisy",
            "dark",
        ],
        "value": [
            "worth it",
            "great value",
            "affordable",
            "good price",
            "excellent value",
            "overpriced",
            "expensive",
            "not worth it",
            "too pricey",
            "poor value",
        ],
        "location": [
            "great location",
            "central",
            "easy access",
            "convenient",
            "quiet area",
            "good neighborhood",
            "bad location",
            "far from center",
            "noisy area",
            "difficult to find",
            "unsafe neighborhood",
        ],
        "amenities": [
            "great amenities",
            "pool",
            "gym",
            "free wifi",
            "breakfast included",
            "spa",
            "no amenities",
            "broken wifi",
            "no pool",
            "no gym",
            "poor breakfast",
        ],
    },
    BUSINESS_TYPE_UUIDS["restaurant"]: {
        "food_quality": [
            "delicious food",
            "great food",
            "amazing cuisine",
            "well cooked",
            "fresh ingredients",
            "bad food",
            "cold food",
            "overcooked",
            "undercooked",
            "bland",
            "tasteless",
            "disappointing food",
            "worst food",
            "terrible food",
            "awful food",
            "disgusting",
            "horrible",
            "worst",
        ],
        "service_quality": [
            "friendly staff",
            "attentive",
            "excellent service",
            "professional",
            "quick service",
            "slow service",
            "rude staff",
            "unattentive",
            "poor service",
            "ignored",
            "dismissive",
            "horrible service",
            "terrible service",
            "worst service",
            "bad service",
            "customer service",
            "rude",
            "unhelpful",
        ],
        "ambiance": [
            "great atmosphere",
            "cozy",
            "romantic",
            "nice ambiance",
            "welcoming",
            "bad atmosphere",
            "noisy",
            "crowded",
            "dull",
            "uncomfortable",
            "dirty",
        ],
        "value": [
            "worth it",
            "great value",
            "affordable",
            "good price",
            "excellent value for money",
            "overpriced",
            "expensive",
            "not worth it",
            "too pricey",
            "poor value",
        ],
        "cleanliness": [
            "clean",
            "tidy",
            "spotless",
            "neat",
            "dirty",
            "filthy",
            "dusty",
            "unclean",
            "messy",
            "smelly",
        ],
        "location": [
            "great location",
            "easy to find",
            "good parking",
            "central",
            "convenient",
            "bad location",
            "hard to find",
            "no parking",
            "far",
            "difficult to access",
        ],
    },
}

ML_CLASSIFICATION_TYPES = {"hotel", "restaurant"}


def get_classification_approach(business_type_name: str) -> str:
    return "ml" if business_type_name.lower() in ML_CLASSIFICATION_TYPES else "keyword"


_ALL_KEYWORDS = []
for categories in KEYWORD_CATEGORIES.values():
    for keywords in categories.values():
        _ALL_KEYWORDS.extend(keywords)

_PATTERN = re.compile("|".join(re.escape(kw) for kw in _ALL_KEYWORDS), re.I)


def classify_with_keywords(text: str, business_type_uuid: str) -> dict:
    text_lower = text.lower()
    matches = set(_PATTERN.findall(text_lower))

    categories = KEYWORD_CATEGORIES.get(business_type_uuid, {})
    category_scores = {}
    for category, keywords in categories.items():
        score = sum(1 for kw in keywords if kw.lower() in matches)
        if score > 0:
            category_scores[category] = score

    sorted_categories = sorted(
        category_scores.items(), key=lambda x: x[1], reverse=True
    )
    top_3 = sorted_categories[:3] if len(sorted_categories) >= 3 else sorted_categories

    labels = [cat[0] for cat in top_3]
    while len(labels) < 3:
        labels.append("(none)")

    type_names = {
        BUSINESS_TYPE_UUIDS["hotel"]: "Hotel",
        BUSINESS_TYPE_UUIDS["restaurant"]: "Restaurant",
        BUSINESS_TYPE_UUIDS["tour_operator"]: "Tour Operator",
        BUSINESS_TYPE_UUIDS["activity_provider"]: "Activity Provider",
    }
    business_type_name = type_names.get(business_type_uuid, "Unknown")

    return {
        "business_type_id": business_type_uuid,
        "business_type": business_type_name,
        "main_label": labels[0] if len(labels) > 0 else "(none)",
        "second_label": labels[1] if len(labels) > 1 else "(none)",
        "third_label": labels[2] if len(labels) > 2 else "(none)",
    }
