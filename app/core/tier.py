# app/core/tier.py

def map_tier(
    authority: int,
    spam_score: float,
    submission: str,
    cms: str,
    indexed: bool,
    niche_match: float = 0.0,
):
    """
    Map site into Tier classification for off-page SEO.

    authority: 0–100
    spam_score: 0.0–1.0 (1 is worst)
    submission:
        - 'direct'
        - 'email'
        - 'registration'
        - 'blocked'
        - None
    cms:
        - WordPress
        - Medium
        - Blogger
        - Custom
        - Shopify
        - etc
    indexed:
        bool
    niche_match: 0–1 relevance to user's niche
    """

    # 👉 immediate block reasons
    if not indexed or authority == 0:
        return "Blocked"

    if spam_score >= 0.8:
        return "Blocked"

    # 👉 elite domain
    if authority >= 80:
        if submission in ("direct", "email", "registration"):
            if spam_score < 0.2:
                return "Tier 1"
        return "Tier 2"

    # 👉 strong domain
    if authority >= 60:
        if submission in ("direct", "email"):
            if spam_score < 0.4:
                return "Tier 2"
        return "Tier 3"

    # 👉 niche booster logic
    if niche_match >= 0.7 and authority >= 40:
        return "Tier 2"

    # 👉 mid-tier
    if authority >= 30:
        return "Tier 3"

    # 👉 weak or generic blog
    return "Tier 3"
