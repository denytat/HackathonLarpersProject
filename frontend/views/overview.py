
"""
SWARMWATCH — Overview dashboard.

Compact dark-glass layout with session-aware metrics.
"""

from __future__ import annotations

from html import escape

import streamlit as st

from components.sidebar import go_to
from services.stats import session_analysis_stats


def _metric_card(label: str, value: str, detail: str = "") -> None:
    """Render a compact metric card."""
    st.markdown(
        f"""
        <div class="sw-overview-metric">
            <div class="sw-overview-metric-label">
                {escape(label)}
            </div>
            <div class="sw-overview-metric-value">
                {escape(str(value))}
            </div>
            <div class="sw-overview-metric-detail">
                {escape(detail)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _pipeline_stage(number: str, title: str, description: str) -> None:
    """Render one pipeline stage."""
    st.markdown(
        f"""
        <div class="sw-overview-stage">
            <span class="sw-overview-stage-number">
                {escape(number)}
            </span>
            <div class="sw-overview-stage-title">
                {escape(title)}
            </div>
            <div class="sw-overview-stage-detail">
                {escape(description)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render() -> None:
    """Render the overview page."""

    st.markdown(
        """
        <div class="sw-overview-heading">
            <div>
                <h1>Overview</h1>
                <p>Coordination intelligence workspace</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Use actual session statistics only.
    stats = session_analysis_stats()

    if stats:
        posts = stats.get("posts", "—")
        accounts = stats.get("accounts", "—")
        clusters = stats.get("swarms", "—")
        status = "Available"
        source = "Current session"
    else:
        posts = "—"
        accounts = "—"
        clusters = "—"
        status = "Not started"
        source = "No analysis loaded"

    st.markdown(
        f"""
        <div class="sw-overview-source">
            <span class="sw-overview-source-dot"></span>
            {escape(source)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Compact metrics
    col1, col2, col3, col4 = st.columns(4, gap="small")

    with col1:
        _metric_card("Posts", str(posts), "Analyzed posts")

    with col2:
        _metric_card("Accounts", str(accounts), "Unique accounts")

    with col3:
        _metric_card("Clusters", str(clusters), "Candidate groups")

    with col4:
        _metric_card("Analysis", status, "Session status")

    st.markdown(
        '<div class="sw-overview-section-title">'
        'Detection pipeline'
        '</div>',
        unsafe_allow_html=True,
    )

    # Pipeline
    p1, p2, p3, p4 = st.columns(4, gap="small")

    with p1:
        _pipeline_stage(
            "01",
            "Detect",
            "Timing, text and account signals",
        )

    with p2:
        _pipeline_stage(
            "02",
            "Classify",
            "Post-level technique analysis",
        )

    with p3:
        _pipeline_stage(
            "03",
            "Interpret",
            "Cluster narrative assessment",
        )

    with p4:
        _pipeline_stage(
            "04",
            "Review",
            "Evidence and uncertainty",
        )

    st.markdown(
        '<div class="sw-overview-section-title">'
        'Investigation'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        left, right = st.columns([3, 1], vertical_alignment="center")

        with left:
            st.markdown("**Ready to investigate**")
            st.caption(
                "Upload a CSV to analyze coordination patterns "
                "and inspect supporting evidence."
            )

        with right:
            if st.button(
                "Analyze dataset",
                type="primary",
                width="stretch",
                key="overview_analyze",
            ):
                go_to("Analyze")

    st.caption(
        "Coordination signals are not proof of malicious intent."
    )
