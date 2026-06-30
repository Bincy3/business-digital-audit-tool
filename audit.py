from bs4 import BeautifulSoup

from utils import (
    AuditError,
    add_check,
    calculate_scores,
    check_broken_images,
    detect_contact_form,
    detect_contact_page,
    detect_cta,
    detect_newsletter_form,
    fetch_website,
    get_canonical,
    get_emails,
    get_h1,
    get_meta_description,
    get_open_graph,
    get_phones,
    get_security_headers,
    get_social_links,
    get_title,
    has_favicon,
    has_robots,
    has_sitemap,
    has_viewport,
    https_enabled,
    images_without_alt,
    is_valid_url,
    normalize_url,
)


BLOCKED_STATUS_CODES = {401, 403, 406, 429, 451}
SERVER_ERROR_STATUS_CODES = {500, 502, 503, 504}


def audit_website(business_name: str, industry: str, website_url: str) -> dict:
    """Run a complete digital audit and return dashboard-ready data."""

    website_url = normalize_url(website_url)
    if not is_valid_url(website_url):
        raise AuditError(
            "Invalid URL",
            "Please enter a valid website URL such as https://example.com.",
        )

    fetched = fetch_website(website_url)
    response = fetched["response"]
    response_time_ms = fetched["response_time_ms"]
    status_code = response.status_code

    if status_code in BLOCKED_STATUS_CODES:
        raise AuditError(
            f"Website Blocked the Audit ({status_code})",
            "The website is reachable but blocked the automated request. Try again later or ask the site owner to allow normal browser-like requests.",
            status_code=status_code,
        )

    if status_code == 404:
        raise AuditError(
            "Page Not Found (404)",
            "The website responded, but the requested page does not exist.",
            status_code=status_code,
        )

    if status_code in SERVER_ERROR_STATUS_CODES:
        raise AuditError(
            f"Server Error ({status_code})",
            "The website server returned an error. The site owner should check hosting, uptime, or application logs.",
            status_code=status_code,
        )

    if status_code >= 400:
        raise AuditError(
            f"HTTP Error ({status_code})",
            "The website returned an error response and could not be audited reliably.",
            status_code=status_code,
        )

    soup = BeautifulSoup(response.text, "html.parser")
    title = get_title(soup)
    meta_description = get_meta_description(soup)
    h1 = get_h1(soup)
    missing_alt_images = images_without_alt(soup)
    social_links = get_social_links(soup)
    emails = get_emails(response.text)
    phones = get_phones(response.text)
    robots_found = has_robots(website_url)
    sitemap_found = has_sitemap(website_url)
    open_graph = get_open_graph(soup)
    missing_open_graph = [name for name, value in open_graph.items() if not value]
    viewport_found = has_viewport(soup)
    canonical = get_canonical(soup)
    favicon_found = has_favicon(soup, website_url)
    broken_images = check_broken_images(soup, website_url)
    security_headers = get_security_headers(response.headers)
    present_security_headers = [
        name for name, present in security_headers.items() if present
    ]
    contact_form_found = detect_contact_form(soup)
    cta_found = detect_cta(soup)
    newsletter_found = detect_newsletter_form(soup)
    contact_page_found = detect_contact_page(soup)
    checks = []

    add_check(
        checks,
        "SEO",
        "Page Title",
        title != "Not Found",
        6,
        title,
        "Add a unique, descriptive title tag to improve search visibility.",
    )
    add_check(
        checks,
        "SEO",
        "Meta Description",
        meta_description != "Missing",
        6,
        meta_description,
        "Add a clear meta description that summarizes the offer and includes important keywords.",
    )
    add_check(
        checks,
        "SEO",
        "H1 Tag",
        h1 != "Not Found",
        6,
        h1,
        "Add exactly one clear H1 that explains the page topic or primary offer.",
    )
    add_check(
        checks,
        "SEO",
        "Canonical Tag",
        canonical != "Missing",
        6,
        canonical,
        "Add a canonical link tag to prevent duplicate URL issues.",
    )
    add_check(
        checks,
        "SEO",
        "Open Graph Tags",
        not missing_open_graph,
        6,
        "Complete" if not missing_open_graph else ", ".join(missing_open_graph),
        "Add og:title, og:description, and og:image for better social sharing previews.",
    )

    add_check(
        checks,
        "Technical Basics",
        "HTTPS Enabled",
        https_enabled(website_url),
        5,
        "Enabled" if https_enabled(website_url) else "Disabled",
        "Enable HTTPS and redirect HTTP traffic to the secure version.",
    )
    add_check(
        checks,
        "Technical Basics",
        "Response Time",
        response_time_ms <= 2500,
        5,
        f"{response_time_ms} ms",
        "Improve hosting, caching, image optimization, or server response time.",
    )
    add_check(
        checks,
        "Technical Basics",
        "robots.txt",
        robots_found,
        5,
        "Found" if robots_found else "Missing",
        "Publish a robots.txt file to guide search engine crawlers.",
    )
    add_check(
        checks,
        "Technical Basics",
        "sitemap.xml",
        sitemap_found,
        5,
        "Found" if sitemap_found else "Missing",
        "Publish a sitemap.xml file and keep it updated.",
    )
    add_check(
        checks,
        "Technical Basics",
        "Security Headers",
        len(present_security_headers) >= 3,
        5,
        f"{len(present_security_headers)}/6 present",
        "Add security headers such as CSP, HSTS, X-Frame-Options, and Referrer-Policy.",
    )

    social_points = {
        "Facebook": 3,
        "Instagram": 3,
        "LinkedIn": 3,
        "X (Twitter)": 2,
        "YouTube": 2,
        "GitHub": 2,
    }
    for network, points in social_points.items():
        add_check(
            checks,
            "Social Presence",
            network,
            network in social_links,
            points,
            "Found" if network in social_links else "Missing",
            f"Link an active {network} profile from the website.",
        )

    add_check(
        checks,
        "Contact Readiness",
        "Email Detection",
        bool(emails),
        5,
        ", ".join(emails) if emails else "Missing",
        "Show a public email address or route users clearly to an enquiry form.",
    )
    add_check(
        checks,
        "Contact Readiness",
        "Phone Number Detection",
        bool(phones),
        5,
        ", ".join(phones) if phones else "Missing",
        "Show a phone number for fast buyer contact.",
    )
    add_check(
        checks,
        "Contact Readiness",
        "Contact Form Detection",
        contact_form_found,
        5,
        "Found" if contact_form_found else "Missing",
        "Add a simple contact form with name, email, message, and submit fields.",
    )

    add_check(
        checks,
        "Conversion Readiness",
        "CTA Button",
        cta_found,
        5,
        "Found" if cta_found else "Missing",
        "Add a prominent call-to-action such as Book a Call, Get a Quote, or Contact Us.",
    )
    add_check(
        checks,
        "Conversion Readiness",
        "Newsletter Form",
        newsletter_found,
        5,
        "Found" if newsletter_found else "Missing",
        "Add a newsletter or lead capture form where relevant.",
    )
    add_check(
        checks,
        "Conversion Readiness",
        "Contact Page",
        contact_page_found,
        5,
        "Found" if contact_page_found else "Missing",
        "Add a visible contact page link in the main navigation or footer.",
    )

    scores = calculate_scores(checks)
    recommendations = [
        check["recommendation"] for check in checks if not check["passed"]
    ]
    if not missing_alt_images:
        image_alt_status = "All checked images include alt text"
    else:
        image_alt_status = f"{len(missing_alt_images)} image(s) missing alt text"

    if not broken_images:
        broken_image_status = "No broken images found in sampled images"
    else:
        broken_image_status = f"{len(broken_images)} broken image(s) found"

    extra_checks = [
        {
            "title": "Website Reachability",
            "passed": True,
            "detail": "Reachable",
            "recommendation": "",
        },
        {
            "title": "HTTP Status Code",
            "passed": 200 <= status_code < 400,
            "detail": str(status_code),
            "recommendation": "Resolve HTTP errors and redirect issues.",
        },
        {
            "title": "Images without ALT text",
            "passed": not missing_alt_images,
            "detail": image_alt_status,
            "recommendation": "Add helpful alt text to every important image.",
        },
        {
            "title": "Mobile Viewport Tag",
            "passed": viewport_found,
            "detail": "Found" if viewport_found else "Missing",
            "recommendation": "Add a mobile viewport meta tag for responsive layouts.",
        },
        {
            "title": "Favicon",
            "passed": favicon_found,
            "detail": "Found" if favicon_found else "Missing",
            "recommendation": "Add a favicon so the brand looks polished in browser tabs.",
        },
        {
            "title": "Broken Images",
            "passed": not broken_images,
            "detail": broken_image_status,
            "recommendation": "Fix or remove broken image URLs.",
        },
    ]

    for check in extra_checks:
        if not check["passed"] and check["recommendation"]:
            recommendations.append(check["recommendation"])

    return {
        "business_name": business_name.strip(),
        "industry": industry.strip(),
        "website_url": website_url,
        "final_url": response.url,
        "status_code": status_code,
        "response_time_ms": response_time_ms,
        "overall_score": scores["overall"],
        "category_scores": scores["categories"],
        "category_max_scores": scores["max_scores"],
        "checks": checks,
        "extra_checks": extra_checks,
        "recommendations": recommendations,
        "details": {
            "title": title,
            "meta_description": meta_description,
            "h1": h1,
            "missing_alt_images": missing_alt_images,
            "social_links": social_links,
            "emails": emails,
            "phones": phones,
            "robots_found": robots_found,
            "sitemap_found": sitemap_found,
            "open_graph": open_graph,
            "viewport_found": viewport_found,
            "canonical": canonical,
            "favicon_found": favicon_found,
            "broken_images": broken_images,
            "security_headers": security_headers,
            "contact_form_found": contact_form_found,
            "cta_found": cta_found,
            "newsletter_found": newsletter_found,
            "contact_page_found": contact_page_found,
        },
    }
