from __future__ import annotations
from components.styles import inject_styles
inject_styles()




import sys
from pathlib import Path

# Make frontend modules importable from any working directory.
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

# Apply SWARMWATCH styling.
inject_styles()

# Sidebar navigation.
page = render_sidebar()

# Page header.
render_page_header(page)

# Render the selected page.
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

else:
    st.error(f"Unknown page: {page}")

# Footer.
st.markdown(
    """
    <div class="sw-footer">
        SWARMWATCH · Coordination Intelligence Platform
        <div>
            AI-assisted assessments are not proof of malicious intent.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
