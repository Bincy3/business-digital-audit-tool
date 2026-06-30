from pathlib import Path

from flask import render_template


REPORTS_DIR = Path("reports")
HTML_REPORT_PATH = REPORTS_DIR / "report.html"
TEXT_REPORT_PATH = REPORTS_DIR / "report.txt"


def ensure_reports_dir() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)


def save_reports(result: dict) -> None:
    ensure_reports_dir()
    save_html_report(result)
    save_text_report(result)


def save_html_report(result: dict) -> None:
    html = render_template("report.html", result=result, saved_report=True)
    HTML_REPORT_PATH.write_text(html, encoding="utf-8")


def save_text_report(result: dict) -> None:
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

    TEXT_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
