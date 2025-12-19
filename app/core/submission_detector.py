import re
from bs4 import BeautifulSoup

def detect_submission_type(html: str) -> str:
    """
    Detect how guest posting can be submitted on the website.
    """

    if not html or len(html) < 100:
        return "unknown"

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True).lower()

    # Common publish/signup URLs
    submit_keywords = [
        "write for us",
        "submit guest post",
        "contribute",
        "become a writer",
        "submit article",
        "guest post guidelines",
        "submit content",
        "partner with us"
    ]

    for kw in submit_keywords:
        if kw in text:
            return "direct"

    # Email submission patterns
    email_match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
    if email_match and any("editor" in e or "submit" in e or "contact" in e for e in email_match):
        return "email"

    # Registration required
    if soup.find("form") and ("register" in text or "signup" in text):
        return "register_to_post"

    # Paid contributor portals
    if "sponsored post" in text or "paid post" in text or "pricing" in text:
        return "paid"

    # Contact form
    if soup.find("form") and ("contact" in text):
        return "contact_form"

    # CMS automated submission (WordPress / Blogger etc.)
    if "wp-admin" in html or "xmlrpc.php" in html:
        return "wordpress_dashboard"

    if "blogger.com" in html:
        return "blogger_dashboard"

    # Submission SaaS portals
    if "submittable" in html or "airtable" in html or "hubspot" in html:
        return "external_portal"

    # Forums / UGC
    if "thread" in text or "forum" in text:
        return "ugc_forum"

    return "unknown"
