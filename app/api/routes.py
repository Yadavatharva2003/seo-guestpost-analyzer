from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import csv
import io
from openpyxl import load_workbook

from app.queue.enqueue import enqueue_urls
from app.storage.sqlite import fetch_results
from app.queue.progress import *
from app.queue.progress import set_run_progress

router = APIRouter()

# -------------------------------
# Helpers: CSV & Excel parsing
# -------------------------------

def extract_csv(raw: bytes):
    for enc in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except:
            continue

    reader = csv.reader(io.StringIO(text))
    urls = []

    for row in reader:
        for cell in row:
            if cell.strip():
                urls.append(cell.strip())
                break

    return urls


def extract_excel(raw: bytes):
    wb = load_workbook(io.BytesIO(raw), read_only=True)
    sheet = wb.active
    urls = []

    for row in sheet.iter_rows(values_only=True):
        for cell in row:
            if isinstance(cell, str) and cell.strip():
                urls.append(cell.strip())
                break

    return urls


# -------------------------------
# MAIN ENDPOINTS
# -------------------------------

@router.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    raw = await file.read()

    name = file.filename.lower()
    if name.endswith(".csv"):
        urls = extract_csv(raw)
    else:
        urls = extract_excel(raw)

    if not urls:
        raise HTTPException(400, "No URLs found")

    run_id = enqueue_urls(urls)

    total = len(urls)
    set_run_progress(run_id, 0, total)

    return {"message": "Queued", "run_id": run_id, "total": total}


@router.get("/api/progress/{run_id}")
def progress(run_id: str):
    data = get_run_progress(run_id)
    return data


@router.get("/api/results/{run_id}")
def results(run_id: str):
    rows = fetch_results(run_id)

    formatted = []
    for r in rows:
        formatted.append({
            "url": r[1],
            "niche": r[2],
            "cms": r[3],
            "submission_type": r[4],
            "guest_post": bool(r[5]),
            "spam_risk": r[6],
            "authority_score": r[7],
            "quality_tier": r[8],
            "structure_group": r[9],
            "index_status": bool(r[10]),
            "content_length": r[11],
            "load_time": r[12]
        })

    return JSONResponse(content=formatted)
