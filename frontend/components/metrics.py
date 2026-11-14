"""Shared editorial HTML helpers."""

from __future__ import annotations

import html

import streamlit as st


def safe(value) -> str:
    return html.escape(str(value), quote=True)


def metric_card(label: str, value, note: str = "", source: str = "") -> None:
    source_html = (
        f'<div class="sw-source-tag">{safe(source)}</div>'
        if source
        else ""
    )
    st.markdown(
        f"""
        <div class="sw-stat">
            <div class="sw-stat-label">{safe(label)}</div>
            <div class="sw-stat-value">{safe(value)}</div>
            <div class="sw-stat-note">{safe(note)}</div>
            {source_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str | None = None) -> None:
    st.markdown(
        f'<div class="sw-section">{safe(title)}</div>',
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f'<div class="sw-section-sub">{safe(subtitle)}</div>',
            unsafe_allow_html=True,
        )


def show_badge(text: str, variant: str = "") -> None:
    css = f"sw-badge {variant}".strip()
    st.markdown(
        f'<span class="{css}">{safe(text)}</span>',
        unsafe_allow_html=True,
    )


def hero_banner(
    eyebrow: str,
    title: str,
    description: str,
    status_html: str = "",
) -> None:
    status_markup = f"<div>{status_html}</div>" if status_html else ""
    st.markdown(
        f"""
        <div class="sw-hero">
            <div class="sw-hero-eyebrow">{safe(eyebrow)}</div>
            <h2 class="sw-hero-title">{safe(title)}</h2>
            <p class="sw-hero-desc">{safe(description)}</p>
            {status_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )


def verdict_banner(label: str, css: str, detail: str) -> None:
    st.markdown(
        f"""
        <div class="sw-panel">
            <div class="sw-verdict {css}">{safe(label)}</div>
            <p class="sw-muted" style="margin-top:12px;margin-bottom:0;">{safe(detail)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_pct(value) -> str:
    """Format a ratio as percent, or N/A when missing."""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.1%}"
    except (TypeError, ValueError):
        return "N/A"


def format_num(value) -> str:
    if value is None:
        return "N/A"
    return str(value)
