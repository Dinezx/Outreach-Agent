from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


BLOCKED_DOMAINS = {
    "facebook.com",
    "github.com",
    "glassdoor.com",
    "instagram.com",
    "linkedin.com",
    "x.com",
    "twitter.com",
    "wikipedia.org",
    "youtube.com",
    "crunchbase.com",
    "zoominfo.com",
    "leadnear.com",
    "yellowpagesinfo.in",
    "indiamart.com",
    "justdial.com",
    "apollo.io",
    "zaubacorp.com",
    "tofler.in",
    "business-standard.com",
    "moneycontrol.com",
    "economictimes.indiatimes.com",
    "indiatimes.com",
    "bloomberg.com",
    "yahoo.com",
    "google.com",
    "bing.com",
    "yelp.com",
    "yellowpages.com",
    "tripadvisor.com",
    "mapquest.com",
    "waze.com",
    "slideshare.net",
    "pinterest.com",
    "tumblr.com",
    "reddit.com",
    "quora.com",
    "medium.com",
    "blogspot.com",
    "wordpress.com",
}


@dataclass(slots=True)
class SearchResult:
    title: str
    url: str
    content: str | None = None


def _root_domain(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    parts = hostname.lower().split(".")
    if len(parts) <= 2:
        return hostname.lower()
    return ".".join(parts[-2:])


def select_official_website(company_name: str, results: list[SearchResult]) -> str | None:
    normalized_company = company_name.lower().strip()
    candidates: list[tuple[int, SearchResult]] = []

    for result in results:
        domain = _root_domain(result.url)
        if not domain or domain in BLOCKED_DOMAINS:
            continue

        score = 0
        title = result.title.lower()
        url = result.url.lower()
        content = (result.content or "").lower()

        if normalized_company in title:
            score += 4
        if normalized_company in content:
            score += 3
        if normalized_company in url:
            score += 2
        score += 1

        candidates.append((score, result))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    best_score, best_result = candidates[0]
    return best_result.url if best_score > 0 else None
