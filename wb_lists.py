import requests
import time
from urllib.parse import urlparse
from datetime import datetime
import whois

CACHE_TTL = 3600

OPENPHISH_URL = "https://openphish.com/feed.txt"
PHISHTANK_URL = "https://data.phishtank.com/data/online-valid.csv" #PhishTank может давать false positive
URLHAUS_URL = "https://urlhaus.abuse.ch/downloads/text_online/"
PHISHSTATS_URL = "https://phishstats.info:2096/api/phishing?_format=json"

SHORTENERS = ["bit.ly", "tinyurl.com", "goo.gl", "t.co", "rb.gy"]

_cache = {
    "domains": set(),
    "urls": set()
}


def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except:
        return ""


def load_openphish():
    urls = set()
    try:
        r = requests.get(OPENPHISH_URL, timeout=10)
        for line in r.text.splitlines():
            if line.startswith("http"):
                urls.add(line.strip())
    except:
        pass
    return urls


def load_urlhaus():
    urls = set()
    try:
        r = requests.get(URLHAUS_URL, timeout=10)
        for line in r.text.splitlines():
            if line.startswith("http"):
                urls.add(line.strip())
    except:
        pass
    return urls


def load_phishstats():
    urls = set()
    try:
        r = requests.get(PHISHSTATS_URL, timeout=10)
        data = r.json()
        for entry in data:
            u = entry.get("url")
            if u:
                urls.add(u)
    except:
        pass
    return urls


def load_phishtank():
    urls = set()
    try:
        r = requests.get(PHISHTANK_URL, timeout=10)
        for line in r.text.splitlines()[1:]:
            parts = line.split(",")
            if len(parts) > 1:
                url = parts[1]
                if url.startswith("http"):
                    urls.add(url)
    except:
        pass
    return urls


def refresh_cache():
    global _cache

    all_urls = set()

    # all_urls |= load_openphish()
    all_urls |= load_urlhaus()
    # all_urls |= load_phishstats()
    # all_urls |= load_phishtank()

    domains = set()
    for u in all_urls:
        d = extract_domain(u)
        if d:
            domains.add(d)

    _cache["urls"] = all_urls
    _cache["domains"] = domains


def is_in_blacklist(url: str) -> bool:
    refresh_cache()

    domain = extract_domain(url)

    if url in _cache["urls"]:
        return True

    return False


def has_https(url: str) -> bool:
    return url.startswith("https://")


def is_shortener(domain: str) -> bool:
    return any(s in domain for s in SHORTENERS)


def domain_age_days(domain: str) -> int:
    try:
        w = whois.whois(domain)
        creation = w.creation_date

        if isinstance(creation, list):
            creation = creation[0]

        if not creation:
            return 9999

        return (datetime.now() - creation).days
    except:
        return 9999


def analyze_url(url: str) -> dict:
    domain = extract_domain(url)

    reasons = []
    phishing = False

    if is_in_blacklist(url):
        phishing = True
        reasons.append("blacklist")

    # if not has_https(url):
    #     phishing = True
    #     reasons.append("no_https")

    if is_shortener(domain):
        phishing = True
        reasons.append("shortener")

    age = domain_age_days(domain)
    if age < 30:
        phishing = True
        reasons.append("young_domain")

    return {
        "url": url,
        "domain": domain,
        "phishing": phishing,
        "reasons": list(set(reasons))
    }


def analyze_urls(urls: list[str]) -> dict:
    results = []
    phishing = False

    for url in urls:
        res = analyze_url(url)
        results.append(res)
        if res["phishing"]:
            phishing = True

    return {
        "phishing": phishing,
        "details": results
    }