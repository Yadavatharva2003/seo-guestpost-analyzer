def good(url, reason, confidence_level):
    score = 90 if confidence_level == "High" else 75
    return {
        "url": url,
        "final_verdict": "GOOD",
        "tier": "Tier 1",
        "confidence": confidence_level,
        "confidence_score": score,
        "reason": reason
    }

def okay(url, reason, confidence_level):
    return {
        "url": url,
        "final_verdict": "OKAY",
        "tier": "Tier 2",
        "confidence": confidence_level,
        "confidence_score": 65,
        "reason": reason
    }

def reject(url, reason):
    return {
        "url": url,
        "final_verdict": "REJECTED",
        "tier": "Do Not Use",
        "confidence": "Low",
        "confidence_score": 20,
        "reason": reason
    }
