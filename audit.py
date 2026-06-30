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
    has_conversion_cta,
    calculate_scores,
)


def failed_report(business, industry, website, status, recommendation):
    return {
        "Business": business,
        "Industry": industry,
        "Website": website,
        "Status": status,
        "HTTPS": "Unknown",
        "Title": "Not Found",
        "Meta": "Missing",
        "H1": "Not Found",
        "Social": ["Not Found"],
        "Email": ["Not Found"],
        "Phone": ["Not Found"],
        "Score": 0,
        "Categories": {},
        "MaxScores": {},
        "Checks": [],
        "MissingImages": [],
        "MissingOG": [],
        "Recommendations": [recommendation],
    }


def audit_website(business, industry, website):

    if not is_valid_url(website):
        return failed_report(
            business,
            industry,
            website,
            "Invalid URL",
            "Provided website URL is not valid. Use a full domain such as https://example.com.",
        )

    response = fetch_website(website)

    if response is None:
        return failed_report(
            business,
            industry,
            website,
            "Not Reachable",
            "Unable to connect to the website. Check the URL, DNS, SSL certificate, or hosting status.",
        )

    if response.status_code in (401, 403, 406, 429, 451, 502, 503, 504):
        blocked = failed_report(
            business,
            industry,
            website,
            f"Blocked or Error ({response.status_code})",
            f"Website returned HTTP {response.status_code}. It may be blocking automated audits or having a server issue.",
        )
        blocked["HTTPS"] = "Enabled" if https_enabled(website) else "Disabled"
        return blocked

    if response.status_code >= 400:
        return failed_report(
            business,
            industry,
            website,
            f"HTTP Error ({response.status_code})",
            f"Website returned HTTP {response.status_code}. Fix the page response before running a full audit.",
        )

    soup = BeautifulSoup(response.text, "html.parser")

    title = get_title(soup)
    meta = get_meta_description(soup)
    h1 = get_h1(soup)
    social = get_social_links(soup)
    emails = get_email(response.text)
    phones = get_phone(response.text)

    https = https_enabled(website)
    sitemap = has_sitemap(website)
    robots = has_robots(website)
    viewport = has_viewport(soup)
    og, missing_og = get_open_graph(soup)
    imgs_missing = images_without_alt(soup)
    cta = has_conversion_cta(soup)

    checks = [
        {
            "title": "Page title",
            "category": "SEO",
            "passed": title != "Not Found",
            "points": 8,
            "detail": title,
            "recommendation": "Add a concise, descriptive page title.",
        },
        {
            "title": "Meta description",
            "category": "SEO",
            "passed": meta != "Missing",
            "points": 8,
            "detail": meta,
            "recommendation": "Add a persuasive meta description for search snippets.",
        },
        {
            "title": "H1 heading",
            "category": "SEO",
            "passed": h1 != "Not Found",
            "points": 7,
            "detail": h1,
            "recommendation": "Add one clear H1 that explains the page offer.",
        },
        {
            "title": "Images include alt text",
            "category": "SEO",
            "passed": len(imgs_missing) == 0,
            "points": 7,
            "detail": "All images have alt text" if not imgs_missing else f"{len(imgs_missing)} image(s) missing alt text",
            "recommendation": "Add useful alt text to important images.",
        },
        {
            "title": "Mobile viewport tag",
            "category": "Technical Basics",
            "passed": viewport,
            "points": 5,
            "detail": "Present" if viewport else "Missing",
            "recommendation": "Add a responsive viewport meta tag.",
        },
        {
            "title": "HTTPS enabled",
            "category": "Technical Basics",
            "passed": https,
            "points": 8,
            "detail": "Enabled" if https else "Disabled",
            "recommendation": "Enable HTTPS and redirect HTTP traffic to HTTPS.",
        },
        {
            "title": "sitemap.xml",
            "category": "Technical Basics",
            "passed": sitemap,
            "points": 6,
            "detail": "Found" if sitemap else "Not found",
            "recommendation": "Publish a sitemap.xml file for search engines.",
        },
        {
            "title": "robots.txt",
            "category": "Technical Basics",
            "passed": robots,
            "points": 6,
            "detail": "Found" if robots else "Not found",
            "recommendation": "Publish a robots.txt file with crawl guidance.",
        },
        {
            "title": "Email contact",
            "category": "Contact Readiness",
            "passed": emails != ["Not Found"],
            "points": 10,
            "detail": ", ".join(emails),
            "recommendation": "Show a public contact email or enquiry form path.",
        },
        {
            "title": "Phone contact",
            "category": "Contact Readiness",
            "passed": phones != ["Not Found"],
            "points": 10,
            "detail": ", ".join(phones),
            "recommendation": "Show a public phone number for direct enquiries.",
        },
        {
            "title": "Social links",
            "category": "Social Presence",
            "passed": social != ["Not Found"],
            "points": 15,
            "detail": ", ".join(social),
            "recommendation": "Link active social profiles from the website.",
        },
        {
            "title": "Open Graph tags",
            "category": "Conversion Readiness",
            "passed": len(missing_og) == 0,
            "points": 5,
            "detail": "Complete" if not missing_og else "Missing: " + ", ".join(missing_og),
            "recommendation": "Add og:title, og:description, and og:image tags.",
        },
        {
            "title": "Conversion call-to-action",
            "category": "Conversion Readiness",
            "passed": cta,
            "points": 5,
            "detail": "Found" if cta else "Not found",
            "recommendation": "Add a clear contact, booking, quote, or enquiry call-to-action.",
        },
    ]

    scores = calculate_scores(checks)

    recommendations = [
        check["recommendation"]
        for check in checks
        if not check["passed"]
    ]
    if scores["total"] >= 80:
        recommendations.append("Strong digital presence. Keep improving content quality, local proof, and conversion paths.")

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
        "MaxScores": scores["max_scores"],
        "Checks": checks,
        "MissingImages": imgs_missing,
        "MissingOG": missing_og,
        "OpenGraph": og,
        "Recommendations": recommendations
    }
