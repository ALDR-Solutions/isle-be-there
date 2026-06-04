from bleach import clean


def sanitize_html(text: str | None) -> str | None:
    if not text:
        return text
    return clean(text, tags=[], strip=True)
