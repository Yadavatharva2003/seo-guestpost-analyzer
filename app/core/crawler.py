import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = 15


def crawl_homepage(url: str) -> dict:
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True
        )

        code = r.status_code

        # ---------- DEAD ----------
        if code in (404, 410, 500):
            return {"status": "dead", "http": code, "url": url}

        # ---------- PROTECTED ----------
        if code in (401, 403):
            return {"status": "protected", "http": code, "url": url}

        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        h1 = soup.find("h1")
        h1 = h1.get_text(strip=True) if h1 else ""

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(" ", strip=True)
        words = len([w for w in text.split() if len(w) > 2])

        # ---------- JS RENDERED ----------
        if words < 80:
            return {
                "status": "js_required",
                "url": url,
                "title": title,
                "h1": h1,
                "content_words": words
            }

        return {
            "status": "success",
            "url": url,
            "title": title,
            "h1": h1,
            "content_words": words,
            "raw_text": text
        }

    except requests.exceptions.Timeout:
        return {"status": "timeout", "url": url}

    except Exception as e:
        return {"status": "error", "error": str(e), "url": url}
