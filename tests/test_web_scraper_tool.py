import requests
import pytest

from tools.web_scraper_tool import Tools


@pytest.fixture
def tool():
    return Tools()


class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def test_rejects_non_http_urls(tool):
    result = tool.scrape_web_page("ftp://example.com/file")
    assert "Error: url must start with http" in result


def test_extracts_title_and_cleaned_text(tool, monkeypatch):
    html = """
    <html>
      <head><title>My Page</title></head>
      <body>
        <nav>ignore this nav</nav>
        <script>ignore(this);</script>
        <style>.ignore { color: red; }</style>
        <p>Hello   world.</p>
        <footer>ignore this footer</footer>
      </body>
    </html>
    """
    monkeypatch.setattr(requests, "get", lambda url, headers=None, timeout=None: FakeResponse(html))
    result = tool.scrape_web_page("https://example.com")
    assert "Title: My Page" in result
    assert "Source: https://example.com" in result
    assert "Hello world." in result
    assert "ignore" not in result.lower().replace("ignore this footer", "").replace("ignore this nav", "")
    # More directly: none of the stripped-tag content should survive
    assert "ignore(this)" not in result
    assert "color: red" not in result
    assert "ignore this nav" not in result
    assert "ignore this footer" not in result


def test_falls_back_to_url_when_no_title_tag(tool, monkeypatch):
    html = "<html><body><p>No title here.</p></body></html>"
    monkeypatch.setattr(requests, "get", lambda url, headers=None, timeout=None: FakeResponse(html))
    result = tool.scrape_web_page("https://example.com/no-title")
    assert "Title: https://example.com/no-title" in result


def test_truncates_text_beyond_max_chars(tool, monkeypatch):
    tool.valves.MAX_CHARS = 50
    long_text = "word " * 100
    html = f"<html><body><p>{long_text}</p></body></html>"
    monkeypatch.setattr(requests, "get", lambda url, headers=None, timeout=None: FakeResponse(html))
    result = tool.scrape_web_page("https://example.com/long")
    assert "[truncated]" in result
    # Body text portion should be capped at MAX_CHARS plus the marker
    body_start = result.index("\n\n") + 2
    body = result[body_start:]
    assert len(body) <= tool.valves.MAX_CHARS + len("... [truncated]")


def test_http_error_status_is_caught_and_reported(tool, monkeypatch):
    monkeypatch.setattr(requests, "get", lambda url, headers=None, timeout=None: FakeResponse("", status_code=404))
    result = tool.scrape_web_page("https://example.com/missing")
    assert "Error fetching https://example.com/missing" in result


def test_connection_exception_is_caught_and_reported(tool, monkeypatch):
    def boom(*a, **kw):
        raise requests.ConnectionError("no network")
    monkeypatch.setattr(requests, "get", boom)
    result = tool.scrape_web_page("https://example.com/unreachable")
    assert "Error fetching https://example.com/unreachable" in result


def test_uses_configured_timeout(tool, monkeypatch):
    tool.valves.TIMEOUT = 3
    captured = {}

    def fake_get(url, headers=None, timeout=None):
        captured["timeout"] = timeout
        return FakeResponse("<html><body>ok</body></html>")

    monkeypatch.setattr(requests, "get", fake_get)
    tool.scrape_web_page("https://example.com")
    assert captured["timeout"] == 3
