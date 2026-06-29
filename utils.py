import requests
import re


def fetch_website(url):
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
            timeout=10,
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
    # Indian mobile numbers only
    phones = re.findall(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        html
    )

    phones = sorted(list(set(phones)))

    if phones:
        return phones

    return ["Not Found"]


def https_enabled(url):
    return url.lower().startswith("https://")


def calculate_score(title, meta, social, https):
    score = 100

    if title == "Not Found":
        score -= 20

    if meta == "Missing":
        score -= 20

    if social == ["Not Found"]:
        score -= 20

    if not https:
        score -= 20

    if score < 0:
        score = 0

    return score