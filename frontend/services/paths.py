"""Filesystem path helpers that work on Windows and Linux/Docker."""

from __future__ import annotations

from pathlib import Path


FRONTEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = FRONTEND_DIR.parent
STYLES_DIR = FRONTEND_DIR / "styles"
SCRIPTS_DIR = FRONTEND_DIR / "scripts"
REPORTS_DIR = PROJECT_ROOT / "reports"
SAMPLE_POSTS_CSV = PROJECT_ROOT / "data" / "synthetic" / "posts.csv"
CHALLENGE_POSTS_CSV = PROJECT_ROOT / "data" / "synthetic" / "challenge_posts.csv"


def reports_path(filename: str) -> Path:
    return REPORTS_DIR / filename
