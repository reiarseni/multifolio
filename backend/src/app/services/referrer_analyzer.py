from __future__ import annotations

import json
import re
from pathlib import Path

_CORPORATE_DOMAINS: set[str] | None = None
_KNOWN_SOCIAL_PATTERNS = [
    re.compile(r"^linkedin\.com$", re.IGNORECASE),
    re.compile(r"^github\.com$", re.IGNORECASE),
    re.compile(r"^gitlab\.com$", re.IGNORECASE),
    re.compile(r"^bitbucket\.org$", re.IGNORECASE),
    re.compile(r"^twitter\.com$", re.IGNORECASE),
    re.compile(r"^x\.com$", re.IGNORECASE),
]


def _load_corporate_domains() -> set[str]:
    global _CORPORATE_DOMAINS
    if _CORPORATE_DOMAINS is not None:
        return _CORPORATE_DOMAINS

    path = Path(__file__).resolve().parent.parent / "data" / "corporate_domains.json"
    if not path.exists():
        _CORPORATE_DOMAINS = set()
        return _CORPORATE_DOMAINS

    with open(path) as f:
        domains = json.load(f)

    _CORPORATE_DOMAINS = set(domains)
    return _CORPORATE_DOMAINS


def extract_domain(referrer_url: str | None) -> str | None:
    if not referrer_url:
        return None
    match = re.search(r"https?://([^/]+)", referrer_url)
    if match:
        return match.group(1).lower()
    return None


def is_notable_referrer(referrer_url: str | None) -> bool:
    domain = extract_domain(referrer_url)
    if not domain:
        return False

    domain = domain.lower()

    corporate_domains = _load_corporate_domains()
    if domain in corporate_domains:
        return True

    for pattern in _KNOWN_SOCIAL_PATTERNS:
        if pattern.match(domain):
            return True

    if any(domain.endswith("." + cd) for cd in corporate_domains if "." in cd):
        return True

    return False


def get_domain_info(domain: str | None) -> dict:
    if not domain:
        return {"domain": None, "is_corporate": False, "category": "unknown"}

    domain = domain.lower()
    corporate_domains = _load_corporate_domains()
    is_corporate = domain in corporate_domains or any(
        domain.endswith("." + cd) for cd in corporate_domains if "." in cd
    )

    if is_corporate:
        return {"domain": domain, "is_corporate": True, "category": "corporate"}
    if domain in ("linkedin.com", "github.com", "gitlab.com", "bitbucket.org"):
        return {"domain": domain, "is_corporate": False, "category": "professional_network"}
    if domain in ("twitter.com", "x.com"):
        return {"domain": domain, "is_corporate": False, "category": "social_media"}

    return {"domain": domain, "is_corporate": False, "category": "unknown"}
