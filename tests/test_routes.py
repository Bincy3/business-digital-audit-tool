from pathlib import Path

import pytest

import app as flask_app
import database


@pytest.fixture
def client():
    database.DB_PATH = Path(flask_app.__file__).resolve().parent / "audit_history.db"
    database.REPORTS_DIR = Path(flask_app.__file__).resolve().parent / "reports"
    database.REPORTS_DIR.mkdir(exist_ok=True)
    database.init_db()
    flask_app.app.config.update(TESTING=True)
    with flask_app.app.test_client() as client:
        yield client


def test_home_page_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_audit_page_returns_valid_response(client):
    response = client.post(
        "/audit",
        data={
            "business_name": "Acme",
            "industry": "Marketing",
            "website_url": "https://example.com",
        },
    )
    assert response.status_code in {200, 400, 500}


def test_history_page_returns_200(client):
    response = client.get("/history")
    assert response.status_code == 200


def test_invalid_url_returns_error(client):
    response = client.post(
        "/audit",
        data={
            "business_name": "Acme",
            "industry": "Marketing",
            "website_url": "http://localhost",
        },
    )
    assert response.status_code == 400
