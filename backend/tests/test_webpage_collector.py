import pytest

from backend.collectors.webpage_collector import (
    decode_html,
    extract_html,
)


def test_decode_utf8():
    raw = "<html><body>Привет мир — café</body></html>".encode("utf-8")

    result = decode_html(raw, "text/html; charset=utf-8")

    assert "Привет мир — café" in result


def test_utf8_takes_priority_over_incorrect_http_charset():
    raw = "<html><body>Привет</body></html>".encode("utf-8")

    result = decode_html(raw, "text/html; charset=windows-1252")

    assert "Привет" in result
    assert "Рџ" not in result


def test_decode_declared_legacy_encoding():
    raw = "<html><body>café</body></html>".encode("windows-1252")

    result = decode_html(raw, "text/html; charset=windows-1252")

    assert "café" in result


def test_decode_html_meta_charset():
    raw = (
        '<html><head><meta charset="windows-1252"></head>'
        '<body>café</body></html>'
    ).encode("windows-1252")

    result = decode_html(raw)

    assert "café" in result


def test_decode_utf8_bom():
    raw = b"\xef\xbb\xbf" + "Привет".encode("utf-8")

    result = decode_html(raw)

    assert result == "Привет"


def test_unknown_charset_falls_back_to_windows_1252():
    raw = b"<html><body>caf\xe9</body></html>"

    result = decode_html(raw, "text/html; charset=unknown-encoding")

    assert "café" in result


def test_extract_html_title_and_readable_text():
    html = """
    <html>
      <head><title>Example article</title></head>
      <body>
        <nav>Navigation should be ignored</nav>
        <article>
          <h1>Article heading</h1>
          <p>This is readable article text.</p>
        </article>
        <script>ignored_script()</script>
      </body>
    </html>
    """

    title, text = extract_html(html)

    assert title == "Example article"
    assert "Article heading" in text
    assert "readable article text" in text
    assert "Navigation should be ignored" not in text
    assert "ignored_script" not in text
