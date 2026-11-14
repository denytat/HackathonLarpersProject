
import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx

from backend.collectors.url_parser import parse_url


MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_REDIRECTS = 5
REQUEST_TIMEOUT = 12.0

USER_AGENT = (
    "Mozilla/5.0 (compatible; Swarmwatch/1.0; "
    "+https://swarmspotter.tech)"
)


class WebpageFetchError(Exception):
    """Raised when a webpage cannot be safely retrieved."""


class ArticleHTMLParser(HTMLParser):
    """Extract readable text and the page title from HTML."""

    BLOCK_TAGS = {
        "p", "div", "br", "article", "section",
        "h1", "h2", "h3", "h4", "li", "blockquote",
    }

    IGNORED_TAGS = {
        "script", "style", "noscript", "svg",
        "iframe", "nav", "footer", "header",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = []
        self.text = []
        self.ignored_depth = 0
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()

        if tag in self.IGNORED_TAGS:
            self.ignored_depth += 1
            return

        if self.ignored_depth:
            return

        if tag == "title":
            self.in_title = True

        if tag in self.BLOCK_TAGS:
            self.text.append("\n")

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag in self.IGNORED_TAGS:
            if self.ignored_depth:
                self.ignored_depth -= 1
            return

        if self.ignored_depth:
            return

        if tag == "title":
            self.in_title = False

        if tag in self.BLOCK_TAGS:
            self.text.append("\n")

    def handle_data(self, data):
        if self.ignored_depth:
            return

        if self.in_title:
            self.title.append(data)

        self.text.append(data)


def validate_public_host(host: str):
    """
    Reject hostnames resolving to private or non-public IP addresses.

    DNS is checked before each request, including redirects.
    """

    try:
        addresses = socket.getaddrinfo(
            host,
            443,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror:
        raise WebpageFetchError("Could not resolve the website hostname.")

    if not addresses:
        raise WebpageFetchError("The website hostname has no IP addresses.")

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])

        if not ip.is_global:
            raise WebpageFetchError(
                "The website resolves to a private or restricted IP address."
            )


def extract_html(html: str) -> tuple[str, str]:
    parser = ArticleHTMLParser()

    try:
        parser.feed(html)
        parser.close()
    except Exception:
        raise WebpageFetchError("Could not parse the webpage HTML.")

    title = " ".join(" ".join(parser.title).split())
    text = "\n".join(
        line.strip()
        for line in "".join(parser.text).splitlines()
        if line.strip()
    )

    return title, text


def collect_webpage(url: str) -> dict:
    """
    Retrieve readable text from a public HTTPS webpage.

    This function does not scrape social-media platforms.
    """

    try:
        parsed = parse_url(url)
    except ValueError as error:
        raise WebpageFetchError(str(error))

    if parsed.platform != "web":
        raise WebpageFetchError(
            "This is a social-media URL. Public webpage extraction "
            "is not supported for this platform."
        )

    current_url = parsed.original_url

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
    }

    try:
        with httpx.Client(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=False,
            trust_env=False,
        ) as client:

            for redirect_count in range(MAX_REDIRECTS + 1):
                current = urlparse(current_url)
                host = current.hostname

                if not host:
                    raise WebpageFetchError("Invalid redirect destination.")

                validate_public_host(host)

                with client.stream(
                    "GET",
                    current_url,
                    headers=headers,
                ) as response:

                    if response.status_code in (301, 302, 303, 307, 308):
                        location = response.headers.get("location")

                        if not location:
                            raise WebpageFetchError(
                                "The website returned an invalid redirect."
                            )

                        if redirect_count >= MAX_REDIRECTS:
                            raise WebpageFetchError(
                                "Too many redirects."
                            )

                        current_url = urljoin(current_url, location)

                        redirect_url = urlparse(current_url)

                        if redirect_url.scheme.lower() != "https":
                            raise WebpageFetchError(
                                "Redirects to non-HTTPS URLs are not allowed."
                            )

                        continue

                    response.raise_for_status()

                    content_type = response.headers.get(
                        "content-type", ""
                    ).lower()

                    if (
                        "text/html" not in content_type
                        and "application/xhtml+xml" not in content_type
                    ):
                        raise WebpageFetchError(
                            "The URL does not return an HTML webpage."
                        )

                    content_length = response.headers.get("content-length")

                    if content_length:
                        try:
                            if int(content_length) > MAX_RESPONSE_BYTES:
                                raise WebpageFetchError(
                                    "The webpage is too large to process."
                                )
                        except ValueError:
                            raise WebpageFetchError(
                                "Invalid response content length."
                            )

                    chunks = []
                    total_bytes = 0

                    for chunk in response.iter_bytes():
                        total_bytes += len(chunk)

                        if total_bytes > MAX_RESPONSE_BYTES:
                            raise WebpageFetchError(
                                "The webpage exceeds the download size limit."
                            )

                        chunks.append(chunk)

                    raw_content = b"".join(chunks)

                    html = decode_html(raw_content, content_type)

                    title, text = extract_html(html)

                    if len(text) < 100:
                        raise WebpageFetchError(
                            "The webpage contains too little readable text."
                        )

                    return {
                        "url": current_url,
                        "platform": "web",
                        "content_type": parsed.content_type,
                        "domain": parsed.domain,
                        "title": title,
                        "text": text,
                        "status": "collected",
                        "character_count": len(text),
                    }

            raise WebpageFetchError("Could not retrieve the webpage.")

    except WebpageFetchError:
        raise

    except httpx.TimeoutException:
        raise WebpageFetchError("The website request timed out.")

    except httpx.HTTPStatusError as error:
        raise WebpageFetchError(
            f"The website returned HTTP status {error.response.status_code}."
        )

    except httpx.RequestError:
        raise WebpageFetchError(
            "Could not connect to the website."
        )


def decode_html(raw_content: bytes, content_type: str = "") -> str:
    """Decode HTML while handling incorrect or missing charset declarations."""

    # Check BOMs first. UTF-32 must be checked before UTF-16.
    bom_encodings = (
        (b"\x00\x00\xfe\xff", "utf-32"),
        (b"\xff\xfe\x00\x00", "utf-32"),
        (b"\xef\xbb\xbf", "utf-8-sig"),
        (b"\xfe\xff", "utf-16"),
        (b"\xff\xfe", "utf-16"),
    )

    for bom, encoding in bom_encodings:
        if raw_content.startswith(bom):
            return raw_content.decode(encoding, errors="replace")

    # UTF-8 is preferred because some websites declare the wrong charset.
    try:
        return raw_content.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        pass

    # Look for a charset declared in the HTTP Content-Type header.
    match = re.search(
        r"charset\s*=\s*[\"']?\s*([a-zA-Z0-9._:-]+)",
        content_type,
        re.IGNORECASE,
    )
    declared_encoding = match.group(1) if match else None

    # If there is no HTTP charset, inspect HTML metadata.
    if not declared_encoding:
        head = raw_content[:4096]

        match = re.search(
            br"<meta\b[^>]*charset\s*=\s*[\"']?\s*([a-zA-Z0-9._:-]+)",
            head,
            re.IGNORECASE,
        )

        if match:
            declared_encoding = match.group(1).decode("ascii")

    # Try the declared encoding.
    if declared_encoding:
        try:
            return raw_content.decode(
                declared_encoding,
                errors="strict",
            )
        except (LookupError, UnicodeDecodeError):
            pass

    # Last-resort fallback for older HTML pages.
    return raw_content.decode("windows-1252", errors="replace")
