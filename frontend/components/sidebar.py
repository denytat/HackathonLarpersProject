
"""
SWARMWATCH sidebar branding and navigation.
Dark mode only — no theme switching.
"""

from __future__ import annotations

from html import escape

import streamlit as st

from services.api import check_health
from services.stats import session_analysis_stats


NAV_PAGES = [
    "Overview",
    "Analyze",
    "Results",
    "Benchmarks",
    "About",
]


def render_sidebar() -> str:
    """Render sidebar and return the selected page."""

    with st.sidebar:
        # Branding
        st.markdown(
            """
            <div class="sw-brand">
                <p class="sw-brand-mark">Swarmwatch</p>
                <div class="sw-brand-sub">
                    Coordination research platform
                </div>
            </div>

            <div class="sw-nav-label">Sections</div>
            """,
            unsafe_allow_html=True,
        )

        # Handle navigation from other pages
        if "pending_nav" in st.session_state:
            pending = st.session_state.pop("pending_nav")

            if pending in NAV_PAGES:
                st.session_state["nav_page"] = pending

        # Default page
        if "nav_page" not in st.session_state:
            st.session_state["nav_page"] = "Overview"

        # Navigation
        page = st.radio(
            "Navigation",
            NAV_PAGES,
            key="nav_page",
            label_visibility="collapsed",
        )

        # Session statistics
        stats = session_analysis_stats()

        session_line = "No analysis in this session"

        if stats:
            session_line = (
                f"Session: {stats['posts']} posts · "
                f"{stats['swarms']} cluster(s)"
            )

        # Backend status
        health = check_health()

        if health["ok"]:
            status_label = "Backend reachable"
            dot = "ok"
        else:
            status_label = "Backend unavailable"
            dot = "err"

        # Compact status panel
        st.markdown(
            f"""
            <div class="sw-sidebar-meta">
                <div class="sw-status-line">
                    <span class="sw-status-dot {dot}"></span>
                    {escape(status_label)}
                </div>
                <div>{escape(session_line)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "Coordination is not proof of malicious intent."
        )

    return page


def go_to(page: str) -> None:
    """Navigate to a page."""
    if page in NAV_PAGES:
        st.session_state["pending_nav"] = page
        st.rerun()
