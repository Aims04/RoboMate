def select_mode(text):
    text = text.lower()

    if "one" in text or "1" in text:
        return "COLLEGE"
    if "two" in text or "2" in text:
        return "GENERAL"

    return None
