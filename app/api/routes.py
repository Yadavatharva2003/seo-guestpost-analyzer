from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import csv, io, threading, time
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from openpyxl import load_workbook

from app.core.crawler import crawl_homepage
from app.core.spam_detector import detect_spam
from app.core.index_check import is_indexed
from app.core.progress import reset_progress, increment_progress, finish_progress, progress_state
from app.core.decision import good, okay, reject
from app.core.outreach import detect_outreach_method
from app.core.dofollow import detect_dofollow_probability
from app.core.normalizer import normalize_url

router = APIRouter()

analysis_results: List[dict] = []
results_lock = Lock()


# ---------- FILE PARSERS ----------
def extract_urls_from_csv(raw: bytes) -> List[str]:
    for enc in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    reader = csv.reader(io.StringIO(text))
    urls = []

    for row in reader:
        for cell in row:
            if isinstance(cell, str) and cell.strip():
                urls.append(cell.strip())
                break

    return urls


def extract_urls_from_excel(raw: bytes) -> List[str]:
    wb = load_workbook(io.BytesIO(raw), read_only=True)
    sheet = wb.active
    urls = []

    for row in sheet.iter_rows(values_only=True):
        for cell in row:
            if isinstance(cell, str) and cell.strip():
                urls.append(cell.strip())
                break

    return urls


# ---------- CORE LOGIC ----------
def process_url(url: str):
    data = crawl_homepage(url)
    status = data.get("status")

    domain = normalize_url(url)
    raw_text = data.get("raw_text", "")

    outreach = detect_outreach_method(raw_text)

    # ✅ DEFAULTS (NO UNDEFINED EVER)
    link_type = "Unknown"
    seo_value = "Low"
    link_reason = "not_analyzed"

    if raw_text:
        df = detect_dofollow_probability(raw_text, url)
        link_type = df.get("link_type", link_type)
        seo_value = df.get("seo_value", seo_value)
        link_reason = df.get("reason", link_reason)

    # ---------- VERDICT ----------
    if status in ("dead", "timeout", "error"):
        r = reject(url, status)

    elif status == "protected":
        r = good(url, "protected_authority_site", "High")
        link_type = "Likely NoFollow"
        seo_value = "Medium"
        link_reason = "authority_site_protected"

    elif status == "js_required":
        if is_indexed(url):
            r = good(url, "js_rendered_editorial_site", "Medium")
        else:
            r = reject(url, "not_indexed")

    else:
        indexed = is_indexed(url)
        spam = detect_spam(raw_text)
        words = data.get("content_words", 0)

        if not indexed or spam:
            r = reject(url, "spam_or_not_indexed")
        elif words >= 800:
            r = good(url, "strong_editorial_content", "High")
        elif 300 <= words < 800:
            r = okay(url, "moderate_content", "Medium")
        else:
            r = reject(url, "thin_content")

    # ---------- ATTACH META ----------
    r["domain"] = domain
    r["outreach"] = outreach
    r["link_type"] = link_type
    r["seo_value"] = seo_value
    r["link_reason"] = link_reason

    return r


# ---------- ANALYSIS ----------
def run_analysis(urls: List[str]):
    domain_best = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_url, u) for u in urls]

        for future in as_completed(futures):
            result = future.result()
            increment_progress()

            domain = result.get("domain")
            if not domain:
                continue

            if domain not in domain_best or result["confidence_score"] > domain_best[domain]["confidence_score"]:
                domain_best[domain] = result

    with results_lock:
        analysis_results.clear()
        analysis_results.extend(domain_best.values())

    finish_progress()


# ---------- API ----------
@router.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    raw = await file.read()
    name = file.filename.lower()

    urls = extract_urls_from_csv(raw) if name.endswith(".csv") else extract_urls_from_excel(raw)

    if not urls:
        raise HTTPException(400, "No valid URLs found")

    reset_progress(len(urls))
    analysis_results.clear()

    threading.Thread(target=run_analysis, args=(urls,), daemon=True).start()
    return {"message": "Analysis started", "total_urls": len(urls)}


@router.get("/api/results")
def results():
    return analysis_results


@router.get("/api/progress")
def progress():
    t, d = progress_state["total"], progress_state["completed"]
    return {"percent": int(d / t * 100) if t else 0, "running": progress_state["running"]}


@router.get("/api/export")
def export_csv():
    def gen():
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow([
            "Domain", "URL", "Verdict", "Confidence Score",
            "Link Type", "SEO Value", "Outreach", "Reason"
        ])

        for r in analysis_results:
            if r["final_verdict"] in ("GOOD", "OKAY"):
                w.writerow([
                    r["domain"], r["url"], r["final_verdict"],
                    r["confidence_score"], r["link_type"],
                    r["seo_value"], r["outreach"], r["reason"]
                ])

        buf.seek(0)
        yield buf.read()

    return StreamingResponse(
        gen(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=seo_offpage.csv"}
    )
