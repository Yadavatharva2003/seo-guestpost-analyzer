import requests
from urllib.parse import urlparse

# -----------------------------
# In-memory cache (per run)
# -----------------------------
_INDEX_CACHE: dict[str, bool] = {}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 8  # seconds


def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "").strip()


def is_indexed(url: str) -> bool:
    """
    Checks if a domain appears indexed in Google using `site:` query.
    Cached per domain for performance.
    """

    domain = extract_domain(url)

    # ---------- CACHE HIT ----------
    if domain in _INDEX_CACHE:
        return _INDEX_CACHE[domain]

    search_url = f"https://www.google.com/search?q=site:{domain}"

    try:
        response = requests.get(
            search_url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        html = response.text.lower()

        # Google "no results" signals
        not_indexed_markers = [
            "did not match any documents",
            "no results found",
            "your search did not match"
        ]

        indexed = not any(marker in html for marker in not_indexed_markers)

    except Exception:
        # Fail SAFE — do NOT block pipeline
        indexed = False

    # ---------- CACHE STORE ----------
    _INDEX_CACHE[domain] = indexed
    return indexed
