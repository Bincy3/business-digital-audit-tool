import types

import pytest

import audit


class DummyResponse:
    def __init__(self, text="", status_code=200, headers=None, url="https://example.com"):
        self.text = text
        self.status_code = status_code
        self.headers = headers or {}
        self.url = url


@pytest.fixture
def audit_setup(monkeypatch):
    def _run(html="", status_code=200, headers=None, url="https://example.com"):
        monkeypatch.setattr(
            audit,
            "fetch_website",
            lambda website_url: {"response": DummyResponse(html, status_code, headers, url), "response_time_ms": 120},
        )
        monkeypatch.setattr(audit, "has_robots", lambda base_url: True)
        monkeypatch.setattr(audit, "has_sitemap", lambda base_url: True)
        monkeypatch.setattr(audit, "check_broken_images", lambda soup, base_url, limit=12: [])
        monkeypatch.setattr(audit, "has_favicon", lambda soup, base_url: True)
        return audit.audit_website("Acme", "Marketing", "https://example.com")

    return _run


def test_detects_html_title_and_meta_description(audit_setup):
    result = audit_setup(
        '<html><head><title>Example Business</title><meta name="description" content="Example description"></head><body></body></html>'
    )

    assert result["details"]["title"] == "Example Business"
    assert result["details"]["meta_description"] == "Example description"


def test_detects_h1_tag(audit_setup):
    result = audit_setup('<html><body><h1>Welcome to our site</h1></body></html>')

    assert result["details"]["h1"] == "Welcome to our site"


def test_detects_https_enabled(audit_setup):
    result = audit_setup('<html><body></body></html>', url="https://example.com")

    assert result["category_scores"]["Technical Basics"] >= 0
    assert any(check["title"] == "HTTPS Enabled" and check["passed"] for check in result["checks"])


def test_detects_robots_and_sitemap(audit_setup):
    result = audit_setup('<html><body></body></html>')

    assert result["details"]["robots_found"] is True
    assert result["details"]["sitemap_found"] is True


def test_detects_open_graph_and_viewport(audit_setup):
    result = audit_setup(
        '<html><head><meta property="og:title" content="Acme" /><meta property="og:description" content="Description" /><meta property="og:image" content="https://example.com/image.png" /><meta name="viewport" content="width=device-width, initial-scale=1" /></head><body></body></html>'
    )

    assert result["details"]["open_graph"]["og:title"] == "Acme"
    assert result["details"]["viewport_found"] is True


def test_detects_social_and_contact_signals(audit_setup):
    result = audit_setup(
        '<html><body><a href="https://linkedin.com/company/acme">LinkedIn</a><a href="mailto:hello@example.com">Email</a><form><input name="name" /><textarea></textarea></form></body></html>'
    )

    assert "LinkedIn" in result["details"]["social_links"]
    assert result["details"]["emails"] == ["hello@example.com"]
    assert result["details"]["contact_form_found"] is True
