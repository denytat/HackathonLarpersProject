"""CSV column detection and post payload building."""

from __future__ import annotations

from typing import Any

import pandas as pd
from dateutil import parser as date_parser


COLUMN_ALIASES = {
    "id": [
        "id", "post_id", "tweet_id", "external_author_id",
        "status_id", "message_id",
    ],
    "account": [
        "account", "author", "username", "user",
        "screen_name", "account_name", "user_id",
    ],
    "text": [
        "text", "content", "message", "post",
        "tweet", "body", "description",
    ],
    "timestamp": [
        "timestamp", "publish_date", "created_at",
        "date", "time", "posted_at",
    ],
}

REQUIRED_FIELDS = ("id", "account", "text", "timestamp")
PLACEHOLDER = "-- Select column --"


def detect_columns(columns) -> dict[str, str]:
    detected: dict[str, str] = {}
    normalized = {
        str(column).strip().lower(): column
        for column in columns
    }

    for field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                detected[field] = normalized[alias]
                break

    return detected


def build_posts_from_dataframe(
    df: pd.DataFrame,
    mapping: dict[str, str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Convert mapped CSV rows into PostInput-compatible dicts.

    Returns (posts, warnings). Invalid rows are reported, not silently dropped
    without notice.
    """
    posts: list[dict[str, Any]] = []
    warnings: list[str] = []

    for index, row in df.iterrows():
        raw_id = row[mapping["id"]]
        account = row[mapping["account"]]
        content = row[mapping["text"]]
        timestamp = row[mapping["timestamp"]]

        missing_fields = []
        if pd.isna(account) or str(account).strip() == "":
            missing_fields.append("account")
        if pd.isna(content) or str(content).strip() == "":
            missing_fields.append("text")
        if pd.isna(timestamp) or str(timestamp).strip() == "":
            missing_fields.append("timestamp")

        if missing_fields:
            warnings.append(
                f"Row {index}: skipped — missing {', '.join(missing_fields)}"
            )
            continue

        ts_text = str(timestamp).strip()
        try:
            date_parser.parse(ts_text)
        except (ValueError, TypeError, OverflowError):
            warnings.append(
                f"Row {index}: skipped — invalid timestamp '{ts_text}'"
            )
            continue

        if pd.isna(raw_id) or str(raw_id).strip() == "":
            post_id = f"post_{index}"
            warnings.append(
                f"Row {index}: missing id — assigned '{post_id}'"
            )
        else:
            post_id = str(raw_id)

        posts.append({
            "id": post_id,
            "account": str(account),
            "text": str(content),
            "timestamp": ts_text,
            "reply_to": None,
            "image_url": None,
        })

    return posts, warnings
