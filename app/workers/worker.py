import time
import traceback
import json
import redis
import sqlite3
from playwright.sync_api import sync_playwright, TimeoutError

from app.storage.sqlite import save_result, init_db
from app.core.niche_detector import detect_niche
from app.core.cms_detector import detect_cms
from app.core.spam_detector import detect_spam
from app.core.structure_detector import detect_structure_group
from app.core.submission_detector import detect_submission_type
from app.core.authority import compute_authority_score
from app.core.tier import map_tier
from app.core.progress import increment_progress

QUEUE_NAME = "seo_queue"
redis_client = redis.Redis(host="localhost", port=6379, db=0)


# --------------------------
# Submission normalization
# --------------------------
def normalize_submission(sub):
    if not sub:
        return "unknown"

    sub = sub.lower()

    mappings = {
        "direct": "direct",
        "email": "email",
        "register": "registration",
        "register_to_post": "registration",
        "contact": "contact",
        "contact_form": "contact",
        "wordpress_dashboard": "registration",
        "blogger_dashboard": "registration",
        "paid": "blocked",
        "sponsored": "blocked",
    }

    return mappings.get(sub, "unknown")


# --------------------------
# Spam → numeric value
# --------------------------
def spam_to_numeric(level):
    if not level:
        return 0.2

    level = level.lower()
    return {"high": 1.0, "medium": 0.6, "low": 0.2}.get(level, 0.2)


# --------------------------
# Page fetch with Playwright
# --------------------------
def fetch_page(page, url: str):

    try:
        start = time.time()
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        html = page.content()
        load_time = round(time.time() - start, 2)

        return html, load_time

    except TimeoutError:
        return None, 15  # timed out ~ 15 sec
    except Exception:
        return None, 0.0


# --------------------------
# Domain processing
# --------------------------
def process_domain(page, url: str, run_id: str):

    html, load_time = fetch_page(page, url)

    if html is None:
        result = {
            "url": url,
            "niche": "unknown",
            "cms": "unknown",
            "submission": "unknown",
            "authority": 0,
            "spam": 1.0,
            "category": "unknown",
            "structure": "unknown",
            "tier": "Blocked",
            "load_time": load_time,
        }

        save_result(run_id, result)
        increment_progress(run_id)
        return

    # detectors
    niche = detect_niche(html)
    cms = detect_cms(html)
    spam = detect_spam(html)
    spam_score = spam_to_numeric(spam)

    submission = normalize_submission(detect_submission_type(html))
    structure = detect_structure_group(html)

    authority = compute_authority_score(url, html)

    indexed = True  # future enhancement

    niche_match = 1.0 if niche != "general" else 0.4

    tier = map_tier(
        authority=authority,
        spam_score=spam_score,
        submission=submission,
        cms=cms,
        indexed=indexed,
        niche_match=niche_match,
    )

    result = {
        "url": url,
        "niche": niche,
        "cms": cms,
        "submission": submission,
        "authority": authority,
        "spam": spam_score,
        "category": niche,
        "structure": structure,
        "tier": tier,
        "load_time": load_time,
    }

    save_result(run_id, result)
    increment_progress(run_id)


# --------------------------
# Worker Loop
# --------------------------
def worker_loop():
    print("Worker started & listening...")

    # ensure DB exists
    init_db()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(10000)

        while True:
            job = redis_client.brpop(QUEUE_NAME, timeout=3)

            if not job:
                time.sleep(0.5)
                continue

            _, payload = job
            try:
                data = json.loads(payload)
                url = data["url"]
                run_id = data["run_id"]

                print(f"[PROCESSING] {url}")

                process_domain(page, url, run_id)

            except Exception:
                traceback.print_exc()
                continue


if __name__ == "__main__":
    worker_loop()
