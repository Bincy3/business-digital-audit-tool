import pytest

from utils import AuditError, is_safe_url, validate_safe_url


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost",
        "https://127.0.0.1",
        "https://192.168.1.10",
        "https://10.0.0.5",
        "https://172.16.0.1",
        "file:///tmp/test",
        "data:text/plain,hello",
        "javascript:alert(1)",
    ],
)
def test_blocked_urls_are_rejected(url):
    assert is_safe_url(url) is False


def test_valid_https_url_is_allowed():
    assert is_safe_url("https://example.com") is True


def test_valid_http_url_is_allowed():
    assert is_safe_url("http://example.com") is True


def test_validate_safe_url_raises_for_localhost():
    with pytest.raises(AuditError):
        validate_safe_url("http://localhost")
