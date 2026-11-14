"""CSV upload, mapping, validation, and analysis trigger."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from components.metrics import metric_card, section_title
from components.sidebar import go_to
from services.api import analyze_posts
from services.columns import (
    PLACEHOLDER,
    REQUIRED_FIELDS,
    build_posts_from_dataframe,
    detect_columns,
)
from services.paths import SAMPLE_POSTS_CSV


def _store_dataframe(df: pd.DataFrame, source_name: str) -> None:
    st.session_state["uploaded_df"] = df
    st.session_state["upload_source"] = source_name
    st.session_state["uploaded_accounts"] = (
        df[detect_columns(df.columns).get("account")].dropna().astype(str).unique().tolist()
        if detect_columns(df.columns).get("account") in df.columns
        else []
    )
    # Clear stale results when dataset changes
    signature = (source_name, len(df), tuple(df.columns.astype(str)))
    if st.session_state.get("file_signature") != signature:
        st.session_state["file_signature"] = signature
        st.session_state.pop("analysis_result", None)
        st.session_state.pop("analysis_mapping", None)
        st.session_state.pop("analysis_warnings", None)


def render() -> None:
    section_title(
        "Dataset Upload",
        "Import a CSV of social media posts. Required fields: id, account, text, timestamp.",
    )

    st.markdown(
        """
        <div class="sw-dropzone-visual">
            <div style="font-size:14px;font-weight:600;color:#F1F5F9;margin-bottom:6px;">
                Drop a CSV into the uploader below
            </div>
            <div class="sw-muted">
                Column names are auto-detected when possible. Invalid rows are reported,
                not silently discarded.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        uploaded_file = st.file_uploader(
            "Choose a CSV dataset",
            type=["csv"],
            key="csv_uploader",
        )
    with c2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        load_sample = st.button(
            "Load sample dataset",
            use_container_width=True,
            help="Loads data/synthetic/posts.csv when available",
        )

    if load_sample:
        if SAMPLE_POSTS_CSV.exists():
            df = pd.read_csv(SAMPLE_POSTS_CSV, dtype=str)
            _store_dataframe(df, SAMPLE_POSTS_CSV.name)
            st.success(f"Loaded sample dataset: {SAMPLE_POSTS_CSV.name}")
        else:
            st.error(
                f"Sample dataset not found at {SAMPLE_POSTS_CSV}. "
                "Ensure data/synthetic is available in this environment."
            )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, dtype=str)
            if df.empty:
                st.error("The uploaded CSV is empty.")
                return
            _store_dataframe(df, uploaded_file.name)
            st.success(f"Dataset uploaded: {uploaded_file.name}")
        except Exception as error:
            st.error(f"Could not read CSV: {error}")
            return

    # Coming soon: URL analysis
    st.markdown(
        """
        <div class="sw-coming-soon">
            <span class="sw-coming-soon-tag">Coming Soon</span>
            <div style="font-weight:600;color:#F1F5F9;margin-bottom:4px;">
                URL-based swarm analysis
            </div>
            <p class="sw-muted" style="margin:0;">
                Paste a post or thread URL to pull related activity automatically.
                This feature is planned and not implemented yet.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = st.session_state.get("uploaded_df")
    if df is None:
        st.markdown(
            """
            <div class="sw-panel">
                <div class="sw-card-label">Ready for investigation</div>
                <p class="sw-muted">
                    Upload a CSV or load the synthetic sample to start analyzing
                    potential coordinated social media activity.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    source = st.session_state.get("upload_source", "dataset")
    col1, col2 = st.columns([1, 3])
    with col1:
        metric_card("Total posts", len(df), f"Source: {source}")
    with col2:
        st.markdown("#### Dataset Preview")
        st.dataframe(df.head(15), use_container_width=True, hide_index=True)

    section_title("Column Mapping")
    st.caption("Confirm automatically detected columns before running analysis.")

    detected = detect_columns(df.columns)
    available_columns = [PLACEHOLDER] + list(df.columns)
    mapping: dict[str, str] = {}
    columns = st.columns(4)

    for position, field in enumerate(REQUIRED_FIELDS):
        default_column = detected.get(field)
        default_index = (
            available_columns.index(default_column)
            if default_column in available_columns
            else 0
        )
        with columns[position]:
            mapping[field] = st.selectbox(
                field.capitalize(),
                available_columns,
                index=default_index,
                key=f"mapping_{field}",
            )

    # Keep account list synced to mapped column
    if mapping.get("account") and mapping["account"] != PLACEHOLDER:
        st.session_state["uploaded_accounts"] = (
            df[mapping["account"]].dropna().astype(str).unique().tolist()
        )

    st.divider()

    analyze_clicked = st.button(
        "Analyze Dataset",
        type="primary",
        use_container_width=True,
    )

    if analyze_clicked:
        missing = [
            field
            for field, column in mapping.items()
            if column == PLACEHOLDER
        ]
        if missing:
            st.error("Please select columns for: " + ", ".join(missing))
            return

        posts, warnings = build_posts_from_dataframe(df, mapping)
        st.session_state["analysis_warnings"] = warnings

        if warnings:
            with st.expander(f"Validation notices ({len(warnings)})", expanded=True):
                for warning in warnings[:50]:
                    st.warning(warning)
                if len(warnings) > 50:
                    st.caption(f"…and {len(warnings) - 50} more notices.")

        if not posts:
            st.error("No valid posts found in the dataset after validation.")
            return

        with st.spinner(f"Analyzing {len(posts)} posts…"):
            outcome = analyze_posts(posts)

        if outcome.get("ok"):
            st.session_state["analysis_result"] = outcome["data"]
            st.session_state["analysis_mapping"] = mapping.copy()
            st.session_state["analyzed_df"] = df
            st.success(
                f"Analysis completed for {len(posts)} posts. "
                "Open the Results page to inspect findings."
            )
            if st.button("Go to Results", type="primary", key="goto_results_after"):
                go_to("Results")
        else:
            st.error(outcome.get("error", "Analysis failed."))
            if outcome.get("body"):
                st.code(outcome["body"])

    # Show prior validation warnings if present
    prior_warnings = st.session_state.get("analysis_warnings") or []
    if prior_warnings and not analyze_clicked:
        with st.expander(f"Last validation notices ({len(prior_warnings)})"):
            for warning in prior_warnings[:30]:
                st.write(warning)
