
from __future__ import annotations
import time


import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

from components.sidebar import go_to
from services.api import analyze_posts
from services.columns import (
    PLACEHOLDER,
    REQUIRED_FIELDS,
    build_posts_from_dataframe,
    detect_columns,
)
from services.paths import SAMPLE_POSTS_CSV


def _store_dataframe(
    df: pd.DataFrame,
    source_name: str,
    signature: str,
) -> None:
    """Store a dataset and invalidate results when it changes."""

    if st.session_state.get("file_signature") != signature:
        st.session_state["file_signature"] = signature

        for key in (
            "analysis_result",
            "analysis_mapping",
            "analysis_warnings",
            "analyzed_df",
        ):
            st.session_state.pop(key, None)

        # Reset mapping widgets for the new dataset.
        for field in REQUIRED_FIELDS:
            st.session_state.pop(f"mapping_{field}", None)

    st.session_state["uploaded_df"] = df
    st.session_state["upload_source"] = source_name

    detected = detect_columns(df.columns)
    account_column = detected.get("account")

    if account_column in df.columns:
        st.session_state["uploaded_accounts"] = (
            df[account_column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    else:
        st.session_state["uploaded_accounts"] = []


def _load_csv(content: bytes) -> pd.DataFrame:
    """Read CSV content as text without modifying identifiers."""

    from io import BytesIO

    return pd.read_csv(
        BytesIO(content),
        dtype=str,
        keep_default_na=False,
    )


def _load_uploaded_file(uploaded_file) -> None:
    """Load a user-uploaded CSV into session state."""

    content = uploaded_file.getvalue()

    signature = hashlib.sha256(content).hexdigest()

    if st.session_state.get("file_signature") == signature:
        return

    df = _load_csv(content)

    if df.empty:
        st.error("The uploaded CSV contains no rows.")
        return

    _store_dataframe(
        df,
        uploaded_file.name,
        signature,
    )


def _load_sample() -> None:
    """Load the existing synthetic sample dataset."""

    sample_path = Path(SAMPLE_POSTS_CSV)

    if not sample_path.is_file():
        st.error("Synthetic sample dataset is unavailable.")
        return

    content = sample_path.read_bytes()
    signature = hashlib.sha256(content).hexdigest()

    df = _load_csv(content)

    if df.empty:
        st.error("The synthetic sample dataset is empty.")
        return

    _store_dataframe(
        df,
        sample_path.name,
        signature,
    )


def _section_heading(title: str, subtitle: str = "") -> None:
    """Render a compact section heading."""

    st.markdown(
        f"#### {title}"
    )

    if subtitle:
        st.caption(subtitle)


def render() -> None:
    """Render the Analyze page."""

    st.markdown(
        """
        <div class="sw-analyze-heading">
            <h1>Analyze</h1>
            <p>Upload, validate and investigate a dataset.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----------------------------------------------
    # Upload area
    # ----------------------------------------------

    with st.container(border=True):
        st.markdown("**Dataset upload**")
        st.caption(
            "Upload a CSV containing social-media posts. "
            "Column names can be mapped before analysis."
        )

        upload_col, sample_col = st.columns(
            [3, 1],
            vertical_alignment="bottom",
            gap="medium",
        )

        with upload_col:
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=["csv"],
                key="csv_uploader",
                label_visibility="collapsed",
            )

        with sample_col:
            load_sample = st.button(
                "Load sample",
                width="stretch",
                key="load_sample_dataset",
            )

    if load_sample:
        try:
            _load_sample()
        except Exception as error:
            st.error(f"Could not load sample: {error}")

    if uploaded_file is not None and not load_sample:
        try:
            _load_uploaded_file(uploaded_file)
        except Exception as error:
            st.error(f"Could not read CSV: {error}")

    df = st.session_state.get("uploaded_df")

    # ----------------------------------------------
    # Empty state
    # ----------------------------------------------

    if df is None:
        with st.container(border=True):
            st.markdown("**No dataset loaded**")
            st.caption(
                "Upload a CSV or select the synthetic sample "
                "to begin an investigation."
            )

        return

    source = st.session_state.get(
        "upload_source",
        "Dataset",
    )

    # ----------------------------------------------
    # Dataset summary
    # ----------------------------------------------

    detected = detect_columns(df.columns)

    account_column = detected.get("account")

    if account_column in df.columns:
        account_count = (
    df[account_column]
    .astype(str)
    .str.strip()
    .replace("", pd.NA)
    .nunique()
)
        account_label = str(account_count)
    else:
        account_label = "—"

    m1, m2, m3 = st.columns(3, gap="small")

    with m1:
        st.metric("Posts", f"{len(df):,}")

    with m2:
        st.metric("Accounts", account_label)

    with m3:
        st.metric("Columns", len(df.columns))

    st.caption(f"Source: {source}")

    # ----------------------------------------------
    # Preview
    # ----------------------------------------------

    with st.expander("Dataset preview", expanded=True):
        st.dataframe(
            df.head(10),
            width="stretch",
            hide_index=True,
        )

        st.caption(
            f"Showing up to 10 of {len(df):,} rows."
        )

    # ----------------------------------------------
    # Column mapping
    # ----------------------------------------------

    _section_heading(
        "Column mapping",
        "Confirm the required fields before analysis.",
    )

    available_columns = [PLACEHOLDER] + list(df.columns)

    mapping: dict[str, str] = {}

    mapping_columns = st.columns(
        len(REQUIRED_FIELDS),
        gap="small",
    )

    for position, field in enumerate(REQUIRED_FIELDS):
        default_column = detected.get(field)

        default_index = (
            available_columns.index(default_column)
            if default_column in available_columns
            else 0
        )

        with mapping_columns[position]:
            mapping[field] = st.selectbox(
                field.capitalize(),
                available_columns,
                index=default_index,
                key=f"mapping_{field}",
            )

    # Update account list using confirmed mapping.
    mapped_account = mapping.get("account")

    if (
        mapped_account
        and mapped_account != PLACEHOLDER
        and mapped_account in df.columns
    ):
        st.session_state["uploaded_accounts"] = (
            df[mapped_account]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    missing = [
        field
        for field, column in mapping.items()
        if column == PLACEHOLDER
    ]

    if missing:
        st.caption(
            "Missing mappings: " + ", ".join(missing)
        )
    else:
        st.caption("All required fields mapped.")

    # ----------------------------------------------
    # Run analysis
    # ----------------------------------------------

    with st.container(border=True):
        left, right = st.columns(
            [3, 1],
            vertical_alignment="center",
        )

        with left:
            st.markdown("**Run coordination analysis**")
            st.caption(
                "Validate posts and send them to the "
                "connected detector backend."
            )

        with right:
            analyze_clicked = st.button(
                "Run analysis",
                type="primary",
                width="stretch",
                disabled=bool(missing),
                key="analyze_dataset_button",
            )

    
    if analyze_clicked:
        posts, warnings = build_posts_from_dataframe(
            df,
            mapping,
        )

        st.session_state["analysis_warnings"] = warnings

        if warnings:
            with st.expander(
                f"Validation notices ({len(warnings)})",
                expanded=True,
            ):
                for warning in warnings[:50]:
                    st.warning(warning)

                if len(warnings) > 50:
                    st.caption(
                        f"{len(warnings) - 50} additional notices."
                    )

        if not posts:
            st.error("No valid posts remain after validation.")
            return

        # Run backend analysis exactly once.
        start_time = time.perf_counter()

        with st.spinner(f"Analyzing {len(posts):,} posts..."):
            outcome = analyze_posts(posts)

        elapsed = time.perf_counter() - start_time

        st.caption(
            f"Backend request took {elapsed:.1f} seconds."
        )

        if outcome.get("ok"):
            st.session_state["analysis_result"] = outcome["data"]
            st.session_state["analysis_mapping"] = mapping.copy()
            st.session_state["analyzed_df"] = df

            st.success(
                f"Analysis completed for {len(posts):,} posts."
            )

        else:
            st.error(outcome.get("error", "Analysis failed."))

            if outcome.get("body"):
                with st.expander("Backend error details"):
                    st.code(str(outcome["body"]))

    # Show results navigation whenever a completed analysis exists.
    if st.session_state.get("analysis_result") is not None:
        if st.button(
            "View results",
            type="primary",
            key="analyze_view_results",
        ):
            go_to("Results")

    # ----------------------------------------------
    # Previous validation notices
    # ----------------------------------------------

    prior_warnings = (
        st.session_state.get("analysis_warnings") or []
    )

    if prior_warnings and not analyze_clicked:
        with st.expander(
            f"Previous validation notices ({len(prior_warnings)})"
        ):
            for warning in prior_warnings[:30]:
                st.write(warning)
