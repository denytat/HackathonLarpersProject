
"""
SWARMWATCH — Dark Mode Styles.
Loads existing CSS files and enforces dark mode.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st


FRONTEND_DIR = Path(__file__).resolve().parent.parent
STYLES_DIR = FRONTEND_DIR / "styles"


DARK_VARS = {
    "--sw-bg": "#0b1018",
    "--sw-bg-sidebar": "#121a26",
    "--sw-surface": "#172131",
    "--sw-surface-elevated": "#1d293b",
    "--sw-border": "#2c3a50",
    "--sw-border-strong": "#40516b",
    "--sw-text": "#e8eef7",
    "--sw-text-secondary": "#b5c3d5",
    "--sw-text-muted": "#8fa1b8",
    "--sw-accent": "#7ea8f8",
    "--sw-accent-soft": "rgba(126, 168, 248, 0.14)",
    "--sw-accent-burgundy": "#d68d99",
    "--sw-accent-burgundy-soft": "rgba(214, 141, 153, 0.14)",
    "--sw-ok": "#7eb6a4",
    "--sw-ok-soft": "rgba(126, 182, 164, 0.14)",
    "--sw-warn": "#d2b36a",
    "--sw-warn-soft": "rgba(210, 179, 106, 0.14)",
    "--sw-danger": "#d08989",
    "--sw-danger-soft": "rgba(208, 137, 137, 0.14)",
    "--sw-shadow": "0 4px 18px rgba(0, 0, 0, 0.25)",
}


def inject_styles() -> None:
    """Load existing CSS and enforce dark mode."""

    variables = "\n".join(
        f"    {name}: {value};"
        for name, value in DARK_VARS.items()
    )

    css_parts = []

    # Load existing stylesheets.
    for filename in ("tokens.css", "editorial.css", "styles.css"):
        css_file = STYLES_DIR / filename

        if css_file.is_file():
            css_parts.append(
                css_file.read_text(encoding="utf-8")
            )

    # Apply dark theme after the existing CSS.
    css_parts.append(
        f"""
        :root,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"] {{
            {variables}
            color-scheme: dark;
        }}

        .stApp,
        [data-testid="stAppViewContainer"] {{
            background-color: var(--sw-bg) !important;
            color: var(--sw-text) !important;
        }}

        [data-testid="stHeader"] {{
            background-color: var(--sw-bg) !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: var(--sw-bg-sidebar) !important;
            border-right: 1px solid var(--sw-border);
        }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: var(--sw-surface);
            border-color: var(--sw-border);
        }}

        .sw-footer {{
            color: var(--sw-text-muted);
            border-top: 1px solid var(--sw-border);
        }}
        """
    )

    st.markdown(
        "<style>\n" + "\n".join(css_parts) + "\n</style>",
        unsafe_allow_html=True,
    )
