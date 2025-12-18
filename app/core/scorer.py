from typing import Dict, Any, List

from app.core.spam_detector import detect_spam
from app.core.index_check import is_indexed



# -----------------------------
# CONFIG
# -----------------------------
TITLE_IDEAL_MIN = 20
TITLE_IDEAL_MAX = 70

CONTENT_STRONG = 1500
CONTENT_MEDIUM = 600

TIER_1_SCORE = 80
TIER_2_SCORE = 55


# -----------------------------
# MAIN SCORER
# -----------------------------
def calculate_seo_score(crawl_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Expects crawl_data from crawler.py:

    {
        "url": str,
        "status": "success" | "failed",
        "title": str | None,
        "h1": str | None,
        "content_length": int,
        "html": str | None
    }
    """

    url = crawl_data.get("url")

    # ---------- HARD FAIL ----------
    if crawl_data.get("status") != "success":
        return _blocked_result(url, "Crawl failed or blocked")

    html = crawl_data.get("html")
    if not html:
        return _blocked_result(url, "Empty HTML response")

    # ---------- CHECKS ----------
    title = crawl_data.get("title")
    h1 = crawl_data.get("h1")
    content_len = crawl_data.get("content_length", 0)

    spam_hits = detect_spam(html)
    indexed = is_indexed(url)


    # ---------- SCORING ----------
    score = 0
    breakdown = {}
    reasons = []

    # ---- Title ----
    if title and TITLE_IDEAL_MIN <= len(title) <= TITLE_IDEAL_MAX:
        score += 20
        breakdown["title"] = {"score": 20, "status": "Good"}
    elif title:
        score += 10
        breakdown["title"] = {"score": 10, "status": "Weak length"}
        reasons.append("Title length not optimal")
    else:
        breakdown["title"] = {"score": 0, "status": "Missing"}
        reasons.append("Missing title tag")

    # ---- H1 ----
    if h1:
        score += 15
        breakdown["h1"] = {"score": 15, "status": "Present"}
    else:
        breakdown["h1"] = {"score": 0, "status": "Missing"}
        reasons.append("Missing H1 heading")

    # ---- Content ----
    if content_len >= CONTENT_STRONG:
        score += 25
        breakdown["content"] = {
            "score": 25,
            "status": f"Strong ({content_len} chars)"
        }
    elif content_len >= CONTENT_MEDIUM:
        score += 15
        breakdown["content"] = {
            "score": 15,
            "status": f"Medium ({content_len} chars)"
        }
        reasons.append("Content could be longer")
    else:
        breakdown["content"] = {
            "score": 0,
            "status": f"Weak ({content_len} chars)"
        }
        reasons.append("Thin content")

    # ---- Spam ----
    if spam_hits:
        breakdown["spam"] = {
            "score": 0,
            "status": f"Detected ({', '.join(spam_hits)})"
        }
        reasons.append("Spam keywords detected")
    else:
        score += 20
        breakdown["spam"] = {"score": 20, "status": "Clean"}

    # ---- Google Index ----
    if indexed:
        score += 20
        breakdown["index"] = {"score": 20, "status": "Indexed"}
    else:
        breakdown["index"] = {"score": 0, "status": "Not indexed"}
        reasons.append("Not indexed on Google")

    # ---------- TIER ----------
    if score >= TIER_1_SCORE:
        tier = "Tier 1"
    elif score >= TIER_2_SCORE:
        tier = "Tier 2"
    else:
        tier = "Tier 3"

    return {
        "url": url,
        "score": score,
        "tier": tier,
        "breakdown": breakdown,
        "reasons": reasons
    }


# -----------------------------
# HELPERS
# -----------------------------
def _blocked_result(url: str, reason: str) -> Dict[str, Any]:
    return {
        "url": url,
        "score": 0,
        "tier": "Blocked",
        "breakdown": {},
        "reasons": [reason]
    }
