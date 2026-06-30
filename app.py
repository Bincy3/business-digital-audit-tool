import logging
import os
from pathlib import Path

from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from audit import audit_website
from database import (
    DatabaseError,
    REPORTS_DIR,
    delete_audit,
    get_audit,
    get_history_stats,
    init_db,
    list_audits,
)
from report import save_reports
from utils import AuditError


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    init_db()
except DatabaseError as error:
    logger.exception("Database initialization failed: %s", error)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/audit", methods=["POST"])
def generate_audit():
    business_name = request.form.get("business_name", "").strip()
    industry = request.form.get("industry", "").strip()
    website_url = request.form.get("website_url", "").strip()

    if not business_name or not industry or not website_url:
        return (
            render_template(
                "error.html",
                title="Missing Information",
                message="Please provide the business name, industry, and website URL.",
                action_label="Back to Audit Form",
                action_url="/",
            ),
            400,
        )

    try:
        result = audit_website(business_name, industry, website_url)
        saved = save_reports(result)
        result["html_filename"] = saved["html_filename"]
        result["txt_filename"] = saved["txt_filename"]
        result["audit_id"] = saved["audit_id"]
        return render_template(
            "report.html",
            result=result,
            saved_report=False,
            success=True,
        )
    except AuditError as error:
        status_code = 400
        if error.status_code and error.status_code >= 500:
            status_code = 502
        elif error.status_code:
            status_code = 400
        return (
            render_template(
                "error.html",
                title=error.title,
                message=error.message,
                status_code=error.status_code,
                action_label="Try Another Website",
                action_url="/",
            ),
            status_code,
        )
    except DatabaseError as error:
        logger.exception("Database failure: %s", error)
        return (
            render_template(
                "error.html",
                title="Storage Error",
                message="The report was generated, but the history database could not be saved.",
                action_label="Back to Home",
                action_url="/",
            ),
            500,
        )
    except Exception as error:
        logger.exception("Unexpected audit failure: %s", error)
        return (
            render_template(
                "error.html",
                title="Unexpected Error",
                message="Something went wrong while generating the audit. Please try again.",
                action_label="Back to Home",
                action_url="/",
            ),
            500,
        )


@app.route("/history", methods=["GET"])
def audit_history():
    search_business = request.args.get("search_business", "")
    search_website = request.args.get("search_website", "")
    score_filter = request.args.get("score_filter", "")
    sort_by = request.args.get("sort_by", "audit_time")
    order = request.args.get("order", "desc")
    page = int(request.args.get("page", 1))
    page_size = 20

    try:
        audits, total = list_audits(
            search_business=search_business,
            search_website=search_website,
            score_filter=score_filter,
            sort_by=sort_by,
            order=order,
            page=page,
            page_size=page_size,
        )
        stats = get_history_stats()
    except DatabaseError as error:
        logger.exception("Audit history retrieval failed: %s", error)
        return (
            render_template(
                "error.html",
                title="Audit History Error",
                message="Unable to load the audit history at this time.",
                action_label="Back to Home",
                action_url="/",
            ),
            500,
        )

    total_pages = (total + page_size - 1) // page_size
    return render_template(
        "history.html",
        audits=audits,
        total=total,
        page=page,
        total_pages=total_pages,
        search_business=search_business,
        search_website=search_website,
        score_filter=score_filter,
        sort_by=sort_by,
        order=order,
        stats=stats,
    )


@app.route("/view-report/<int:audit_id>", methods=["GET"])
def view_report(audit_id):
    try:
        audit_record = get_audit(audit_id)
    except DatabaseError as error:
        logger.exception("Unable to load audit record: %s", error)
        abort(500)

    if not audit_record:
        abort(404)

    html_path = REPORTS_DIR / audit_record["html_filename"]
    if not html_path.exists():
        return (
            render_template(
                "error.html",
                title="Report Not Found",
                message="The HTML report file is missing or was deleted.",
                action_label="Go to Audit History",
                action_url="/history",
            ),
            404,
        )

    return send_from_directory(REPORTS_DIR, audit_record["html_filename"])


@app.route("/download-html/<int:audit_id>", methods=["GET"])
def download_html(audit_id):
    try:
        audit_record = get_audit(audit_id)
    except DatabaseError as error:
        logger.exception("Unable to load audit record: %s", error)
        abort(500)

    if not audit_record:
        abort(404)

    html_path = REPORTS_DIR / audit_record["html_filename"]
    if not html_path.exists():
        return (
            render_template(
                "error.html",
                title="Report File Missing",
                message="The saved HTML report is no longer available.",
                action_label="Go to Audit History",
                action_url="/history",
            ),
            404,
        )

    return send_from_directory(
        REPORTS_DIR,
        audit_record["html_filename"],
        as_attachment=True,
        download_name=audit_record["html_filename"],
    )


@app.route("/download-txt/<int:audit_id>", methods=["GET"])
def download_txt(audit_id):
    try:
        audit_record = get_audit(audit_id)
    except DatabaseError as error:
        logger.exception("Unable to load audit record: %s", error)
        abort(500)

    if not audit_record:
        abort(404)

    txt_path = REPORTS_DIR / audit_record["txt_filename"]
    if not txt_path.exists():
        return (
            render_template(
                "error.html",
                title="Report File Missing",
                message="The saved TXT report is no longer available.",
                action_label="Go to Audit History",
                action_url="/history",
            ),
            404,
        )

    return send_from_directory(
        REPORTS_DIR,
        audit_record["txt_filename"],
        as_attachment=True,
        download_name=audit_record["txt_filename"],
    )


@app.route("/delete-audit/<int:audit_id>", methods=["POST"])
def delete_audit_route(audit_id):
    try:
        deleted = delete_audit(audit_id)
    except DatabaseError as error:
        logger.exception("Audit deletion failed: %s", error)
        return (
            render_template(
                "error.html",
                title="Delete Failed",
                message="Unable to delete the audit report. Please try again later.",
                action_label="Go to Audit History",
                action_url="/history",
            ),
            500,
        )

    if not deleted:
        return (
            render_template(
                "error.html",
                title="Audit Not Found",
                message="This audit record does not exist or was already removed.",
                action_label="Go to Audit History",
                action_url="/history",
            ),
            404,
        )

    return redirect(url_for("audit_history"))


@app.errorhandler(404)
def not_found(error):
    return (
        render_template(
            "error.html",
            title="Page Not Found",
            message="The page you requested does not exist.",
            action_label="Back to Home",
            action_url="/",
        ),
        404,
    )


@app.errorhandler(500)
def server_error(error):
    return (
        render_template(
            "error.html",
            title="Server Error",
            message="The server could not complete the request. Please try again.",
            action_label="Back to Home",
            action_url="/",
        ),
        500,
    )


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=debug,
    )
