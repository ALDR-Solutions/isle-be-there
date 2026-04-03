"""Keyword-based classifier for Events, Tours, and Services reviews."""

# Placeholder UUIDs - replace with actual later
BUSINESS_TYPE_UUIDS = {
    "hotel": "390a6943-b75a-465b-a09b-560e7522682c",
    "restaurant": "b155ad8f-91e8-4cee-9384-de3eb498bec5",
    "events": "11111111-1111-1111-1111-111111111111",
    "tours": "22222222-2222-2222-2222-222222222222",
    "services": "33333333-3333-3333-3333-333333333333",
}

KEYWORD_CATEGORIES = {
    BUSINESS_TYPE_UUIDS["events"]: {
        "atmosphere": [
            "amazing vibes", "electric atmosphere", "good vibes", "fun energy", "crowd was great",
            "lively", "exciting", "unforgettable experience", "incredible atmosphere", "party vibe",
            "boring", "dull atmosphere", "dead crowd", "no energy", "disappointing", "flat", "lackluster"
        ],
        "entertainment": [
            "great music", "awesome DJ", "live band", "amazing performances", "good entertainment",
            "excellent show", "talented performers", "exciting acts",
            "bad music", "terrible DJ", "boring show", "no entertainment", "disappointing performance", "repetitive music"
        ],
        "organisation": [
            "well organized", "smooth entry", "great organization", "easy entry", "well planned",
            "efficient", "seamless",
            "disorganized", "chaos", "long lines", "no organization", "poorly planned", "crowded", "confusing", "hectic"
        ],
        "value": [
            "worth it", "great value", "affordable", "good price", "bang for buck", "excellent value",
            "overpriced", "expensive", "not worth it", "too pricey", "poor value", "highway robbery"
        ],
        "safety": [
            "felt safe", "secure", "safe environment", "good security", "police present",
            "unsafe", "dangerous", "security issues", "felt threatened", "too crowded", "panic", "stampede"
        ],
        "location": [
            "easy to find", "great location", "good parking", "central location", "accessible", "convenient",
            "hard to find", "bad location", "no parking", "far from everything", "difficult to access"
        ],
        "food_drinks": [
            "great drinks", "good bar", "delicious food", "excellent cocktails", "good selection",
            "overpriced drinks", "bad bar", "no drinks", "warm beer", "limited selection", "watered down"
        ],
    },
    BUSINESS_TYPE_UUIDS["tours"]: {
        "guide_quality": [
            "knowledgeable guide", "great tour guide", "informative guide", "expert guide",
            "friendly guide", "excellent guide",
            "bad guide", "uninformed guide", "boring guide", "unprofessional", "rude guide", "missing information"
        ],
        "historical_value": [
            "rich history", "fascinating history", "important heritage", "interesting history",
            "well preserved", "educational",
            "no history", "boring history", "poorly preserved", "disappointing", "lack of information"
        ],
        "facilities": [
            "clean facilities", "good restrooms", "accessible", "well maintained",
            "wheelchair friendly", "clean",
            "dirty restrooms", "poor facilities", "not accessible", "broken", "poorly maintained", "unsanitary"
        ],
        "value": [
            "worth it", "great value", "affordable", "good price", "excellent tour value",
            "overpriced", "expensive", "not worth it", "tour too short", "poor value"
        ],
        "atmosphere": [
            "beautiful scenery", "amazing views", "stunning", "breathtaking", "impressive", "fascinating",
            "boring", "disappointing", "underwhelming", "nothing special", "dull"
        ],
        "information": [
            "great audio guide", "good signage", "informative displays", "excellent explanations",
            "detailed plaques",
            "poor signage", "no information", "missing plaques", "confusing", "audio guide broken", "lack of info"
        ],
    },
    BUSINESS_TYPE_UUIDS["services"]: {
        "service_quality": [
            "friendly staff", "professional", "helpful", "excellent service", "courteous",
            "attentive", "great service",
            "rude staff", "unprofessional", "unhelpful", "terrible service", "slow service", "dismissive", "incompetent"
        ],
        "efficiency": [
            "fast", "quick", "on time", "efficient", "timely", "prompt", "speedy", "no wait",
            "slow", "took forever", "late", "long wait", "inefficient", "delayed", "wasted time"
        ],
        "quality": [
            "great quality", "excellent work", "perfectly done", "immaculate", "top quality", "fresh",
            "poor quality", "damaged", "ruined", "stained", "unsatisfactory", "substandard", "torn"
        ],
        "value": [
            "fair price", "affordable", "great value", "worth it", "good deal", "reasonable",
            "overpriced", "expensive", "not worth it", "poor value", "inflated price"
        ],
        "communication": [
            "easy booking", "responsive", "clear communication", "confirmed booking", "kept updated",
            "difficult booking", "no response", "booking issues", "confused", "no confirmation", "ignored"
        ],
    },
}

PROFANITY_WORDS = [
    "fuck", "fucks", "fucked", "fucking", "shit", "shits", "shitty", "ass", "asses",
    "bitch", "bitches", "damn", "damned", "bullshit", "crap", "crappy"
]

HATE_PATTERNS = [
    "hate them", "kill them", "die", "should die", "rot in hell", "worthless"
]

SPAM_PATTERNS = [
    "click here", "buy now", "free money", "limited offer", "act now", "visit our website",
    "subscribe now", "winner", "congratulations you won"
]

PERSONAL_ATTACK_PATTERNS = [
    "idiot", "idiots", "stupid", "dumb", "moron", "imbecile", "fool", "ignorant"
]


def classify_with_keywords(text: str, business_type_uuid: str) -> dict:
    """Classify review text using keyword matching.

    Args:
        text: Review text to classify
        business_type_uuid: UUID of the business type

    Returns:
        dict with business_type_id, business_type, main_label, second_label, third_label
    """
    text_lower = text.lower()

    # Get categories for this business type
    categories = KEYWORD_CATEGORIES.get(business_type_uuid, {})

    # Score each category
    category_scores = {}
    for category, keywords in categories.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in text_lower:
                score += 1
        if score > 0:
            category_scores[category] = score

    # Sort by score and get top 3
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_categories[:3] if len(sorted_categories) >= 3 else sorted_categories

    # Get labels (use 'other' if less than 3)
    labels = [cat[0] for cat in top_3]
    while len(labels) < 3:
        labels.append("(none)")

    # Get business type name
    type_names = {
        BUSINESS_TYPE_UUIDS["events"]: "Events",
        BUSINESS_TYPE_UUIDS["tours"]: "Tours",
        BUSINESS_TYPE_UUIDS["services"]: "Services",
    }
    business_type_name = type_names.get(business_type_uuid, "Unknown")

    return {
        "business_type_id": business_type_uuid,
        "business_type": business_type_name,
        "main_label": labels[0] if len(labels) > 0 else "(none)",
        "second_label": labels[1] if len(labels) > 1 else "(none)",
        "third_label": labels[2] if len(labels) > 2 else "(none)",
    }


def check_flags(text: str) -> dict:
    """Check review text for inappropriate content.

    Args:
        text: Review text to check

    Returns:
        dict with is_flagged (bool) and reason (str or None)
    """
    text_lower = text.lower()

    # Check profanity
    for word in PROFANITY_WORDS:
        if word in text_lower:
            return {"is_flagged": True, "reason": "profanity"}

    # Check hate speech
    for pattern in HATE_PATTERNS:
        if pattern in text_lower:
            return {"is_flagged": True, "reason": "hate_speech"}

    # Check spam
    for pattern in SPAM_PATTERNS:
        if pattern in text_lower:
            return {"is_flagged": True, "reason": "spam"}

    # Check personal attacks
    for pattern in PERSONAL_ATTACK_PATTERNS:
        if pattern in text_lower:
            return {"is_flagged": True, "reason": "personal_attack"}

    return {"is_flagged": False, "reason": None}
