from bs4 import BeautifulSoup
from utils import (
    fetch_website,
    is_valid_url,
    get_title,
    get_meta_description,
    get_h1,
    get_social_links,
    get_email,
    get_phone,
    https_enabled,
    images_without_alt,
    has_sitemap,
    has_robots,
    get_open_graph,
    has_viewport,
    calculate_scores,
)


def audit_website(business, industry, website):

    # Validate URL
    if not is_valid_url(website):
        return {
            "Business": business,
            "Industry": industry,
            "Website": website,
            "Status": "Invalid URL",
            "HTTPS": "Unknown",
            "Title": "Not Found",
            "Meta": "Missing",
            "Social": ["Not Found"],
            "Email": ["Not Found"],
            "Phone": ["Not Found"],
            "Score": 0,
            "Categories": {},
            "Recommendations": ["Provided website URL is not valid."]
        }

    response = fetch_website(website)

    if response is None:
        return {
            "Business": business,
            "Industry": industry,
            "Website": website,
            "Status": "Not Reachable",
            "HTTPS": "Unknown",
            "Title": "Not Found",
            "Meta": "Missing",
            "Social": ["Not Found"],
            "Email": ["Not Found"],
            "Phone": ["Not Found"],
            "Score": 0,
            "Categories": {},
            "Recommendations": ["Unable to connect to the website."]
        }

    # Detect blocked or error status codes
    if response.status_code in (403, 429, 502, 503, 504):
        return {
            "Business": business,
            "Industry": industry,
            "Website": website,
            "Status": f"Blocked or Error ({response.status_code})",
            "HTTPS": "Enabled" if https_enabled(website) else "Disabled",
            "Title": "Not Found",
            "Meta": "Missing",
            "Social": ["Not Found"],
            "Email": ["Not Found"],
            "Phone": ["Not Found"],
            "Score": 0,
            "Categories": {},
            "Recommendations": [f"Website returned HTTP {response.status_code}."]
        }

    soup = BeautifulSoup(response.text, "html.parser")

    title = get_title(soup)
    meta = get_meta_description(soup)
    h1 = get_h1(soup)
    social = get_social_links(soup)
    emails = get_email(response.text)
    phones = get_phone(response.text)

    https = https_enabled(website)

    scores = calculate_scores(soup, response.text, website, social, emails, phones)

    recommendations = []

    if title == "Not Found":
        recommendations.append("Add a proper page title.")

    if meta == "Missing":
        recommendations.append("Add a meta description.")

    if h1 == "Not Found":
        recommendations.append("Add a clear H1 heading.")

    if social == ["Not Found"]:
        recommendations.append("Add social media links.")

    if emails == ["Not Found"]:
        recommendations.append("Provide a public contact email.")

    if phones == ["Not Found"]:
        recommendations.append("Provide a contact phone number.")

    if not https:
        recommendations.append("Enable HTTPS (TLS) for the site.")

    if scores["total"] >= 80:
        recommendations.append("Great digital presence! Keep improving content and SEO.")

    og, missing_og = get_open_graph(soup)
    imgs_missing = images_without_alt(soup)

    if missing_og:
        recommendations.append("Add Open Graph tags for better social sharing.")

    if imgs_missing:
        recommendations.append("Add alt attributes for key images to improve accessibility and SEO.")

    return {
        "Business": business,
        "Industry": industry,
        "Website": website,
        "Status": "Reachable",
        "HTTPS": "Enabled" if https else "Disabled",
        "Title": title,
        "Meta": meta,
        "H1": h1,
        "Social": social,
        "Email": emails,
        "Phone": phones,
        "Score": scores["total"],
        "Categories": scores["categories"],
        "MissingImages": imgs_missing,
        "MissingOG": missing_og,
        "Recommendations": recommendations
    }