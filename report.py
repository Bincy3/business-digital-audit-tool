from pathlib import Path

from flask import render_template

from database import REPORTS_DIR, add_audit, build_report_filenames


REPORTS_DIR.mkdir(exist_ok=True)


def save_reports(result: dict) -> dict:
    html_filename, txt_filename = build_report_filenames(result["business_name"])
    html_path = REPORTS_DIR / html_filename
    txt_path = REPORTS_DIR / txt_filename

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

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    audit_id = add_audit(
        result["business_name"],
        result["website_url"],
        result["overall_score"],
        html_filename,
        txt_filename,
        "Complete",
    )

    return {
        "html_filename": html_filename,
        "txt_filename": txt_filename,
        "audit_id": audit_id,
    }
