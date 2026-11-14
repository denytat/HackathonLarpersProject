"""
Swarmwatch Streamlit frontend.

Entry point used by Docker:
  streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure `frontend/` is importable whether launched from repo root or /app.
_FRONTEND_DIR = Path(__file__).resolve().parent
if str(_FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(_FRONTEND_DIR))

import streamlit as st

from components.header import render_page_header
from components.sidebar import render_sidebar
from components.styles import inject_styles
from views import about, analyze, benchmarks, overview, results


st.set_page_config(
    page_title="Swarmwatch | Coordination Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

page = render_sidebar()
render_page_header(page)

if page == "Overview":
    overview.render()
elif page == "Analyze":
    analyze.render()
elif page == "Results":
    results.render()
elif page == "Benchmarks":
    benchmarks.render()
elif page == "About":
    about.render()

st.markdown(
    """
    <div class="sw-footer">
        SWARMWATCH · Coordination Intelligence Platform<br>
        AI-assisted assessments are not proof of malicious intent.
    </div>
    """,
    unsafe_allow_html=True,
)
