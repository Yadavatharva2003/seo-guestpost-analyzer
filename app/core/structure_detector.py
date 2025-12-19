import re
from bs4 import BeautifulSoup

def detect_structure_group(html: str) -> str:
    """
    Detect the structural pattern of a website.
    Used for grouping automation targets with similar DOM layouts.
    """

    if not html or len(html) < 100:
        return "unknown"

    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text(" ", strip=True).lower()

    # WordPress common patterns
    if "wp-content" in html or "wp-includes" in html or "wordpress" in text:
        return "wordpress"

    # Medium style
    if "medium-feed" in html or "medium.com" in html or "meteredContent" in html:
        return "medium"

    # Blogspot / Blogger
    if "blogger.com" in html or "blogspot" in html:
        return "blogger"

    # Wix platform
    if "wixstatic" in html or "wix.com" in html:
        return "wix"

    # Ghost CMS
    if "ghost.min.js" in html or "ghost" in text:
        return "ghost"

    # Drupal
    if "drupal" in text or "sites/default/files" in html:
        return "drupal"

    # Joomla
    if "joomla" in text or "/components/com_" in html:
        return "joomla"

    # Static SPA patterns
    if re.search(r'<div id="root">|<div id="app">', html):
        return "react_vue_spa"

    # E-commerce structures
    if "woocommerce" in html or "shopify" in html:
        return "ecommerce"

    # Developer docs & MD sites
    if soup.find("nav") and soup.find("main") and soup.find("article"):
        return "docs_style"

    # Forums
    if soup.find("ul", {"class": re.compile("thread|forum")}):
        return "forum"

    # News / magazine
    if soup.find("article") and soup.find("header") and soup.find("section"):
        return "magazine"

    # Online directories
    if "directory" in text or "listing" in text:
        return "directory"

    # Link farms / PBN guess
    if len(soup.find_all("a")) > 200:
        return "link_farm"

    return "generic"
