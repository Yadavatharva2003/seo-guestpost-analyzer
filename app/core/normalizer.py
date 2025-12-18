from urllib.parse import urlparse
import re

DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
)

def normalize_url(raw_url: str) -> str | None:
    """
    Convert any URL-like input into a clean root domain.
    Returns None if invalid.
    """

    if not raw_url:
        return None

    raw_url = raw_url.strip().lower()

    # Add scheme if missing (urlparse fails without it)
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "http://" + raw_url

    try:
        parsed = urlparse(raw_url)
        domain = parsed.netloc
    except Exception:
        return None

    # Remove www.
    if domain.startswith("www."):
        domain = domain[4:]

    # Basic domain validation
    if not DOMAIN_REGEX.match(domain):
        return None

    return domain
