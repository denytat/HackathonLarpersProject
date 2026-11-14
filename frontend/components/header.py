"""Page header helpers."""

from __future__ import annotations

import streamlit as st

from components.metrics import safe


PAGE_META = {
    "Overview": {
        "kicker": "Overview",
        "title": "Coordination research",
        "desc": (
            "Understand how Swarmwatch detects coordinated activity across "
            "groups of social-media accounts."
        ),
    },
    "Analyze": {
        "kicker": "Analyze",
        "title": "Dataset analysis",
        "desc": (
            "Upload a CSV, map columns, validate records, and run the "
            "coordination pipeline."
        ),
    },
    "Results": {
        "kicker": "Results",
        "title": "Investigation report",
        "desc": (
            "Evidence-led findings from the latest analysis in this session."
        ),
    },
    "Benchmarks": {
        "kicker": "Evaluation",
        "title": "Benchmark reports",
        "desc": (
            "Synthetic evaluation metrics for detector and AI layers. "
            "Not real-world accuracy claims."
        ),
    },
    "About": {
        "kicker": "About",
        "title": "About Swarmwatch",
        "desc": (
            "Method, AI roles, evidence standards, and known limitations."
        ),
    },
}


def render_page_header(page: str) -> None:
    meta = PAGE_META.get(
        page,
        {"kicker": page, "title": page, "desc": ""},
    )
    st.markdown(
        f"""
        <div class="sw-page-kicker">{safe(meta['kicker'])}</div>
        <h1 class="sw-page-title">{safe(meta['title'])}</h1>
        <p class="sw-page-desc">{safe(meta['desc'])}</p>
        <hr class="sw-rule" />
        """,
        unsafe_allow_html=True,
    )
