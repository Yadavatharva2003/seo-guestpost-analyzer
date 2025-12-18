import re

NOFOLLOW_KEYWORDS = [
    "nofollow",
    "ugc",
    "sponsored",
    "advertorial",
    "paid post",
    "partner content"
]

GOOD_CONTEXT_KEYWORDS = [
    "editorial",
    "author",
    "opinion",
    "news",
    "blog"
]

def detect_dofollow_probability(html: str, url: str) -> dict:
    """
    Returns dofollow probability + SEO value verdict
    """

    if not html:
        return {
            "link_type": "Unknown",
            "seo_value": "Low",
            "reason": "no_html_content"
        }

    text = html.lower()

    # 🔴 Strong NoFollow signals
    for k in NOFOLLOW_KEYWORDS:
        if k in text:
            return {
                "link_type": "Likely NoFollow",
                "seo_value": "Low",
                "reason": f"nofollow_signal:{k}"
            }

    # 🟢 Strong DoFollow signals
    for k in GOOD_CONTEXT_KEYWORDS:
        if k in text:
            return {
                "link_type": "Likely DoFollow",
                "seo_value": "High",
                "reason": f"editorial_signal:{k}"
            }

    # 🟡 Neutral / Mixed
    return {
        "link_type": "Mixed / Unknown",
        "seo_value": "Medium",
        "reason": "no_clear_signal"
    }
