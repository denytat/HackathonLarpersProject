"""Backend API client for Swarmwatch."""

from __future__ import annotations

import os
from typing import Any

import requests


def get_api_base() -> str:
    """Resolve API base URL from environment (Docker-compatible)."""
    return os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")


def get_analyze_url() -> str:
    base = get_api_base()
    if base.endswith("/analyze"):
        return base
    return f"{base}/analyze"


def get_health_url() -> str:
    base = get_api_base()
    if base.endswith("/analyze"):
        base = base[: -len("/analyze")]
    return f"{base.rstrip('/')}/health"


def check_health(timeout: float = 1.5) -> dict[str, Any]:
    """Probe the FastAPI /health endpoint."""
    try:
        response = requests.get(get_health_url(), timeout=timeout)
        if response.status_code == 200:
            payload = response.json() if response.content else {}
            return {
                "ok": True,
                "status": payload.get("status", "ok"),
                "detail": "Backend reachable",
            }
        return {
            "ok": False,
            "status": "error",
            "detail": f"HTTP {response.status_code}",
        }
    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "status": "unreachable",
            "detail": "Cannot connect to FastAPI backend",
        }
    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "status": "timeout",
            "detail": "Health check timed out",
        }
    except requests.exceptions.RequestException as error:
        return {
            "ok": False,
            "status": "error",
            "detail": str(error),
        }


def analyze_posts(
    posts: list[dict[str, Any]],
    timeout: float = 120.0,
) -> dict[str, Any]:
    """
    POST /analyze with PostInput-compatible payloads.

    Returns:
        {"ok": True, "data": AnalyzeResponse-like dict}
        or {"ok": False, "error": str, "status_code": optional int, "body": optional str}
    """
    try:
        response = requests.post(
            get_analyze_url(),
            json={"posts": posts},
            timeout=timeout,
        )

        if response.status_code == 200:
            return {"ok": True, "data": response.json()}

        return {
            "ok": False,
            "error": f"Backend error: HTTP {response.status_code}",
            "status_code": response.status_code,
            "body": response.text,
        }

    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "error": (
                "Cannot connect to FastAPI. "
                "Check that the backend is running and API_URL is correct."
            ),
        }
    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "error": "Analysis timed out. Try a smaller dataset.",
        }
    except requests.exceptions.RequestException as error:
        return {
            "ok": False,
            "error": f"Request failed: {error}",
        }
