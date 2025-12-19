def detect_cms(html: str) -> str:
    text = html.lower()

    if "wp-content" in text or "wp-json" in text:
        return "WordPress"

    if "blogger" in text or "blogspot" in text:
        return "Blogger"

    if "medium.com" in text or "data-ghost" in text:
        return "Medium"

    if "shopify" in text:
        return "Shopify"

    if "drupal" in text or "drupal-settings" in text:
        return "Drupal"

    if "ghost" in text:
        return "Ghost"

    return "Unknown"
