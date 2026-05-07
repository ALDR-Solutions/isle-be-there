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