"""Sidebar branding, theme toggle, and navigation."""

from __future__ import annotations

import streamlit as st

from components.styles import get_theme, set_theme
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
    with st.sidebar:
        st.markdown(
            """
            <div class="sw-brand">
                <p class="sw-brand-mark">Swarmwatch</p>
                <div class="sw-brand-sub">Coordination research platform</div>
            </div>
            <div class="sw-nav-label">Sections</div>
            """,
            unsafe_allow_html=True,
        )

        if "pending_nav" in st.session_state:
            pending = st.session_state.pop("pending_nav")
            if pending in NAV_PAGES:
                st.session_state["nav_page"] = pending

        if "nav_page" not in st.session_state:
            st.session_state["nav_page"] = "Overview"

        if "ui_theme" not in st.session_state:
            st.session_state["ui_theme"] = "light"

        page = st.radio(
            "Navigation",
            NAV_PAGES,
            key="nav_page",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="sw-nav-label" style="margin-top:14px;">Appearance</div>',
            unsafe_allow_html=True,
        )
        theme_label = "Dark" if get_theme() == "dark" else "Light"
        cols = st.columns(2)
        with cols[0]:
            if st.button(
                "Light",
                use_container_width=True,
                type="primary" if get_theme() == "light" else "secondary",
                key="theme_light_btn",
            ):
                set_theme("light")
                st.rerun()
        with cols[1]:
            if st.button(
                "Dark",
                use_container_width=True,
                type="primary" if get_theme() == "dark" else "secondary",
                key="theme_dark_btn",
            ):
                set_theme("dark")
                st.rerun()

        stats = session_analysis_stats()
        session_line = "No analysis in this session"
        if stats:
            session_line = (
                f"Session: {stats['posts']} posts · "
                f"{stats['swarms']} cluster(s)"
            )

        health = check_health()
        if health["ok"]:
            status_label = "Backend reachable"
            dot = "ok"
        else:
            status_label = f"Backend unavailable"
            dot = "err"

        st.markdown(
            f"""
            <div class="sw-sidebar-meta">
                <div class="sw-status-line">
                    <span class="sw-status-dot {dot}"></span>
                    {status_label}
                </div>
                <div>{session_line}</div>
                <div style="margin-top:8px;">Theme: {theme_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "Research support tool. Coordination is not proof of malicious intent."
        )

    return page


def go_to(page: str) -> None:
    st.session_state["pending_nav"] = page
    st.rerun()
