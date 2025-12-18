OUTREACH_KEYWORDS = {
    "Form": ["write for us", "contribute", "submit", "contact"],
    "Email": ["mailto:", "editor@", "contact@"]
}

def detect_outreach_method(text: str) -> str:
    if not text:
        return "Manual"

    text = text.lower()
    for method, keywords in OUTREACH_KEYWORDS.items():
        for k in keywords:
            if k in text:
                return method

    return "Manual"
