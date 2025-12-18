# app/core/spam_detector.py

SPAM_KEYWORDS = [
    "casino", "betting", "poker",
    "loan", "payday",
    "viagra", "cialis", "pills",
    "adult", "porn", "sex",
    "crypto scam", "binary option"
]


def detect_spam(text: str) -> bool:
    """
    Detect common spam / link-farm keywords
    """
    if not text:
        return False

    text = text.lower()
    return any(keyword in text for keyword in SPAM_KEYWORDS)
