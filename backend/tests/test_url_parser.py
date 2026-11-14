import pytest

from backend.collectors.url_parser import (
    parse_post_url,
    parse_post_urls,
)


@pytest.mark.parametrize(
    "url,platform,post_id",
    [
        (
            "https://www.reddit.com/r/test/comments/abc123/example/",
            "reddit",
            "abc123",
        ),
        (
            "https://redd.it/abc123",
            "reddit",
            "abc123",
        ),
        (
            "https://x.com/example/status/1234567890123456789",
            "x",
            "1234567890123456789",
        ),
        (
            "https://twitter.com/example/status/1234567890123456789",
            "x",
            "1234567890123456789",
        ),
        (
            "https://www.instagram.com/p/ABC_def123/",
            "instagram",
            "ABC_def123",
        ),
        (
            "https://www.instagram.com/reel/ABC_def123/",
            "instagram",
            "ABC_def123",
        ),
    ],
)
def test_parse_supported_urls(url, platform, post_id):
    result = parse_post_url(url)

    assert result.platform == platform
    assert result.post_id == post_id


@pytest.mark.parametrize(
    "url",
    [
        "",
        "not-a-url",
        "http://www.reddit.com/r/test/comments/abc123/",
        "https://example.com/post/123",
        "https://www.instagram.com/accounts/login/",
        "https://x.com/example",
        "https://user:password@x.com/example/status/1234567890",
    ],
)
def test_reject_invalid_urls(url):
    with pytest.raises(ValueError):
        parse_post_url(url)


def test_parse_multiple_urls_and_duplicates():
    urls = [
        "https://redd.it/abc123",
        "https://x.com/example/status/1234567890123456789",
        "https://redd.it/abc123",
        "invalid",
    ]

    parsed, errors = parse_post_urls(urls)

    assert len(parsed) == 2
    assert len(errors) == 2
    assert errors[0]["error"] == "Duplicate post URL."


def test_reject_unsupported_subdomains():
    with pytest.raises(ValueError):
        parse_post_url("https://reddit.com.evil.example/r/test/comments/abc123/")

from backend.collectors.url_parser import parse_url


@pytest.mark.parametrize(
    "url,platform,post_id",
    [
        (
            "https://www.instagram.com/tv/ABC_def123/",
            "instagram",
            "ABC_def123",
        ),
        (
            "https://x.com/example/status/1234567890?ref=share",
            "x",
            "1234567890",
        ),
        (
            "https://www.reddit.com/r/test/comments/abc123/example/?utm_source=test",
            "reddit",
            "abc123",
        ),
    ],
)
def test_parse_additional_social_url_variants(url, platform, post_id):
    result = parse_post_url(url)

    assert result.platform == platform
    assert result.post_id == post_id


def test_parse_article_url():
    result = parse_url("https://example.com/news/example-story")

    assert result.platform == "web"
    assert result.content_type == "article"
    assert result.domain == "example.com"


def test_parse_regular_webpage():
    result = parse_url("https://www.iana.org/domains/reserved")

    assert result.platform == "web"
    assert result.content_type == "webpage"


def test_parse_url_recognizes_social_post():
    result = parse_url(
        "https://x.com/example/status/1234567890"
    )

    assert result.platform == "x"
    assert result.content_type == "social_post"
    assert result.post_id == "1234567890"


@pytest.mark.parametrize(
    "url",
    [
        "https://reddit.com.evil.example/r/test/comments/abc123/",
        "https://instagram.com.evil.example/p/ABC123/",
        "https://x.com:8443/example/status/1234567890",
        "https://127.0.0.1/example",
        "https://localhost/example",
    ],
)
def test_reject_unsafe_or_deceptive_social_urls(url):
    with pytest.raises(ValueError):
        parse_post_url(url)


def test_duplicate_post_with_tracking_parameters():
    urls = [
        "https://x.com/example/status/1234567890",
        "https://x.com/example/status/1234567890?utm_source=share",
    ]

    parsed, errors = parse_post_urls(urls)

    assert len(parsed) == 1
    assert len(errors) == 1
    assert errors[0]["error"] == "Duplicate post URL."

from backend.collectors.url_parser import parse_url


@pytest.mark.parametrize(
    "url,platform,post_id",
    [
        (
            "https://www.instagram.com/tv/ABC_def123/",
            "instagram",
            "ABC_def123",
        ),
        (
            "https://x.com/example/status/1234567890?ref=share",
            "x",
            "1234567890",
        ),
        (
            "https://www.reddit.com/r/test/comments/abc123/example/?utm_source=test",
            "reddit",
            "abc123",
        ),
    ],
)
def test_parse_additional_social_url_variants(url, platform, post_id):
    result = parse_post_url(url)

    assert result.platform == platform
    assert result.post_id == post_id


def test_parse_article_url():
    result = parse_url("https://example.com/news/example-story")

    assert result.platform == "web"
    assert result.content_type == "article"
    assert result.domain == "example.com"


def test_parse_regular_webpage():
    result = parse_url("https://www.iana.org/domains/reserved")

    assert result.platform == "web"
    assert result.content_type == "webpage"


def test_parse_url_recognizes_social_post():
    result = parse_url(
        "https://x.com/example/status/1234567890"
    )

    assert result.platform == "x"
    assert result.content_type == "social_post"
    assert result.post_id == "1234567890"


@pytest.mark.parametrize(
    "url",
    [
        "https://reddit.com.evil.example/r/test/comments/abc123/",
        "https://instagram.com.evil.example/p/ABC123/",
        "https://x.com:8443/example/status/1234567890",
        "https://127.0.0.1/example",
        "https://localhost/example",
    ],
)
def test_reject_unsafe_or_deceptive_social_urls(url):
    with pytest.raises(ValueError):
        parse_post_url(url)


def test_duplicate_post_with_tracking_parameters():
    urls = [
        "https://x.com/example/status/1234567890",
        "https://x.com/example/status/1234567890?utm_source=share",
    ]

    parsed, errors = parse_post_urls(urls)

    assert len(parsed) == 1
    assert len(errors) == 1
    assert errors[0]["error"] == "Duplicate post URL."
