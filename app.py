import logging
import os

from flask import Flask, render_template, request

from audit import audit_website
from report import save_reports
from utils import AuditError


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


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
        save_reports(result)
        return render_template("report.html", result=result, saved_report=False)
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
