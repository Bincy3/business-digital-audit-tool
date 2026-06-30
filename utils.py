import requests
import re
import validators


def is_valid_url(url):
    return bool(validators.url(url))


def fetch_website(url, timeout=10):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
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


def has_sitemap(base_url):
    if not base_url.endswith("/"):
        base_url = base_url + "/"
    try:
        r = requests.get(base_url + "sitemap.xml", timeout=6)
        return r.status_code == 200
    except requests.RequestException:
        return False


def has_robots(base_url):
    if not base_url.endswith("/"):
        base_url = base_url + "/"
    try:
        r = requests.get(base_url + "robots.txt", timeout=6)
        return r.status_code == 200
    except requests.RequestException:
        return False


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


def calculate_scores(soup, html, website, social, emails, phones):
    # Scoring weights
    scores = {
        "SEO": 0,
        "Contact": 0,
        "Social": 0,
        "Technical": 0,
        "Conversion": 0
    }

    # SEO (30): title(10), meta(10), h1(5), viewport(5)
    scores["SEO"] += 10 if get_title(soup) != "Not Found" else 0
    scores["SEO"] += 10 if get_meta_description(soup) != "Missing" else 0
    scores["SEO"] += 5 if get_h1(soup) != "Not Found" else 0
    scores["SEO"] += 5 if has_viewport(soup) else 0

    # Contact readiness (20): email(10), phone(10)
    scores["Contact"] += 10 if emails != ["Not Found"] else 0
    scores["Contact"] += 10 if phones != ["Not Found"] else 0

    # Social presence (20): any social link
    scores["Social"] += 20 if social != ["Not Found"] else 0

    # Technical basics (20): HTTPS(10), sitemap(5), robots(5)
    scores["Technical"] += 10 if https_enabled(website) else 0
    scores["Technical"] += 5 if has_sitemap(website) else 0
    scores["Technical"] += 5 if has_robots(website) else 0

    # Conversion readiness (10): images alt (5), OG tags (5)
    imgs_missing = images_without_alt(soup)
    scores["Conversion"] += 5 if len(imgs_missing) == 0 else 0
    og, missing_og = get_open_graph(soup)
    scores["Conversion"] += 5 if len(missing_og) == 0 else 0

    total = sum(scores.values())

    return {
        "categories": scores,
        "total": total,
        "missing_images": imgs_missing,
        "missing_og": missing_og
    }