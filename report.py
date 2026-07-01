from pathlib import Path

from flask import render_template

from database import REPORTS_DIR, add_audit, build_report_filenames


REPORTS_DIR.mkdir(exist_ok=True)


def build_whatsapp_message(result: dict) -> str:
    recommendation = ""
    recommendations = result.get("recommendations") or []
    if recommendations:
        recommendation = recommendations[0]
    else:
        recommendation = "Continue improving your site speed, visibility, and conversion experience."
    return (
        f"Hi {result['business_name']}, I completed a digital audit for your website and your overall score is "
        f"{result['overall_score']}/100. The main opportunity is: {recommendation}. I can help you turn this into a clear action plan."
    )


def save_reports(result: dict) -> dict:
    html_filename, txt_filename = build_report_filenames(result["business_name"])
    html_path = REPORTS_DIR / html_filename
    txt_path = REPORTS_DIR / txt_filename

    result["whatsapp_message"] = build_whatsapp_message(result)

    html = render_template("report.html", result=result, saved_report=True)
    html_path.write_text(html, encoding="utf-8")

    lines = [
        "BUSINESS DIGITAL AUDIT REPORT",
        "=" * 60,
        "",
        f"Business Name : {result['business_name']}",
        f"Industry      : {result['industry']}",
        f"Website URL   : {result['website_url']}",
        f"Final URL     : {result['final_url']}",
        f"HTTP Status   : {result['status_code']}",
        f"Response Time : {result['response_time_ms']} ms",
        f"Overall Score : {result['overall_score']}/100",
        "",
        "CATEGORY SCORES",
        "-" * 60,
    ]

    for category, score in result["category_scores"].items():
        max_score = result["category_max_scores"][category]
        lines.append(f"{category}: {score}/{max_score}")

    lines.extend(["", "AUDIT CHECKLIST", "-" * 60])
    for check in result["checks"]:
        status = "PASS" if check["passed"] else "NEEDS WORK"
        lines.append(
            f"{status}: {check['title']} | {check['category']} | {check['detail']}"
        )

    lines.extend(["", "ADDITIONAL CHECKS", "-" * 60])
    for check in result["extra_checks"]:
        status = "PASS" if check["passed"] else "NEEDS WORK"
        lines.append(f"{status}: {check['title']} | {check['detail']}")

    lines.extend(["", "RECOMMENDATIONS", "-" * 60])
    if result["recommendations"]:
        lines.extend(f"- {item}" for item in result["recommendations"])
    else:
        lines.append("- Strong audit result. Continue monitoring performance and conversion quality.")

    lines.extend(["", "WHATSAPP MESSAGE", "-" * 60, result["whatsapp_message"]])

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    audit_id = add_audit(
        result["business_name"],
        result["industry"],
        result["website_url"],
        result["overall_score"],
        result["category_scores"].get("SEO", 0),
        result["category_scores"].get("Technical Basics", 0),
        result["category_scores"].get("Social Presence", 0),
        result["category_scores"].get("Contact Readiness", 0),
        result["category_scores"].get("Conversion Readiness", 0),
        html_filename,
        txt_filename,
        result.get("recommendations", []),
        result["whatsapp_message"],
        "Complete",
    )

    return {
        "html_filename": html_filename,
        "txt_filename": txt_filename,
        "audit_id": audit_id,
        "whatsapp_message": result["whatsapp_message"],
    }
