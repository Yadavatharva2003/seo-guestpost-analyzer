def detect_niche(html: str) -> str:
    text = html.lower()

    niches = {
        "tech": ["software", "ai", "gadgets", "hosting", "code", "developer"],
        "finance": ["loan", "credit", "stock", "bank", "roi", "crypto"],
        "health": ["fitness", "supplement", "doctor", "weight loss", "diet"],
        "education": ["university", "college", "student", "courses", "exam"],
        "marketing": ["seo", "content", "digital marketing", "affiliate"],
        "legal": ["lawyer", "attorney", "legal", "notary"],
        "casino": ["casino", "bet", "slot", "bonus", "gambling"],
        "adult": ["xxx", "porn", "sex", "escort"],
        "real estate": ["property", "housing", "rent", "investor"],
    }

    for niche, keywords in niches.items():
        for word in keywords:
            if word in text:
                return niche

    return "general"
