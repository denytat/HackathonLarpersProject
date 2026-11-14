"""Derive dashboard statistics from real session/report data only."""

from __future__ import annotations

import json
from typing import Any

import streamlit as st

from services.paths import reports_path


def session_analysis_stats() -> dict[str, Any] | None:
    result = st.session_state.get("analysis_result")
    if not result:
        return None

    swarms = result.get("swarms") or []
    posts = result.get("posts") or []
    accounts: set[str] = set()

    for swarm in swarms:
        for account in swarm.get("accounts") or []:
            accounts.add(str(account))

    # Also count accounts from uploaded dataframe if available
    uploaded_accounts = st.session_state.get("uploaded_accounts")
    if uploaded_accounts:
        accounts.update(str(a) for a in uploaded_accounts)

    flagged = sum(1 for post in posts if post.get("flagged_by"))
    max_score = max(
        (float(swarm.get("score", 0)) for swarm in swarms),
        default=0.0,
    )

    return {
        "posts": len(posts),
        "accounts": len(accounts),
        "swarms": len(swarms),
        "flagged_posts": flagged,
        "max_swarm_score": max_score,
        "source": "current_session",
    }


def benchmark_snapshot() -> dict[str, Any] | None:
    """Load known totals from the baseline detector report (synthetic)."""
    path = reports_path("detector_evaluation_posts.json")
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None

    return {
        "posts": report.get("total_posts", 0),
        "accounts": report.get("total_accounts", 0),
        "swarms": len(report.get("detected_swarms") or []),
        "dataset": report.get("dataset", "posts"),
        "source": "benchmark_report",
        "generated_at": report.get("generated_at"),
    }


def summarize_verdict(result: dict[str, Any] | None) -> dict[str, Any]:
    """Produce a high-level verdict summary from an AnalyzeResponse."""
    if not result:
        return {
            "label": "No analysis yet",
            "css": "sw-verdict-uncertain",
            "detail": "Run an analysis to see coordination findings.",
        }

    swarms = result.get("swarms") or []
    posts = result.get("posts") or []

    if not swarms:
        return {
            "label": "No coordinated groups detected",
            "css": "sw-verdict-clear",
            "detail": (
                "No account clusters met the coordination thresholds "
                "for this dataset."
            ),
        }

    high_score = any(float(s.get("score", 0)) >= 0.75 for s in swarms)
    mid_score = any(float(s.get("score", 0)) >= 0.4 for s in swarms)
    ai_coordinated = any(
        ((s.get("ai_analysis") or {}).get("verdict") or "")
        .lower()
        .find("coordinat")
        >= 0
        for s in swarms
    )

    flagged = sum(1 for p in posts if p.get("flagged_by"))

    if high_score or ai_coordinated:
        return {
            "label": "Coordinated activity signals",
            "css": "sw-verdict-coordinated",
            "detail": (
                f"{len(swarms)} swarm cluster(s) detected. "
                "Coordination does not establish malicious intent."
            ),
        }

    if mid_score or flagged:
        return {
            "label": "Suspicious activity signals",
            "css": "sw-verdict-suspicious",
            "detail": (
                f"{len(swarms)} potential cluster(s) and "
                f"{flagged} flagged post(s). Review evidence carefully."
            ),
        }

    return {
        "label": "Uncertain — review recommended",
        "css": "sw-verdict-uncertain",
        "detail": (
            "Weak or mixed signals. Manual analyst review is recommended."
        ),
    }
