import ssl
import socket
import whois
from datetime import datetime

TOP_AUTHORITY_DOMAINS = [
    "bbc.com", "forbes.com", "techcrunch.com", "microsoft.com",
    "linkedin.com", "github.com", "stackoverflow.com",
    "medium.com", "theverge.com"
]

def check_domain_age(domain):
    try:
        w = whois.whois(domain)
        created = w.creation_date

        if isinstance(created, list):
            created = created[0]

        if not created:
            return 0

        years = (datetime.utcnow() - created).days / 365
        return years
    except:
        return 0


def ssl_valid(domain):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=3) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain):
                return True
    except:
        return False


def authority_score(domain):
    score = 0

    if domain in TOP_AUTHORITY_DOMAINS:
        score += 3

    age = check_domain_age(domain)
    if age > 5:
        score += 2
    elif age > 2:
        score += 1

    if ssl_valid(domain):
        score += 1

    if score >= 4:
        return "High"
    elif score >= 2:
        return "Medium"
    return "Low"
