import ipaddress
import re
import socket
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
import validators
from bs4 import BeautifulSoup


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 12

SOCIAL_NETWORKS = {
    "Facebook": "facebook.com",
    "Instagram": "instagram.com",
    "LinkedIn": "linkedin.com",
    "X (Twitter)": "x.com",
    "Twitter": "twitter.com",
    "YouTube": "youtube.com",
    "GitHub": "github.com",
}

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy",
]

CATEGORY_MAX_SCORES = {
    "SEO": 30,
    "Technical Basics": 25,
    "Social Presence": 15,
    "Contact Readiness": 15,
    "Conversion Readiness": 15,
}


class AuditError(Exception):
    """User-facing audit failure with a friendly title and message."""

    def __init__(self, title: str, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.title = title
        self.message = message
        self.status_code = status_code


def _is_blocked_ip(address: ipaddress._BaseAddress) -> bool:
    return (
        address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_private
        or address.is_unspecified
    )


def _validate_host(host: str) -> None:
    normalized_host = (host or "").strip().rstrip(".").lower()
    if not normalized_host:
        raise AuditError("Invalid URL", "The website URL is missing a hostname.")
    if normalized_host in {"localhost", "localhost.localdomain"}:
        raise AuditError(
            "Invalid URL",
            "Localhost URLs are not permitted for security reasons.",
        )

    try:
        parsed_ip = ipaddress.ip_address(normalized_host)
    except ValueError:
        parsed_ip = None

    if parsed_ip is not None:
        if _is_blocked_ip(parsed_ip):
            raise AuditError(
                "Invalid URL",
                "The provided URL points to a blocked internal or local address.",
            )
        return

    try:
        resolved_addresses = socket.getaddrinfo(normalized_host, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise AuditError(
            "Invalid URL",
            "We could not resolve the website host to a safe public address.",
        ) from exc

    for _, _, _, _, sockaddr in resolved_addresses:
        ip_address = sockaddr[0]
        try:
            resolved_ip = ipaddress.ip_address(ip_address)
        except ValueError:
            continue
        if _is_blocked_ip(resolved_ip):
            raise AuditError(
                "Invalid URL",
                "The hostname resolves to a blocked internal or local address.",
            )


def validate_url(url: str) -> str:
    if not url:
        raise AuditError("Invalid URL", "Please enter a website URL.")

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise AuditError(
            "Invalid URL",
            "Please enter a safe HTTP or HTTPS website URL.",
        )
    if not parsed.netloc:
        raise AuditError("Invalid URL", "Please enter a complete website URL.")

    hostname = parsed.hostname
    if not hostname:
        raise AuditError("Invalid URL", "The website URL is missing a hostname.")

    _validate_host(hostname)
    return parsed.geturl()


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if url and not url.lower().startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


def is_valid_url(url: str) -> bool:
    try:
        validate_url(url)
    except AuditError:
        return False
    return True


def _safe_request(url: str, *, method: str = "GET", timeout: int = REQUEST_TIMEOUT, allow_redirects: bool = True):
    current_url = validate_url(url)
    session = requests.Session()
    redirect_count = 0
    while True:
        response = session.request(
            method,
            current_url,
            headers=REQUEST_HEADERS,
            timeout=timeout,
            allow_redirects=False,
        )
        response.url = current_url
        if not allow_redirects:
            return response
        if response.is_redirect or response.is_permanent_redirect:
            redirect_count += 1
            if redirect_count > 5:
                raise AuditError(
                    "Too Many Redirects",
                    "The website redirected too many times, so the audit was stopped for safety.",
                )
            location = response.headers.get("Location")
            if not location:
                return response
            current_url = urljoin(current_url, location)
            validate_url(current_url)
            continue
        return response


def fetch_website(url: str) -> Dict:
    start = time.perf_counter()
    try:
        response = _safe_request(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        response_time = round((time.perf_counter() - start) * 1000)
        return {"response": response, "response_time_ms": response_time}
    except requests.exceptions.SSLError as exc:
        raise AuditError(
            "SSL Certificate Error",
            "The website has an SSL certificate problem. Ask the site owner to renew or fix the certificate.",
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise AuditError(
            "Website Timeout",
            "The website took too long to respond. Try again later or check the hosting performance.",
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise AuditError(
            "Website Not Reachable",
            "The domain could not be reached. Check the URL, DNS settings, or hosting status.",
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise AuditError(
            "Request Failed",
            "The website could not be audited because the request failed.",
        ) from exc


def get_title(soup: BeautifulSoup) -> str:
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return "Not Found"


def get_meta_description(soup: BeautifulSoup) -> str:
    meta = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    if meta and meta.get("content"):
        return meta["content"].strip()
    return "Missing"


def get_h1(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(" ", strip=True)
    return "Not Found"


def images_without_alt(soup: BeautifulSoup) -> List[str]:
    missing = []
    for image in soup.find_all("img"):
        alt = image.get("alt")
        src = image.get("src") or image.get("data-src") or "inline/unknown image"
        if not alt or not alt.strip():
            missing.append(src)
    return missing


def resource_exists(base_url: str, path: str) -> bool:
    try:
        url = urljoin(base_url.rstrip("/") + "/", path)
        response = _safe_request(url, timeout=6, allow_redirects=True)
        return response.status_code == 200
    except (AuditError, requests.RequestException):
        return False


def has_robots(base_url: str) -> bool:
    return resource_exists(base_url, "robots.txt")


def has_sitemap(base_url: str) -> bool:
    return resource_exists(base_url, "sitemap.xml")


def get_open_graph(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    tags = {"og:title": None, "og:description": None, "og:image": None}
    for name in tags:
        tag = soup.find("meta", property=name)
        if tag and tag.get("content"):
            tags[name] = tag["content"].strip()
    return tags


def has_viewport(soup: BeautifulSoup) -> bool:
    tag = soup.find("meta", attrs={"name": re.compile("^viewport$", re.I)})
    return bool(tag and tag.get("content"))


def get_canonical(soup: BeautifulSoup) -> str:
    tag = soup.find("link", rel=lambda value: value and "canonical" in value)
    if tag and tag.get("href"):
        return tag["href"].strip()
    return "Missing"


def has_favicon(soup: BeautifulSoup, base_url: str) -> bool:
    icon = soup.find("link", rel=lambda value: value and "icon" in value.lower())
    return bool(icon and icon.get("href")) or resource_exists(base_url, "favicon.ico")


def get_social_links(soup: BeautifulSoup) -> Dict[str, List[str]]:
    links = [a.get("href", "") for a in soup.find_all("a", href=True)]
    found = {}
    for name, domain in SOCIAL_NETWORKS.items():
        matches = sorted({link for link in links if domain in link.lower()})
        if matches:
            found[name] = matches
    if "X (Twitter)" in found and "Twitter" in found:
        found["X (Twitter)"].extend(found.pop("Twitter"))
    elif "Twitter" in found:
        found["X (Twitter)"] = found.pop("Twitter")
    return found


def get_emails(html: str) -> List[str]:
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html)
    return sorted(set(emails))


def get_phones(html: str) -> List[str]:
    phones = re.findall(
        r"(?:\+?\d{1,3}[\s.-]?)?(?:\(\d+\)[\s.-]?)?[0-9][0-9\s.-]{6,}",
        html,
    )
    cleaned = [re.sub(r"[\s.-]", "", phone) for phone in phones]
    return sorted({phone for phone in cleaned if len(phone) >= 7})


def https_enabled(url: str) -> bool:
    return url.lower().startswith("https://")


def get_security_headers(headers: Dict[str, str]) -> Dict[str, bool]:
    return {header: header in headers for header in SECURITY_HEADERS}


def detect_contact_form(soup: BeautifulSoup) -> bool:
    contact_words = ("contact", "message", "enquiry", "inquiry", "name", "email")
    for form in soup.find_all("form"):
        form_text = form.get_text(" ", strip=True).lower()
        inputs = " ".join(
            str(input_tag.get("name", "")) + " " + str(input_tag.get("placeholder", ""))
            for input_tag in form.find_all(["input", "textarea"])
        ).lower()
        if any(word in form_text or word in inputs for word in contact_words):
            return True
    return False


def detect_newsletter_form(soup: BeautifulSoup) -> bool:
    words = ("newsletter", "subscribe", "updates", "mailing list")
    for form in soup.find_all("form"):
        text = form.get_text(" ", strip=True).lower()
        attrs = " ".join(str(value) for value in form.attrs.values()).lower()
        if any(word in text or word in attrs for word in words):
            return True
    return False


def detect_cta(soup: BeautifulSoup) -> bool:
    cta_words = (
        "contact",
        "book",
        "call",
        "quote",
        "schedule",
        "buy",
        "shop",
        "enquire",
        "inquire",
        "get started",
        "start now",
        "request demo",
    )
    for tag in soup.find_all(["a", "button"]):
        text = tag.get_text(" ", strip=True).lower()
        href = tag.get("href", "").lower()
        if any(word in text or word in href for word in cta_words):
            return True
    return False


def detect_contact_page(soup: BeautifulSoup) -> bool:
    for link in soup.find_all("a", href=True):
        text = link.get_text(" ", strip=True).lower()
        href = link["href"].lower()
        if "contact" in text or "contact" in href:
            return True
    return False


def check_broken_images(soup: BeautifulSoup, base_url: str, limit: int = 12) -> List[str]:
    broken = []
    image_sources = []
    for image in soup.find_all("img"):
        src = image.get("src") or image.get("data-src")
        if src and not src.startswith("data:"):
            image_sources.append(urljoin(base_url, src))

    for src in image_sources[:limit]:
        try:
            response = _safe_request(src, method="HEAD", timeout=5, allow_redirects=True)
            if response.status_code >= 400:
                broken.append(src)
        except (AuditError, requests.RequestException):
            broken.append(src)
    return broken


def add_check(
    checks: List[Dict],
    category: str,
    title: str,
    passed: bool,
    points: int,
    detail: str,
    recommendation: str,
) -> None:
    checks.append(
        {
            "category": category,
            "title": title,
            "passed": bool(passed),
            "points": points,
            "detail": detail,
            "recommendation": recommendation,
        }
    )


def calculate_scores(checks: List[Dict]) -> Dict:
    categories = {category: 0 for category in CATEGORY_MAX_SCORES}
    for check in checks:
        if check["passed"]:
            categories[check["category"]] += check["points"]
    return {
        "categories": categories,
        "max_scores": CATEGORY_MAX_SCORES,
        "overall": sum(categories.values()),
    }
