# app/core/playwright_fallback.py

PLAYWRIGHT_ENABLED = False  # keep OFF for FastAPI on Windows


def crawl_with_playwright(domain: str) -> dict:
    """
    Safe Playwright fallback (disabled by default).

    NOTE:
    Playwright should only be enabled in:
    - Docker
    - Linux
    - Separate worker (Celery / RQ)
    """
    if not PLAYWRIGHT_ENABLED:
        return {
            "status": "failed",
            "reason": "playwright_disabled"
        }
