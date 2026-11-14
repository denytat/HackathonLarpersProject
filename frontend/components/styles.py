"""Load and inject Swarmwatch editorial CSS into Streamlit."""

from __future__ import annotations

import streamlit as st

from services.paths import STYLES_DIR


_CSS_FILES = (
    "tokens.css",
    "editorial.css",
)

# Explicit variable maps so theme switching does not depend on JS class injection.
_LIGHT_VARS = {
    "--sw-bg": "#f3eee6",
    "--sw-bg-sidebar": "#ebe4d8",
    "--sw-surface": "#fbfaf7",
    "--sw-surface-elevated": "#ffffff",
    "--sw-border": "#ddd6cb",
    "--sw-border-strong": "#c9c0b2",
    "--sw-text": "#1f1c19",
    "--sw-text-secondary": "#5c564f",
    "--sw-text-muted": "#7a736a",
    "--sw-accent": "#3d4f5f",
    "--sw-accent-soft": "rgba(61, 79, 95, 0.1)",
    "--sw-accent-burgundy": "#6b3a3a",
    "--sw-accent-burgundy-soft": "rgba(107, 58, 58, 0.1)",
    "--sw-ok": "#2f5d50",
    "--sw-ok-soft": "rgba(47, 93, 80, 0.12)",
    "--sw-warn": "#8a6a2f",
    "--sw-warn-soft": "rgba(138, 106, 47, 0.12)",
    "--sw-danger": "#8b3a3a",
    "--sw-danger-soft": "rgba(139, 58, 58, 0.12)",
    "--sw-shadow": "0 1px 2px rgba(31, 28, 25, 0.04)",
}

_DARK_VARS = {
    "--sw-bg": "#1a1917",
    "--sw-bg-sidebar": "#141312",
    "--sw-surface": "#242220",
    "--sw-surface-elevated": "#2c2a27",
    "--sw-border": "#3a3733",
    "--sw-border-strong": "#4d4943",
    "--sw-text": "#f2ede6",
    "--sw-text-secondary": "#b0a99f",
    "--sw-text-muted": "#8a837a",
    "--sw-accent": "#8fa3b5",
    "--sw-accent-soft": "rgba(143, 163, 181, 0.14)",
    "--sw-accent-burgundy": "#c4877a",
    "--sw-accent-burgundy-soft": "rgba(196, 135, 122, 0.14)",
    "--sw-ok": "#7eb6a4",
    "--sw-ok-soft": "rgba(126, 182, 164, 0.14)",
    "--sw-warn": "#d2b36a",
    "--sw-warn-soft": "rgba(210, 179, 106, 0.14)",
    "--sw-danger": "#d08989",
    "--sw-danger-soft": "rgba(208, 137, 137, 0.14)",
    "--sw-shadow": "0 1px 2px rgba(0, 0, 0, 0.25)",
}


def get_theme() -> str:
    theme = st.session_state.get("ui_theme", "light")
    return theme if theme in ("light", "dark") else "light"


def set_theme(theme: str) -> None:
    if theme in ("light", "dark"):
        st.session_state["ui_theme"] = theme


def _vars_block(theme: str) -> str:
    mapping = _DARK_VARS if theme == "dark" else _LIGHT_VARS
    body = "\n".join(f"  {key}: {value};" for key, value in mapping.items())
    return f"""
.stApp, :root, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {{
{body}
}}
.stApp {{
  background-color: var(--sw-bg) !important;
  color: var(--sw-text) !important;
}}
"""


def inject_styles() -> None:
    theme = get_theme()
    chunks: list[str] = [_vars_block(theme)]

    for name in _CSS_FILES:
        path = STYLES_DIR / name
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))

    # Mark theme for components that read a class (e.g. primary button text)
    theme_mark = (
        ".stApp { /* theme: dark */ }\n"
        if theme == "dark"
        else ".stApp { /* theme: light */ }\n"
    )
    if theme == "dark":
        theme_mark += ".stApp { color-scheme: dark; }\n"
        theme_mark += (
            "div.stButton > button[kind=\"primary\"] { color: #1a1917 !important; }\n"
        )
    else:
        theme_mark += ".stApp { color-scheme: light; }\n"

    st.markdown(
        f"<style>\n{theme_mark}{''.join(chunks)}\n</style>",
        unsafe_allow_html=True,
    )
