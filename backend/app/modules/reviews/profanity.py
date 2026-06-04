from better_profanity import profanity

profanity.load_censor_words()


def censor_text(text: str) -> str:
    if not text:
        return text
    return profanity.censor(text)
