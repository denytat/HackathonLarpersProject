
from dataclasses import dataclass
import ipaddress
import re
from urllib.parse import urlparse, urlunparse


@dataclass(frozen=True)
class ParsedPostUrl:
    platform: str
    post_id: str
    original_url: str


@dataclass(frozen=True)
class ParsedUrl:
    platform: str
    content_type: str
    original_url: str
    post_id: str | None = None
    domain: str | None = None


SOCIAL_HOSTS = {
    "reddit.com",
    "www.reddit.com",
    "old.reddit.com",
    "redd.it",
    "x.com",
    "www.x.com",
    "twitter.com",
    "www.twitter.com",
    "instagram.com",
    "www.instagram.com",
}

REDDIT_HOSTS = {
    "reddit.com", "www.reddit.com", "old.reddit.com"
}
X_HOSTS = {
    "x.com", "www.x.com", "twitter.com", "www.twitter.com"
}
INSTAGRAM_HOSTS = {
    "instagram.com", "www.instagram.com"
}

ARTICLE_PATH_HINTS = (
    "/news/",
    "/article/",
    "/articles/",
    "/story/",
    "/stories/",
    "/blog/",
    "/opinion/",
    "/politics/",
)


def _validate_url(value: str):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("URL cannot be empty.")

    value = value.strip()

    if len(value) > 2048:
        raise ValueError("URL is too long.")

    try:
        parsed = urlparse(value)

        if parsed.scheme.lower() != "https":
            raise ValueError("Only HTTPS URLs are supported.")

        if not parsed.hostname:
            raise ValueError("URL must contain a valid hostname.")

        if parsed.username is not None or parsed.password is not None:
            raise ValueError("URLs containing credentials are not supported.")

        if parsed.port not in (None, 443):
            raise ValueError("Custom URL ports are not supported.")

        host = parsed.hostname.lower().rstrip(".")

        if not host or host == "localhost" or host.endswith(".localhost"):
            raise ValueError("Local addresses are not supported.")

        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            ip = None

        if ip is not None and not ip.is_global:
            raise ValueError("Private or local IP addresses are not supported.")

        if not re.fullmatch(
            r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*",
            host,
        ):
            raise ValueError("Invalid hostname.")

        return value, parsed, host

    except ValueError:
        raise
    except Exception:
        raise ValueError("Invalid URL.")


def _canonical_post_url(value: str, parsed) -> str:
    """Remove fragments and query parameters for stable duplicate detection."""
    return urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip("/") or "/",
        "",
        "",
        "",
    ))


def parse_post_url(value: str) -> ParsedPostUrl:
    """
    Recognize supported social-media post URLs.
    Does not access external platforms or retrieve content.
    """
    value, parsed, host = _validate_url(value)
    path = parsed.path

    if host in REDDIT_HOSTS:
        match = re.search(
            r"/comments/([a-z0-9]+)/?",
            path,
            re.IGNORECASE,
        )

        if not match:
            raise ValueError("Could not identify a Reddit post ID.")

        return ParsedPostUrl("reddit", match.group(1), value)

    if host == "redd.it":
        match = re.fullmatch(
            r"/([a-z0-9]+)/?",
            path,
            re.IGNORECASE,
        )

        if not match:
            raise ValueError("Invalid Reddit short URL.")

        return ParsedPostUrl("reddit", match.group(1), value)

    if host in X_HOSTS:
        match = re.fullmatch(
            r"/[^/]+/status/([0-9]+)/?",
            path,
            re.IGNORECASE,
        )

        if not match:
            raise ValueError("Could not identify an X post ID.")

        return ParsedPostUrl("x", match.group(1), value)

    if host in INSTAGRAM_HOSTS:
        match = re.fullmatch(
            r"/(?:p|reel|tv)/([A-Za-z0-9_-]+)/?",
            path,
            re.IGNORECASE,
        )

        if not match:
            raise ValueError("Could not identify an Instagram post ID.")

        return ParsedPostUrl("instagram", match.group(1), value)

    raise ValueError("This URL is not a recognized social-media post.")


def parse_url(value: str) -> ParsedUrl:
    """
    Universal URL recognition.

    Recognizes supported social-media posts and ordinary HTTPS webpages.
    Does not retrieve content.
    """
    value, parsed, host = _validate_url(value)

    if host in SOCIAL_HOSTS:
        post = parse_post_url(value)

        return ParsedUrl(
            platform=post.platform,
            content_type="social_post",
            original_url=value,
            post_id=post.post_id,
            domain=host,
        )

    path = parsed.path.lower()

    if any(hint in path for hint in ARTICLE_PATH_HINTS):
        content_type = "article"
    else:
        content_type = "webpage"

    return ParsedUrl(
        platform="web",
        content_type=content_type,
        original_url=value,
        domain=host,
    )


def parse_post_urls(values: list[str]) -> tuple[list[ParsedPostUrl], list[dict]]:
    """
    Parse multiple social-media URLs independently.
    Invalid and duplicate post URLs are returned as errors.
    """
    parsed_urls = []
    errors = []
    seen = set()

    for index, value in enumerate(values):
        try:
            parsed = parse_post_url(value)
            _, validated, _ = _validate_url(value)

            key = (
                parsed.platform,
                parsed.post_id,
            )

            if key in seen:
                errors.append({
                    "index": index,
                    "url": value,
                    "error": "Duplicate post URL.",
                })
                continue

            seen.add(key)
            parsed_urls.append(parsed)

        except ValueError as error:
            errors.append({
                "index": index,
                "url": value,
                "error": str(error),
            })

    return parsed_urls, errors
