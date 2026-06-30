import requests
import re
import validators
from urllib.parse import urljoin


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )
}

CATEGORY_MAX_SCORES = {
    "SEO": 30,
    "Contact Readiness": 20,
    "Social Presence": 15,
    "Technical Basics": 25,
    "Conversion Readiness": 10,
}


def is_valid_url(url):
    return bool(validators.url(url))


def fetch_website(url, timeout=10):
    try:
        response = requests.get(
            url,
            headers=REQUEST_HEADERS,
            timeout=timeout,
            allow_redirects=True
        )
        return response
    except requests.exceptions.RequestException:
        return None


def get_title(soup):
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return "Not Found"


def get_meta_description(soup):
    meta = soup.find("meta", attrs={"name": "description"})

    if meta and meta.get("content"):
        return meta["content"].strip()

    return "Missing"


def get_h1(soup):
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)
    return "Not Found"


def images_without_alt(soup):
    imgs = []
    for img in soup.find_all("img"):
        alt = img.get("alt")
        src = img.get("src") or img.get("data-src") or ""
        if not alt or not alt.strip():
            imgs.append(src)
    return imgs


def resource_exists(base_url, path):
    try:
        url = urljoin(base_url.rstrip("/") + "/", path)
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=6)
        return response.status_code == 200
    except requests.RequestException:
        return False


def has_sitemap(base_url):
    return resource_exists(base_url, "sitemap.xml")


def has_robots(base_url):
    return resource_exists(base_url, "robots.txt")


def get_open_graph(soup):
    og_tags = {
        "og:title": None,
        "og:description": None,
        "og:image": None
    }

    for prop in og_tags.keys():
        tag = soup.find("meta", property=prop)
        if tag and tag.get("content"):
            og_tags[prop] = tag.get("content").strip()

    missing = [k for k, v in og_tags.items() if not v]
    return og_tags, missing


def has_viewport(soup):
    tag = soup.find("meta", attrs={"name": "viewport"})
    return bool(tag and tag.get("content"))


def has_conversion_cta(soup):
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
    )

    for tag in soup.find_all(["a", "button"]):
        text = tag.get_text(" ", strip=True).lower()
        href = tag.get("href", "").lower()
        if any(word in text or word in href for word in cta_words):
            return True

    return False


def get_social_links(soup):
    links = [a.get("href", "") for a in soup.find_all("a", href=True)]

    social = []

    social_sites = {
        "Facebook": "facebook.com",
        "Instagram": "instagram.com",
        "LinkedIn": "linkedin.com",
        "X": "x.com",
        "Twitter": "twitter.com",
        "YouTube": "youtube.com",
        "GitHub": "github.com"
    }

    for name, keyword in social_sites.items():
        if any(keyword in link.lower() for link in links):
            social.append(name)

    if not social:
        return ["Not Found"]

    return sorted(list(set(social)))


def get_email(html):
    emails = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        html
    )

    emails = sorted(list(set(emails)))

    if emails:
        return emails

    return ["Not Found"]


def get_phone(html):
    phones = re.findall(
        r"(?:\+?\d{1,3}[\s-]?)?(?:\(\d+\)[\s-]?)?[0-9][0-9\s-]{6,}",
        html
    )

    phones = [re.sub(r"[\s-]", "", p) for p in phones]
    phones = sorted(list(set(phones)))

    if phones:
        return phones

    return ["Not Found"]


def https_enabled(url):
    return url.lower().startswith("https://")


def calculate_scores(checks):
    scores = {category: 0 for category in CATEGORY_MAX_SCORES}

    for check in checks:
        if check["passed"]:
            scores[check["category"]] += check["points"]

    return {
        "categories": scores,
        "max_scores": CATEGORY_MAX_SCORES,
        "total": sum(scores.values()),
    }
