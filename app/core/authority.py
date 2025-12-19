import re
from bs4 import BeautifulSoup

TRUSTED_TLDS = [
    ".gov", ".edu", ".org", ".ac", ".mil"
]

SPAM_TLDS = [
    ".xyz", ".click", ".loan", ".buzz", ".work", ".top"
]

KNOWN_AUTH_DOMAINS = [
    "bbc.com", "forbes.com", "microsoft.com", "github.com",
    "yahoo", "nytimes", "wikipedia", "medium.com"
]


def compute_authority_score(url: str, html: str) -> int:
    """
    Very lightweight authority estimation.
    Score range = 0–100.
    """

    if not url:
        return 0

    score = 20  # baseline

    url = url.lower()

    # TLD influence
    for tld in TRUSTED_TLDS:
        if url.endswith(tld):
            score += 25

    for tld in SPAM_TLDS:
        if url.endswith(tld):
            score -= 20

    # Known authority domain boost
    if any(domain in url for domain in KNOWN_AUTH_DOMAINS):
        score += 30

    # Domain age heuristic via TLD + known patterns
    if ".com" in url and len(url) > 15:
        score += 5

    # Content based authority signals
    if html:
        soup = BeautifulSoup(html, "html.parser")

        word_count = len(soup.get_text(" ", strip=True).split())
        
        if word_count > 2000:
            score += 15
        elif word_count > 800:
            score += 8
        elif word_count < 200:
            score -= 10

        # backlink heuristic (anchor count)
        anchors = soup.find_all("a")
        if len(anchors) > 200:
            score -= 5
        elif len(anchors) > 50:
            score += 5

        # presence of structured data
        if soup.find("script", {"type": "application/ld+json"}):
            score += 5

    # clamp score
    if score < 0: 
        score = 0
    if score > 100:
        score = 100

    return score
