import time
import traceback
from playwright.sync_api import sync_playwright

from app.storage.sqlite import save_result
from app.core.niche_detector import detect_niche
from app.core.cms_detector import detect_cms
from app.core.spam_detector import detect_spam
from app.core.structure_detector import detect_structure_group
from app.core.submission_detector import detect_submission_type
from app.core.authority import compute_authority_score
from app.core.tier import map_tier

def fetch_page(url: str):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            start = time.time()
            response = page.goto(url, wait_until="domcontentloaded", timeout=25000)
            load_time = time.time() - start

            html = page.content()
            title = page.title()

            browser.close()

            return html, title, load_time

    except Exception:
        traceback.print_exc()
        return None, None, None


def process_domain(url: str, run_id: str):
    html, title, load_time = fetch_page(url)

    # if crawl fails → mark blocked
    if html is None:
        result = {
            "url": url,
            "niche": "unknown",
            "cms": "unknown",
            "submission_type": "unknown",
            "guest_post": False,
            "spam_risk": "High",
            "authority_score": 0,
            "quality_tier": "Blocked",
            "structure_group": "unknown",
            "index_status": False,
            "content_length": 0,
            "load_time": 0,
            "run_id": run_id
        }
        save_result(result)
        return result

    # deep metrics
    niche = detect_niche(html)
    cms = detect_cms(html)
    spam_risk = detect_spam(html)
    structure = detect_structure_group(html, cms)
    submission = detect_submission_type(html)
    authority = compute_authority_score(html, title)
    tier = map_tier(authority)

    guest_possible = submission in ("Direct", "Email", "Account")

    result = {
        "url": url,
        "niche": niche,
        "cms": cms,
        "submission_type": submission,
        "guest_post": guest_possible,
        "spam_risk": spam_risk,
        "authority_score": authority,
        "quality_tier": tier,
        "structure_group": structure,
        "index_status": True,  # improved later via index API fallback
        "content_length": len(html),
        "load_time": load_time,
        "run_id": run_id
    }

    save_result(result)
    return result
