def detect_spam(html: str) -> str:
    text = html.lower()

    spam_keywords = [
        "casino", "bet", "gambling",
        "porn", "xxx", "viagra",
        "loan", "fast cash"
    ]

    hit = any(word in text for word in spam_keywords)

    if hit:
        return "High"

    if text.count("href=") > 200:   # too many outbound links
        return "Medium"

    return "Low"
