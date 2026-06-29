from bs4 import BeautifulSoup
from utils import (
    fetch_website,
    get_title,
    get_meta_description,
    get_social_links,
    get_email,
    get_phone,
    https_enabled,
    calculate_score
)


def audit_website(business, industry, website):

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
            "Recommendations": [
                "Unable to connect to the website."
            ]
        }

    soup = BeautifulSoup(response.text, "html.parser")

    title = get_title(soup)
    meta = get_meta_description(soup)
    social = get_social_links(soup)
    emails = get_email(response.text)
    phones = get_phone(response.text)

    https = https_enabled(website)

    score = calculate_score(
        title,
        meta,
        social,
        https
    )

    recommendations = []

    if title == "Not Found":
        recommendations.append("Add a proper page title.")

    if meta == "Missing":
        recommendations.append("Add a meta description.")

    if social == ["Not Found"]:
        recommendations.append("Add social media links.")

    if emails == ["Not Found"]:
        recommendations.append("Provide a public contact email.")

    if phones == ["Not Found"]:
        recommendations.append("Provide a contact phone number.")

    if not https:
        recommendations.append("Enable HTTPS.")

    if score >= 80:
        recommendations.append("Great digital presence!")

    return {
        "Business": business,
        "Industry": industry,
        "Website": website,
        "Status": "Reachable",
        "HTTPS": "Enabled" if https else "Disabled",
        "Title": title,
        "Meta": meta,
        "Social": social,
        "Email": emails,
        "Phone": phones,
        "Score": score,
        "Recommendations": recommendations
    }